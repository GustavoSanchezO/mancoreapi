from datetime import datetime, timezone
import os

from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.dependencias import get_current_user, require_admin
from app.auth.google import oauth
from app.database.dependencias import get_db
from app.models.usuario import Usuario
from app.models.invitacion_schema import CodigoInvitacionRequest
from app.services import usuario as usuario_service

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"]
)


class UsuarioRolUpdate(BaseModel):
    rol: str


class UsuarioEstadoUpdate(BaseModel):
    activo: bool


@router.get("/")
def listar_usuarios(
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db)
):
    return usuario_service.obtener_usuarios(db)


@router.put("/{usuario_id}/rol")
def actualizar_rol_usuario(
    usuario_id: int,
    datos: UsuarioRolUpdate,
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db)
):
    usuario = usuario_service.actualizar_rol_usuario(db, usuario_id, datos.rol)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"mensaje": "Rol actualizado"}


@router.put("/{usuario_id}/estado")
def actualizar_estado_usuario(
    usuario_id: int,
    datos: UsuarioEstadoUpdate,
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db)
):
    try:
        usuario = usuario_service.actualizar_estado_usuario(
            db=db,
            usuario_id=usuario_id,
            activo=datos.activo,
            admin_id=admin.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"mensaje": "Estado actualizado"}


@router.post("/{usuario_id}/proyectos/{proyecto_id}")
def asignar_proyecto(
    usuario_id: int,
    proyecto_id: int,
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db)
):
    exito = usuario_service.asignar_proyecto_usuario(db, usuario_id, proyecto_id)
    if not exito:
        raise HTTPException(status_code=404, detail="Usuario o proyecto no encontrado")
    return {"mensaje": "Proyecto asignado al usuario"}


@router.delete("/{usuario_id}/proyectos/{proyecto_id}")
def remover_proyecto(
    usuario_id: int,
    proyecto_id: int,
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db)
):
    exito = usuario_service.remover_proyecto_usuario(db, usuario_id, proyecto_id)
    if not exito:
        raise HTTPException(status_code=404, detail="Usuario o proyecto no encontrado")
    return {"mensaje": "Proyecto removido del usuario"}


@router.get("/google/login")
async def google_login(request: Request):
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", str(request.url_for("google_callback")))
    if redirect_uri.startswith("http://") and not ("localhost" in redirect_uri or "127.0.0.1" in redirect_uri):
        redirect_uri = redirect_uri.replace("http://", "https://", 1)

    return await oauth.google.authorize_redirect(
        request,
        redirect_uri
    )


@router.get("/google/callback", name="google_callback")
async def google_callback(
    request: Request,
    db: Session = Depends(get_db)
):
    token = await oauth.google.authorize_access_token(request)
    userinfo = token["userinfo"]

    google_id = userinfo["sub"]
    email = userinfo["email"]
    nombre = userinfo.get("name", "")

    usuario = (
        db.query(Usuario)
        .filter(Usuario.google_id == google_id)
        .first()
    )

    if not usuario:
        request.session["google_pending"] = {
            "google_id": google_id,
            "email": email,
            "nombre": nombre
        }

        frontend_url = os.getenv("FRONTEND_URL", "https://administracion.mancore.mx")
        return RedirectResponse(
            url=f"{frontend_url}/login?requiere_invitacion=true",
            status_code=303
        )

    if not usuario.activo:
        return JSONResponse(
            status_code=403,
            content={
                "detail": "Este usuario está desactivado."
            }
        )

    usuario.ultimo_acceso = datetime.now(timezone.utc).replace(tzinfo=None)
    db.commit()

    request.session["user_id"] = usuario.id
    frontend_url = os.getenv("FRONTEND_URL", "https://administracion.mancore.mx")

    return RedirectResponse(
        url=f"{frontend_url}/",
        status_code=303
    )


@router.get("/me")
async def obtener_usuario_actual(
    usuario: Usuario = Depends(get_current_user)
):
    return {
        "id": usuario.id,
        "email": usuario.email,
        "nombre": usuario.nombre,
        "rol": usuario.rol,
        "es_test": usuario.es_test
    }


@router.delete("/test/{usuario_id}")
def eliminar_usuario_test(
    usuario_id: int,
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db)
):
    exito = usuario_service.purgar_usuario_test(db, usuario_id)
    if not exito:
        raise HTTPException(status_code=404, detail="El usuario de prueba no existe o ya fue purgado.")
    return {"mensaje": "Usuario de prueba y todos sus datos fueron eliminados físicamente."}


@router.post("/invitacion")
async def usar_codigo_invitacion(
    datos: CodigoInvitacionRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    pendiente = request.session.get("google_pending")
    if not pendiente:
        return JSONResponse(
            status_code=401,
            content={
                "detail": "No hay una autenticación de Google pendiente."
            }
        )

    usuario = usuario_service.procesar_codigo_invitacion(db, datos.codigo, pendiente)
    if not usuario:
        return JSONResponse(
            status_code=400,
            content={
                "detail": "El código de invitación no es válido o ya fue utilizado."
            }
        )

    request.session.pop("google_pending", None)
    request.session["user_id"] = usuario.id

    return {
        "mensaje": "Cuenta creada correctamente",
        "usuario": {
            "id": usuario.id,
            "email": usuario.email,
            "nombre": usuario.nombre,
            "rol": usuario.rol
        }
    }


@router.post("/invitacion/generar")
def generar_codigo_invitacion(
    usuario: Usuario = Depends(require_admin),
    db: Session = Depends(get_db)
):
    nueva_invitacion = usuario_service.generar_codigo_invitacion(db, usuario.id)

    return {
        "mensaje": "Código de invitación creado",
        "codigo": nueva_invitacion.codigo,
        "id": nueva_invitacion.id
    }


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return {
        "mensaje": "Sesión cerrada correctamente"
    }

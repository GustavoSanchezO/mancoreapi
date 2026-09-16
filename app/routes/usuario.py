from datetime import datetime

from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel
import secrets
import os

from app.auth.dependencias import require_admin
from app.models.codigo_invitacion import CodigoInvitacion
from sqlalchemy.orm import Session

from app.auth.google import oauth
from app.database.dependencias import get_db
from app.models.usuario import Usuario
from app.models.proyecto import Proyecto
from app.models.codigo_invitacion import CodigoInvitacion
from app.models.invitacion import CodigoInvitacionRequest
from app.auth.dependencias import get_current_user

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
    # Retornamos los usuarios. FastAPI serializará automáticamente los objetos ORM.
    # Necesitamos asegurar que no falle por ciclos, podemos devolver un dict o dejar que FastAPI y pydantic lo resuelvan si definimos un schema, pero para simplificar lo armamos:
    usuarios = db.query(Usuario).all()
    resultado = []
    for u in usuarios:
        resultado.append({
            "id": u.id,
            "email": u.email,
            "nombre": u.nombre,
            "rol": u.rol,
            "activo": u.activo,
            "fecha_creacion": u.fecha_creacion,
            "proyectos": [{"id": p.id, "nombre": p.nombre} for p in u.proyectos]
        })
    return resultado

@router.put("/{usuario_id}/rol")
def actualizar_rol_usuario(
    usuario_id: int,
    datos: UsuarioRolUpdate,
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    usuario.rol = datos.rol
    db.commit()
    return {"mensaje": "Rol actualizado"}

@router.put("/{usuario_id}/estado")
def actualizar_estado_usuario(
    usuario_id: int,
    datos: UsuarioEstadoUpdate,
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if usuario.id == admin.id:
        raise HTTPException(status_code=400, detail="No puedes desactivarte a ti mismo")
    usuario.activo = datos.activo
    db.commit()
    return {"mensaje": "Estado actualizado"}

@router.post("/{usuario_id}/proyectos/{proyecto_id}")
def asignar_proyecto(
    usuario_id: int,
    proyecto_id: int,
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not usuario or not proyecto:
        raise HTTPException(status_code=404, detail="Usuario o proyecto no encontrado")
    
    if proyecto not in usuario.proyectos:
        usuario.proyectos.append(proyecto)
        db.commit()
    return {"mensaje": "Proyecto asignado al usuario"}

@router.delete("/{usuario_id}/proyectos/{proyecto_id}")
def remover_proyecto(
    usuario_id: int,
    proyecto_id: int,
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not usuario or not proyecto:
        raise HTTPException(status_code=404, detail="Usuario o proyecto no encontrado")
    
    if proyecto in usuario.proyectos:
        usuario.proyectos.remove(proyecto)
        db.commit()
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

    usuario.ultimo_acceso = datetime.utcnow()

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
        "rol": usuario.rol
    }

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

    codigo = (
        db.query(CodigoInvitacion)
        .filter(
            CodigoInvitacion.codigo == datos.codigo,
            CodigoInvitacion.usado == False
        )
        .with_for_update()
        .first()
    )

    if not codigo:
        return JSONResponse(
            status_code=400,
            content={
                "detail": "El código de invitación no es válido o ya fue utilizado."
            }
        )

    usuario = Usuario(
        google_id=pendiente["google_id"],
        email=pendiente["email"],
        nombre=pendiente["nombre"],
        rol="EMPLEADO",
        activo=True,
        fecha_creacion=datetime.utcnow()
    )

    db.add(usuario)
    db.flush()

    codigo.usado = True
    codigo.usuario_id = usuario.id
    codigo.fecha_uso = datetime.utcnow()

    db.commit()

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
    codigo = f"MANC-{secrets.token_urlsafe(8).upper()}"

    nueva_invitacion = CodigoInvitacion(
        codigo=codigo,
        usado=False,
        creado_por=usuario.id,
        fecha_creacion=datetime.utcnow()
    )

    db.add(nueva_invitacion)
    db.commit()
    db.refresh(nueva_invitacion)

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

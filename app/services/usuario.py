from datetime import datetime, timezone
import secrets

from sqlalchemy.orm import Session
from app.models.usuario import Usuario
from app.models.proyecto import Proyecto
from app.models.codigo_invitacion import CodigoInvitacion


def obtener_usuarios(db: Session) -> list[dict]:
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


def actualizar_rol_usuario(db: Session, usuario_id: int, nuevo_rol: str) -> Usuario | None:
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        return None
    usuario.rol = nuevo_rol
    db.commit()
    return usuario


def actualizar_estado_usuario(db: Session, usuario_id: int, activo: bool, admin_id: int) -> Usuario | None:
    if usuario_id == admin_id:
        raise ValueError("No puedes desactivarte a ti mismo")
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        return None
    usuario.activo = activo
    db.commit()
    return usuario


def asignar_proyecto_usuario(db: Session, usuario_id: int, proyecto_id: int) -> bool:
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not usuario or not proyecto:
        return False

    if proyecto not in usuario.proyectos:
        usuario.proyectos.append(proyecto)
        db.commit()
    return True


def remover_proyecto_usuario(db: Session, usuario_id: int, proyecto_id: int) -> bool:
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not usuario or not proyecto:
        return False

    if proyecto in usuario.proyectos:
        usuario.proyectos.remove(proyecto)
        db.commit()
    return True


def procesar_codigo_invitacion(db: Session, codigo_str: str, pendiente: dict) -> Usuario | None:
    codigo = (
        db.query(CodigoInvitacion)
        .filter(
            CodigoInvitacion.codigo == codigo_str,
            CodigoInvitacion.usado.is_(False)
        )
        .with_for_update()
        .first()
    )

    if not codigo:
        return None

    usuario = Usuario(
        google_id=pendiente["google_id"],
        email=pendiente["email"],
        nombre=pendiente["nombre"],
        rol="EMPLEADO",
        activo=True,
        fecha_creacion=datetime.now(timezone.utc).replace(tzinfo=None)
    )

    db.add(usuario)
    db.flush()

    codigo.usado = True
    codigo.usuario_id = usuario.id
    codigo.fecha_uso = datetime.now(timezone.utc).replace(tzinfo=None)

    db.commit()
    db.refresh(usuario)
    return usuario


def generar_codigo_invitacion(db: Session, creador_id: int) -> CodigoInvitacion:
    codigo_str = f"MANC-{secrets.token_urlsafe(8).upper()}"

    nueva_invitacion = CodigoInvitacion(
        codigo=codigo_str,
        usado=False,
        creado_por=creador_id,
        fecha_creacion=datetime.now(timezone.utc).replace(tzinfo=None)
    )

    db.add(nueva_invitacion)
    db.commit()
    db.refresh(nueva_invitacion)

    return nueva_invitacion

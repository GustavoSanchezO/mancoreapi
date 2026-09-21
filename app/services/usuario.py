from datetime import datetime, timezone, timedelta
import secrets

from sqlalchemy.orm import Session
from app.models.usuario import Usuario
from app.models.proyecto import Proyecto
from app.models.codigo_invitacion import CodigoInvitacion
from app.models.cotizacion_db import CotizacionDB
from app.models.partida_cotizacion import PartidaCotizacion
from app.models.material_cotizacion import MaterialCotizacion
from app.models.mano_obra_cotizada import ManoObraCotizada
from app.models.gasto_extra_cotizado import GastoExtraCotizado
from app.models.venta import Venta
from app.models.costo_material_real import CostoMaterialReal
from app.models.costo_mano_obra_real import CostoManoObraReal
from app.models.costo_gasto_extra_real import CostoGastoExtraReal


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
            "es_test": u.es_test,
            "fecha_creacion": u.fecha_creacion,
            "ultimo_acceso": u.ultimo_acceso,
            "ultimo_cambio": u.ultimo_cambio,
            "proyectos": [{"id": p.id, "nombre": p.nombre} for p in u.proyectos]
        })
    return resultado


def actualizar_rol_usuario(db: Session, usuario_id: int, nuevo_rol: str) -> Usuario | None:
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        return None
    usuario.rol = nuevo_rol
    if usuario.es_test:
        usuario.ultimo_cambio = datetime.now(timezone.utc).replace(tzinfo=None)
    db.commit()
    return usuario


def actualizar_estado_usuario(db: Session, usuario_id: int, activo: bool, admin_id: int) -> Usuario | None:
    if usuario_id == admin_id:
        raise ValueError("No puedes desactivarte a ti mismo")
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        return None
    usuario.activo = activo
    if usuario.es_test:
        usuario.ultimo_cambio = datetime.now(timezone.utc).replace(tzinfo=None)
    db.commit()
    return usuario


def asignar_proyecto_usuario(db: Session, usuario_id: int, proyecto_id: int) -> bool:
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not usuario or not proyecto:
        return False

    if proyecto not in usuario.proyectos:
        usuario.proyectos.append(proyecto)
        if usuario.es_test:
            usuario.ultimo_cambio = datetime.now(timezone.utc).replace(tzinfo=None)
        db.commit()
    return True


def remover_proyecto_usuario(db: Session, usuario_id: int, proyecto_id: int) -> bool:
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not usuario or not proyecto:
        return False

    if proyecto in usuario.proyectos:
        usuario.proyectos.remove(proyecto)
        if usuario.es_test:
            usuario.ultimo_cambio = datetime.now(timezone.utc).replace(tzinfo=None)
        db.commit()
    return True


def procesar_codigo_invitacion(db: Session, codigo_str: str, pendiente: dict | None = None) -> Usuario | None:
    codigo_clean = codigo_str.strip().lower()
    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)

    # Registro mediante código especial de prueba
    if codigo_clean in ("testempleado", "testadmin"):
        rol_test = "ADMIN" if codigo_clean == "testadmin" else "EMPLEADO"
        
        google_id = pendiente["google_id"] if (pendiente and "google_id" in pendiente) else f"test_google_{codigo_clean}"
        email = pendiente["email"] if (pendiente and "email" in pendiente) else f"{codigo_clean}@mancore.test"
        nombre = pendiente["nombre"] if (pendiente and "nombre" in pendiente) else f"Usuario {codigo_clean.upper()}"

        # Verificar si el usuario ya existe en DB para actualizarlo como test o crearlo
        usuario_existente = db.query(Usuario).filter(
            (Usuario.google_id == google_id) | (Usuario.email == email)
        ).first()

        if usuario_existente:
            usuario_existente.rol = rol_test
            usuario_existente.es_test = True
            usuario_existente.activo = True
            usuario_existente.ultimo_cambio = now_utc
            usuario_existente.ultimo_acceso = now_utc
            db.commit()
            db.refresh(usuario_existente)
            return usuario_existente

        usuario = Usuario(
            google_id=google_id,
            email=email,
            nombre=nombre,
            rol=rol_test,
            activo=True,
            es_test=True,
            fecha_creacion=now_utc,
            ultimo_acceso=now_utc,
            ultimo_cambio=now_utc
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        return usuario

    # Registro mediante código de invitación estándar (requiere pendiente de Google)
    if not pendiente:
        return None
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
        es_test=False,
        fecha_creacion=now_utc,
        ultimo_acceso=now_utc
    )

    db.add(usuario)
    db.flush()

    codigo.usado = True
    codigo.usuario_id = usuario.id
    codigo.fecha_uso = now_utc

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


def purgar_usuario_test(db: Session, usuario_id: int) -> bool:
    """
    Realiza un borrado físico total (Hard Delete) del usuario test
    y de todos los registros creados o asociados a él.
    """
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        return False

    try:
        # 1. Obtener IDs de cotizaciones pertenecientes al usuario
        cot_ids = [c[0] for c in db.query(CotizacionDB.id).filter(CotizacionDB.usuario_id == usuario.id).all()]
        
        if cot_ids:
            # Ventas asociadas a las cotizaciones
            venta_ids = [v[0] for v in db.query(Venta.id).filter(Venta.cotizacion_id.in_(cot_ids)).all()]
            if venta_ids:
                # Costos reales asociados a las ventas
                db.query(CostoMaterialReal).filter(CostoMaterialReal.venta_id.in_(venta_ids)).delete(synchronize_session=False)
                db.query(CostoManoObraReal).filter(CostoManoObraReal.venta_id.in_(venta_ids)).delete(synchronize_session=False)
                db.query(CostoGastoExtraReal).filter(CostoGastoExtraReal.venta_id.in_(venta_ids)).delete(synchronize_session=False)
                db.query(Venta).filter(Venta.id.in_(venta_ids)).delete(synchronize_session=False)

            # Partidas asociadas a las cotizaciones
            partida_ids = [p[0] for p in db.query(PartidaCotizacion.id).filter(PartidaCotizacion.cotizacion_id.in_(cot_ids)).all()]
            if partida_ids:
                # Hijos de las partidas
                db.query(MaterialCotizacion).filter(MaterialCotizacion.partida_id.in_(partida_ids)).delete(synchronize_session=False)
                db.query(ManoObraCotizada).filter(ManoObraCotizada.partida_id.in_(partida_ids)).delete(synchronize_session=False)
                db.query(GastoExtraCotizado).filter(GastoExtraCotizado.partida_id.in_(partida_ids)).delete(synchronize_session=False)
                db.query(PartidaCotizacion).filter(PartidaCotizacion.id.in_(partida_ids)).delete(synchronize_session=False)

            # Eliminar cotizaciones
            db.query(CotizacionDB).filter(CotizacionDB.id.in_(cot_ids)).delete(synchronize_session=False)

        # 2. Códigos de invitación del usuario
        db.query(CodigoInvitacion).filter(
            (CodigoInvitacion.creado_por == usuario.id) | (CodigoInvitacion.usuario_id == usuario.id)
        ).delete(synchronize_session=False)

        # 3. Remover de la tabla intermedia usuario_proyecto
        usuario.proyectos.clear()
        db.flush()

        # 4. Eliminar finalmente el registro de Usuario
        db.delete(usuario)
        db.commit()
        return True

    except Exception:
        db.rollback()
        raise


def purgar_usuarios_test_inactivos(db: Session, minutos_inactividad: int = 3) -> int:
    """
    Revisa todos los usuarios con es_test = True y purga aquellos que tengan
    más de minutos_inactividad (por defecto 3) sin registrar cambios/actividad.
    """
    usuarios_test = db.query(Usuario).filter(Usuario.es_test.is_(True)).all()
    ahora = datetime.now(timezone.utc).replace(tzinfo=None)
    limite = ahora - timedelta(minutes=minutos_inactividad)

    purgados = 0
    for u in usuarios_test:
        ultima_actividad = u.ultimo_cambio or u.ultimo_acceso or u.fecha_creacion
        if ultima_actividad and ultima_actividad <= limite:
            purgado = purgar_usuario_test(db, u.id)
            if purgado:
                purgados += 1
    return purgados


def registrar_cambio_test(db: Session, usuario: Usuario):
    """
    Registra el timestamp de último cambio para usuarios test.
    """
    if usuario and usuario.es_test:
        usuario.ultimo_cambio = datetime.now(timezone.utc).replace(tzinfo=None)
        db.commit()

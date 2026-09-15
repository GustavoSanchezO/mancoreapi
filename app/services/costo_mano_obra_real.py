from sqlalchemy.orm import Session

from app.models.costo_mano_obra_real import CostoManoObraReal
from app.models.mano_obra_cotizada import ManoObraCotizada
from app.models.partida_cotizacion import PartidaCotizacion
from app.models.venta import Venta


def crear_costo_mano_obra_real(db: Session, datos):
    venta = (
        db.query(Venta)
        .filter(Venta.id == datos.venta_id)
        .first()
    )

    if not venta:
        return None

    mano_obra = (
        db.query(ManoObraCotizada)
        .filter(
            ManoObraCotizada.id == datos.mano_obra_cotizada_id
        )
        .first()
    )

    if not mano_obra:
        return None

    partida = (
        db.query(PartidaCotizacion)
        .filter(
            PartidaCotizacion.id == mano_obra.partida_id
        )
        .first()
    )

    if not partida:
        return None

    if partida.cotizacion_id != venta.cotizacion_id:
        raise ValueError(
            "La mano de obra cotizada no pertenece a la venta indicada."
        )

    total = datos.cantidad * datos.precio_unitario

    try:
        costo = CostoManoObraReal(
            venta_id=datos.venta_id,
            mano_obra_cotizada_id=datos.mano_obra_cotizada_id,
            descripcion=datos.descripcion,
            cantidad=datos.cantidad,
            precio_unitario=datos.precio_unitario,
            total=total,
            fecha=datos.fecha
        )

        db.add(costo)
        db.commit()
        db.refresh(costo)

        return costo

    except Exception:
        db.rollback()
        raise


def obtener_costos_mano_obra(db: Session):
    return (
        db.query(CostoManoObraReal)
        .order_by(CostoManoObraReal.id)
        .all()
    )


def obtener_costo_mano_obra(
    db: Session,
    costo_id: int
):
    return (
        db.query(CostoManoObraReal)
        .filter(CostoManoObraReal.id == costo_id)
        .first()
    )


def actualizar_costo_mano_obra(
    db: Session,
    costo_id: int,
    descripcion: str,
    cantidad,
    precio_unitario,
    fecha
):
    costo = (
        db.query(CostoManoObraReal)
        .filter(CostoManoObraReal.id == costo_id)
        .first()
    )

    if not costo:
        return None

    total = cantidad * precio_unitario

    try:
        costo.descripcion = descripcion
        costo.cantidad = cantidad
        costo.precio_unitario = precio_unitario
        costo.total = total
        costo.fecha = fecha

        db.commit()
        db.refresh(costo)

        return costo

    except Exception:
        db.rollback()
        raise
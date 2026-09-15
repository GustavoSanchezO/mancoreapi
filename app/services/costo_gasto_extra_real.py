from sqlalchemy.orm import Session

from app.models.costo_gasto_extra_real import CostoGastoExtraReal
from app.models.gasto_extra_cotizado import GastoExtraCotizado
from app.models.partida_cotizacion import PartidaCotizacion
from app.models.venta import Venta


def crear_costo_gasto_extra_real(db: Session, datos):
    venta = (
        db.query(Venta)
        .filter(Venta.id == datos.venta_id)
        .first()
    )

    if not venta:
        return None

    gasto = (
        db.query(GastoExtraCotizado)
        .filter(
            GastoExtraCotizado.id == datos.gasto_extra_cotizado_id
        )
        .first()
    )

    if not gasto:
        return None

    partida = (
        db.query(PartidaCotizacion)
        .filter(
            PartidaCotizacion.id == gasto.partida_id
        )
        .first()
    )

    if not partida:
        return None

    if partida.cotizacion_id != venta.cotizacion_id:
        raise ValueError(
            "El gasto extra cotizado no pertenece a la venta indicada."
        )

    total = datos.cantidad * datos.precio_unitario

    try:
        costo = CostoGastoExtraReal(
            venta_id=datos.venta_id,
            gasto_extra_cotizado_id=datos.gasto_extra_cotizado_id,
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


def obtener_costos_gastos_extra(db: Session):
    return (
        db.query(CostoGastoExtraReal)
        .order_by(CostoGastoExtraReal.id)
        .all()
    )


def obtener_costo_gasto_extra(
    db: Session,
    costo_id: int
):
    return (
        db.query(CostoGastoExtraReal)
        .filter(CostoGastoExtraReal.id == costo_id)
        .first()
    )


def actualizar_costo_gasto_extra(
    db: Session,
    costo_id: int,
    descripcion: str,
    cantidad,
    precio_unitario,
    fecha
):
    costo = (
        db.query(CostoGastoExtraReal)
        .filter(CostoGastoExtraReal.id == costo_id)
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
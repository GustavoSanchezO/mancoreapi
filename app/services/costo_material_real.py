from sqlalchemy.orm import Session

from app.models.costo_material_real import CostoMaterialReal
from app.models.material_cotizacion import MaterialCotizacion
from app.models.partida_cotizacion import PartidaCotizacion
from app.models.venta import Venta


def crear_costo_material_real(db: Session, datos):
    venta = (
        db.query(Venta)
        .filter(Venta.id == datos.venta_id)
        .first()
    )

    if not venta:
        return None

    material = (
        db.query(MaterialCotizacion)
        .filter(
            MaterialCotizacion.id == datos.material_cotizacion_id
        )
        .first()
    )

    if not material:
        return None

    partida = (
        db.query(PartidaCotizacion)
        .filter(
            PartidaCotizacion.id == material.partida_id
        )
        .first()
    )

    if not partida:
        return None

    if partida.cotizacion_id != venta.cotizacion_id:
        raise ValueError(
            "El material cotizado no pertenece a la venta indicada."
        )

    total = datos.cantidad * datos.precio_unitario

    try:
        costo = CostoMaterialReal(
            venta_id=datos.venta_id,
            material_cotizacion_id=datos.material_cotizacion_id,
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


def obtener_costos_materiales(db: Session):
    return (
        db.query(CostoMaterialReal)
        .order_by(CostoMaterialReal.id)
        .all()
    )


def obtener_costo_material(
    db: Session,
    costo_id: int
):
    return (
        db.query(CostoMaterialReal)
        .filter(CostoMaterialReal.id == costo_id)
        .first()
    )


def actualizar_costo_material(
    db: Session,
    costo_id: int,
    descripcion: str,
    cantidad,
    precio_unitario,
    fecha
):
    costo = (
        db.query(CostoMaterialReal)
        .filter(CostoMaterialReal.id == costo_id)
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
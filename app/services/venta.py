from sqlalchemy.orm import Session

from app.models.cotizacion_db import CotizacionDB
from app.models.venta import Venta
from calendar import monthrange
from app.models.venta_schema import (
    VentaCrear,
    VentaEstadoActualizar,
    VentaActualizar
)
from decimal import Decimal
from app.models.cliente import Cliente
from app.models.proyecto import Proyecto
from app.models.cotizacion_db import CotizacionDB
from app.models.partida_cotizacion import PartidaCotizacion
from app.models.material_cotizacion import MaterialCotizacion
from app.models.mano_obra_cotizada import ManoObraCotizada
from app.models.gasto_extra_cotizado import GastoExtraCotizado
from sqlalchemy import func

from app.models.costo_material_real import CostoMaterialReal
from app.models.costo_mano_obra_real import CostoManoObraReal
from app.models.costo_gasto_extra_real import CostoGastoExtraReal
from app.models.impuesto_mensual import ImpuestoMensual

def crear_venta(
    db: Session,
    cotizacion_id: int,
    fecha, 
    fecha_pago
):
    cotizacion = (
        db.query(CotizacionDB)
        .filter(
            CotizacionDB.id == cotizacion_id
        )
        .first()
    )

    if not cotizacion:
        return None

    # La cotización debe estar aceptada
    if cotizacion.estado != "ACEPTADA":
        raise ValueError(
            "Solo se puede crear una venta "
            "a partir de una cotización aceptada."
        )

    # Una cotización solo puede tener una venta
    venta_existente = (
        db.query(Venta)
        .filter(
            Venta.cotizacion_id == cotizacion_id
        )
        .first()
    )

    if venta_existente:
        raise ValueError(
            "Esta cotización ya tiene una venta."
        )

    try:
        venta = Venta(
            cotizacion_id=cotizacion.id,
            fecha=fecha,
            fecha_pago=fecha_pago,
            subtotal=cotizacion.subtotal,
            iva=cotizacion.iva,
            total=cotizacion.total,
            estado="PENDIENTE"
        )

        db.add(venta)

        db.commit()
        db.refresh(venta)

        return venta

    except Exception:
        db.rollback()
        raise

def obtener_ventas(db: Session, usuario=None):
    query = db.query(Venta)
    if usuario and usuario.rol == "EMPLEADO":
        from app.models.usuario_proyecto import usuario_proyecto
        from app.models.cotizacion_db import CotizacionDB
        query = query.join(CotizacionDB, Venta.cotizacion_id == CotizacionDB.id).join(
            usuario_proyecto, 
            CotizacionDB.proyecto_id == usuario_proyecto.c.proyecto_id
        ).filter(
            usuario_proyecto.c.usuario_id == usuario.id
        )
    return query.order_by(Venta.fecha_creacion.desc()).all()

def obtener_venta(
    db: Session,
    venta_id: int,
    usuario=None
):
    query = db.query(Venta).filter(Venta.id == venta_id)
    if usuario and usuario.rol == "EMPLEADO":
        from app.models.usuario_proyecto import usuario_proyecto
        from app.models.cotizacion_db import CotizacionDB
        query = query.join(CotizacionDB, Venta.cotizacion_id == CotizacionDB.id).join(
            usuario_proyecto, 
            CotizacionDB.proyecto_id == usuario_proyecto.c.proyecto_id
        ).filter(
            usuario_proyecto.c.usuario_id == usuario.id
        )
    return query.first()

def obtener_venta_detalle(
    db: Session,
    venta_id: int,
    usuario=None
):
    query = db.query(Venta).filter(Venta.id == venta_id)
    if usuario and usuario.rol == "EMPLEADO":
        from app.models.usuario_proyecto import usuario_proyecto
        from app.models.cotizacion_db import CotizacionDB
        query = query.join(CotizacionDB, Venta.cotizacion_id == CotizacionDB.id).join(
            usuario_proyecto, 
            CotizacionDB.proyecto_id == usuario_proyecto.c.proyecto_id
        ).filter(
            usuario_proyecto.c.usuario_id == usuario.id
        )
    venta = query.first()

    if not venta:
        return None

    # =========================
    # COTIZACIÓN
    # =========================

    cotizacion = (
        db.query(CotizacionDB)
        .filter(
            CotizacionDB.id == venta.cotizacion_id
        )
        .first()
    )

    if not cotizacion:
        return None

    # =========================
    # CLIENTE
    # =========================

    cliente = (
        db.query(Cliente)
        .filter(
            Cliente.id == cotizacion.cliente_id
        )
        .first()
    )

    # =========================
    # PROYECTO
    # =========================

    proyecto = (
        db.query(Proyecto)
        .filter(
            Proyecto.id == cotizacion.proyecto_id
        )
        .first()
    )

    # =========================
    # PARTIDAS
    # =========================

    partidas = (
        db.query(PartidaCotizacion)
        .filter(
            PartidaCotizacion.cotizacion_id
            == cotizacion.id
        )
        .all()
    )

    partidas_resultado = []

    for partida in partidas:

        materiales = (
            db.query(MaterialCotizacion)
            .filter(
                MaterialCotizacion.partida_id
                == partida.id
            )
            .all()
        )

        mano_obra = (
            db.query(ManoObraCotizada)
            .filter(
                ManoObraCotizada.partida_id
                == partida.id
            )
            .all()
        )

        gastos_extra = (
            db.query(GastoExtraCotizado)
            .filter(
                GastoExtraCotizado.partida_id
                == partida.id
            )
            .all()
        )

        partidas_resultado.append({
            "id": partida.id,
            "descripcion": partida.descripcion,
            "cantidad": partida.cantidad,
            "precio_unitario": partida.precio_unitario,
            "total": partida.total,
            "materiales": materiales,
            "mano_obra": mano_obra,
            "gastos_extra": gastos_extra
        })

    return {
        "id": venta.id,
        "cotizacion_id": venta.cotizacion_id,
        "fecha": venta.fecha,
        "fecha_pago": venta.fecha_pago,
        "subtotal": venta.subtotal,
        "iva": venta.iva,
        "total": venta.total,
        "estado": venta.estado,
        "fecha_creacion": venta.fecha_creacion,

        "cliente": cliente,
        "proyecto": proyecto,

        "cotizacion": {
            "id": cotizacion.id,
            "rfq": cotizacion.rfq,
            "fecha": cotizacion.fecha,
            "tiempo_entrega_estimado": (
                cotizacion.tiempo_entrega_estimado
            ),
            "estado": cotizacion.estado,
            "subtotal": cotizacion.subtotal,
            "iva": cotizacion.iva,
            "total": cotizacion.total,
            "partidas": partidas_resultado
        }
    }

TRANSICIONES_VENTA = {
    "PENDIENTE": {
        "PAGADA",
        "CANCELADA"
    },
    "PAGADA": {
        "CANCELADA"
    },
    "CANCELADA": set()
}


def actualizar_estado_venta(
    db: Session,
    venta_id: int,
    nuevo_estado: str
):
    venta = (
        db.query(Venta)
        .filter(Venta.id == venta_id)
        .first()
    )

    if not venta:
        return None

    estado_actual = venta.estado

    estados_permitidos = TRANSICIONES_VENTA.get(
        estado_actual,
        set()
    )

    if nuevo_estado not in estados_permitidos:
        raise ValueError(
            f"No se puede cambiar una venta de "
            f"{estado_actual} a {nuevo_estado}."
        )

    try:
        venta.estado = nuevo_estado

        db.commit()
        db.refresh(venta)

        return venta

    except Exception:
        db.rollback()
        raise

def obtener_rentabilidad_venta(
    db: Session,
    venta_id: int
):
    venta = (
        db.query(Venta)
        .filter(Venta.id == venta_id)
        .first()
    )

    if not venta:
        return None

    # -----------------------------------------
    # COSTOS REALES DE MATERIALES
    # -----------------------------------------

    costo_materiales = (
        db.query(
            func.coalesce(
                func.sum(CostoMaterialReal.total),
                0
            )
        )
        .filter(
            CostoMaterialReal.venta_id == venta.id
        )
        .scalar()
    )

    # -----------------------------------------
    # COSTOS REALES DE MANO DE OBRA
    # -----------------------------------------

    costo_mano_obra = (
        db.query(
            func.coalesce(
                func.sum(CostoManoObraReal.total),
                0
            )
        )
        .filter(
            CostoManoObraReal.venta_id == venta.id
        )
        .scalar()
    )

    # -----------------------------------------
    # COSTOS REALES DE GASTOS EXTRA
    # -----------------------------------------

    costo_gastos_extra = (
        db.query(
            func.coalesce(
                func.sum(CostoGastoExtraReal.total),
                0
            )
        )
        .filter(
            CostoGastoExtraReal.venta_id == venta.id
        )
        .scalar()
    )

        # -----------------------------------------
    # IMPUESTO DEL MES
    # -----------------------------------------

    impuesto_mensual = (
        db.query(ImpuestoMensual)
        .filter(
            ImpuestoMensual.año == venta.fecha.year,
            ImpuestoMensual.mes == venta.fecha.month
        )
        .first()
    )

    impuesto_por_venta = Decimal("0.00")

    if impuesto_mensual:

        primer_dia_mes = venta.fecha.replace(day=1)

        if venta.fecha.month == 12:
            primer_dia_siguiente = venta.fecha.replace(
                year=venta.fecha.year + 1,
                month=1,
                day=1
            )
        else:
            primer_dia_siguiente = venta.fecha.replace(
                month=venta.fecha.month + 1,
                day=1
            )

        cantidad_ventas = (
            db.query(func.count(Venta.id))
            .filter(
                Venta.fecha >= primer_dia_mes,
                Venta.fecha < primer_dia_siguiente,
                Venta.estado != "CANCELADA"
            )
            .scalar()
        )

        if cantidad_ventas > 0:
            impuesto_por_venta = (
                impuesto_mensual.total_impuestos
                / Decimal(cantidad_ventas)
            )

            # -----------------------------------------
    # COSTO TOTAL
    # -----------------------------------------

    costo_total = (
        costo_materiales
        + costo_mano_obra
        + costo_gastos_extra
        + impuesto_por_venta
    )

    # -----------------------------------------
    # UTILIDAD
    # -----------------------------------------

    utilidad = venta.subtotal - costo_total

    # -----------------------------------------
    # MARGEN
    # -----------------------------------------

    if venta.subtotal > 0:
        margen_porcentaje = (
            utilidad / venta.subtotal
        ) * Decimal("100")
    else:
        margen_porcentaje = Decimal("0.00")

    return {
        "venta_id": venta.id,
        "fecha": venta.fecha,
        "estado": venta.estado,
        "ingreso": venta.subtotal,

        "costos": {
            "materiales": costo_materiales,
            "mano_obra": costo_mano_obra,
            "gastos_extra": costo_gastos_extra,
            "impuesto": impuesto_por_venta,
            "costo_total": costo_total
        },

        "utilidad": utilidad,
        "margen_porcentaje": margen_porcentaje
    }

def actualizar_venta(db: Session, venta_id: int, venta_actualizar: VentaActualizar):
    venta = obtener_venta(db, venta_id)
    if not venta:
        raise ValueError(f"Venta con id {venta_id} no encontrada.")
    if venta_actualizar.fecha is not None:
        venta.fecha = venta_actualizar.fecha
    if venta_actualizar.fecha_pago is not None:
        venta.fecha_pago = venta_actualizar.fecha_pago
    db.commit()
    db.refresh(venta)
    return venta

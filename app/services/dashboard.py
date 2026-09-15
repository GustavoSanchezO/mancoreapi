from calendar import monthrange
from datetime import date
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.cotizacion_db import CotizacionDB
from app.models.costo_gasto_extra_real import CostoGastoExtraReal
from app.models.costo_mano_obra_real import CostoManoObraReal
from app.models.costo_material_real import CostoMaterialReal
from app.models.impuesto_mensual import ImpuestoMensual
from app.models.venta import Venta


def obtener_resumen_dashboard(
    db: Session,
    año: int,
    mes: int
):
    primer_dia = date(año, mes, 1)

    if mes == 12:
        primer_dia_siguiente = date(año + 1, 1, 1)
    else:
        primer_dia_siguiente = date(año, mes + 1, 1)

    # -----------------------------------------
    # VENTAS DEL MES
    # -----------------------------------------

    ventas = (
        db.query(Venta)
        .filter(
            Venta.fecha >= primer_dia,
            Venta.fecha < primer_dia_siguiente
        )
        .all()
    )

    ventas_no_canceladas = [
        venta
        for venta in ventas
        if venta.estado != "CANCELADA"
    ]

    ventas_mes = len(ventas_no_canceladas)

    ingresos_mes = sum(
        (venta.subtotal for venta in ventas_no_canceladas),
        Decimal("0.00")
    )

    ventas_pendientes = sum(
        (
            venta.total
            for venta in ventas_no_canceladas
            if venta.estado == "PENDIENTE"
        ),
        Decimal("0.00")
    )

    # -----------------------------------------
    # COSTOS REALES
    # -----------------------------------------

    costos_materiales = (
        db.query(
            func.coalesce(
                func.sum(CostoMaterialReal.total),
                0
            )
        )
        .filter(
            CostoMaterialReal.fecha >= primer_dia,
            CostoMaterialReal.fecha < primer_dia_siguiente
        )
        .scalar()
    )

    costos_mano_obra = (
        db.query(
            func.coalesce(
                func.sum(CostoManoObraReal.total),
                0
            )
        )
        .filter(
            CostoManoObraReal.fecha >= primer_dia,
            CostoManoObraReal.fecha < primer_dia_siguiente
        )
        .scalar()
    )

    costos_gastos_extra = (
        db.query(
            func.coalesce(
                func.sum(CostoGastoExtraReal.total),
                0
            )
        )
        .filter(
            CostoGastoExtraReal.fecha >= primer_dia,
            CostoGastoExtraReal.fecha < primer_dia_siguiente
        )
        .scalar()
    )

    # -----------------------------------------
    # IMPUESTOS
    # -----------------------------------------

    impuesto = (
        db.query(ImpuestoMensual)
        .filter(
            ImpuestoMensual.año == año,
            ImpuestoMensual.mes == mes
        )
        .first()
    )

    impuestos_mes = (
        impuesto.total_impuestos
        if impuesto
        else Decimal("0.00")
    )

    # -----------------------------------------
    # UTILIDAD
    # -----------------------------------------

    impuesto_por_venta = Decimal("0.00")

    if ventas_mes > 0:
        impuesto_por_venta = (
            impuestos_mes /
            Decimal(ventas_mes)
        )

    impuesto_distribuido = (
        impuesto_por_venta *
        Decimal(ventas_mes)
    )

    costo_total = (
        costos_materiales
        + costos_mano_obra
        + costos_gastos_extra
        + impuesto_distribuido
    )

    utilidad_mes = ingresos_mes - costo_total

    # -----------------------------------------
    # COTIZACIONES
    # -----------------------------------------

    cotizaciones_enviadas = (
        db.query(func.count(CotizacionDB.id))
        .filter(
            CotizacionDB.fecha >= primer_dia,
            CotizacionDB.fecha < primer_dia_siguiente,
            CotizacionDB.estado == "ENVIADA"
        )
        .scalar()
    )

    cotizaciones_aceptadas = (
        db.query(func.count(CotizacionDB.id))
        .filter(
            CotizacionDB.fecha >= primer_dia,
            CotizacionDB.fecha < primer_dia_siguiente,
            CotizacionDB.estado == "ACEPTADA"
        )
        .scalar()
    )

    return {
        "ventas_mes": ventas_mes,
        "ingresos_mes": ingresos_mes,
        "ventas_pendientes": ventas_pendientes,
        "utilidad_mes": utilidad_mes,

        "cotizaciones_enviadas": cotizaciones_enviadas,
        "cotizaciones_aceptadas": cotizaciones_aceptadas,

        "costos_materiales_mes": costos_materiales,
        "costos_mano_obra_mes": costos_mano_obra,
        "costos_gastos_extra_mes": costos_gastos_extra,
        "impuestos_mes": impuestos_mes
    }
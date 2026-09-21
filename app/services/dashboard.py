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


from app.models.usuario import Usuario
from app.services.seguridad_db import aplicar_filtro_test

def obtener_resumen_dashboard(
    db: Session,
    año: int,
    mes: int,
    usuario: Usuario
):
    primer_dia = date(año, mes, 1)

    if mes == 12:
        primer_dia_siguiente = date(año + 1, 1, 1)
    else:
        primer_dia_siguiente = date(año, mes + 1, 1)

    # -----------------------------------------
    # VENTAS DEL MES
    # -----------------------------------------

    query_ventas = db.query(Venta).filter(
        Venta.fecha >= primer_dia,
        Venta.fecha < primer_dia_siguiente
    )
    query_ventas = aplicar_filtro_test(query_ventas, Venta, usuario)
    ventas = query_ventas.all()

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

    query_materiales = db.query(func.coalesce(func.sum(CostoMaterialReal.total), 0)).join(
        Venta, CostoMaterialReal.venta_id == Venta.id
    ).filter(
        CostoMaterialReal.fecha >= primer_dia,
        CostoMaterialReal.fecha < primer_dia_siguiente
    )
    query_materiales = aplicar_filtro_test(query_materiales, Venta, usuario)
    costos_materiales = query_materiales.scalar()

    query_mano_obra = db.query(func.coalesce(func.sum(CostoManoObraReal.total), 0)).join(
        Venta, CostoManoObraReal.venta_id == Venta.id
    ).filter(
        CostoManoObraReal.fecha >= primer_dia,
        CostoManoObraReal.fecha < primer_dia_siguiente
    )
    query_mano_obra = aplicar_filtro_test(query_mano_obra, Venta, usuario)
    costos_mano_obra = query_mano_obra.scalar()

    query_gastos_extra = db.query(func.coalesce(func.sum(CostoGastoExtraReal.total), 0)).join(
        Venta, CostoGastoExtraReal.venta_id == Venta.id
    ).filter(
        CostoGastoExtraReal.fecha >= primer_dia,
        CostoGastoExtraReal.fecha < primer_dia_siguiente
    )
    query_gastos_extra = aplicar_filtro_test(query_gastos_extra, Venta, usuario)
    costos_gastos_extra = query_gastos_extra.scalar()

    # -----------------------------------------
    # IMPUESTOS
    # -----------------------------------------

    query_impuesto = db.query(ImpuestoMensual).filter(
        ImpuestoMensual.año == año,
        ImpuestoMensual.mes == mes
    )
    query_impuesto = aplicar_filtro_test(query_impuesto, ImpuestoMensual, usuario)
    impuesto = query_impuesto.first()

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

    query_enviadas = db.query(func.count(CotizacionDB.id)).filter(
        CotizacionDB.fecha >= primer_dia,
        CotizacionDB.fecha < primer_dia_siguiente,
        CotizacionDB.estado == "ENVIADA"
    )
    query_enviadas = aplicar_filtro_test(query_enviadas, CotizacionDB, usuario)
    cotizaciones_enviadas = query_enviadas.scalar()

    query_aceptadas = db.query(func.count(CotizacionDB.id)).filter(
        CotizacionDB.fecha >= primer_dia,
        CotizacionDB.fecha < primer_dia_siguiente,
        CotizacionDB.estado == "ACEPTADA"
    )
    query_aceptadas = aplicar_filtro_test(query_aceptadas, CotizacionDB, usuario)
    cotizaciones_aceptadas = query_aceptadas.scalar()

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
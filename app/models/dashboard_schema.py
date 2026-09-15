from decimal import Decimal

from pydantic import BaseModel


class DashboardResumenRespuesta(BaseModel):
    ventas_mes: int
    ingresos_mes: Decimal
    ventas_pendientes: Decimal
    utilidad_mes: Decimal

    cotizaciones_enviadas: int
    cotizaciones_aceptadas: int

    costos_materiales_mes: Decimal
    costos_mano_obra_mes: Decimal
    costos_gastos_extra_mes: Decimal
    impuestos_mes: Decimal
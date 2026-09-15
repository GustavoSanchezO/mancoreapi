from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.dependencias import require_admin
from app.database.dependencias import get_db
from app.models.usuario import Usuario
from app.models.dashboard_schema import DashboardResumenRespuesta
from app.services.dashboard import obtener_resumen_dashboard


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get(
    "/resumen",
    response_model=DashboardResumenRespuesta
)
def obtener_dashboard(
    año: int | None = Query(default=None, ge=2000),
    mes: int | None = Query(default=None, ge=1, le=12),
    usuario: Usuario = Depends(require_admin),
    db: Session = Depends(get_db)
):
    hoy = date.today()

    if año is None:
        año = hoy.year

    if mes is None:
        mes = hoy.month

    return obtener_resumen_dashboard(
        db=db,
        año=año,
        mes=mes
    )
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencias import require_admin
from app.database.dependencias import get_db
from app.models.usuario import Usuario

from app.models.impuesto_mensual_schema import (
    ImpuestoMensualCrear,
    ImpuestoMensualActualizar,
    ImpuestoMensualRespuesta
)

from app.services.impuesto_mensual import (
    crear_impuesto_mensual,
    obtener_impuestos_mensuales,
    obtener_impuesto_mensual,
    actualizar_impuesto_mensual
)


router = APIRouter(
    prefix="/impuestos-mensuales",
    tags=["Impuestos mensuales"]
)


@router.post(
    "",
    response_model=ImpuestoMensualRespuesta
)
def crear_impuesto_mensual_endpoint(
    datos: ImpuestoMensualCrear,
    usuario: Usuario = Depends(require_admin),
    db: Session = Depends(get_db)
):
    try:
        impuesto = crear_impuesto_mensual(
            db=db,
            año=datos.año,
            mes=datos.mes,
            total_impuestos=datos.total_impuestos
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    return impuesto


@router.get(
    "",
    response_model=list[ImpuestoMensualRespuesta]
)
def listar_impuestos_mensuales_endpoint(
    usuario: Usuario = Depends(require_admin),
    db: Session = Depends(get_db)
):
    return obtener_impuestos_mensuales(db)


@router.get(
    "/{impuesto_id}",
    response_model=ImpuestoMensualRespuesta
)
def obtener_impuesto_mensual_endpoint(
    impuesto_id: int,
    usuario: Usuario = Depends(require_admin),
    db: Session = Depends(get_db)
):
    impuesto = obtener_impuesto_mensual(
        db=db,
        impuesto_id=impuesto_id
    )

    if not impuesto:
        raise HTTPException(
            status_code=404,
            detail="El impuesto mensual no existe."
        )

    return impuesto


@router.put(
    "/{impuesto_id}",
    response_model=ImpuestoMensualRespuesta
)
def actualizar_impuesto_mensual_endpoint(
    impuesto_id: int,
    datos: ImpuestoMensualActualizar,
    usuario: Usuario = Depends(require_admin),
    db: Session = Depends(get_db)
):
    impuesto = actualizar_impuesto_mensual(
        db=db,
        impuesto_id=impuesto_id,
        total_impuestos=datos.total_impuestos
    )

    if not impuesto:
        raise HTTPException(
            status_code=404,
            detail="El impuesto mensual no existe."
        )

    return impuesto
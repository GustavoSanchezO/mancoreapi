from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencias import get_current_user
from app.database.dependencias import get_db
from app.models.usuario import Usuario

from app.models.costo_gasto_extra_real_schema import (
    CostoGastoExtraRealCrear,
    CostoGastoExtraRealActualizar,
    CostoGastoExtraRealRespuesta
)

from app.services.costo_gasto_extra_real import (
    crear_costo_gasto_extra_real,
    obtener_costos_gastos_extra,
    obtener_costo_gasto_extra,
    actualizar_costo_gasto_extra
)


router = APIRouter(
    prefix="/costos/gastos-extra",
    tags=["Costos reales - Gastos extra"]
)


@router.post(
    "",
    response_model=CostoGastoExtraRealRespuesta
)
def crear_costo_gasto_extra_real_endpoint(
    datos: CostoGastoExtraRealCrear,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        costo = crear_costo_gasto_extra_real(
            db=db,
            datos=datos
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    if not costo:
        raise HTTPException(
            status_code=404,
            detail="La venta o el gasto extra cotizado no existe."
        )

    return costo


@router.get(
    "",
    response_model=list[CostoGastoExtraRealRespuesta]
)
def listar_costos_gastos_extra_endpoint(
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return obtener_costos_gastos_extra(db)


@router.get(
    "/{costo_id}",
    response_model=CostoGastoExtraRealRespuesta
)
def obtener_costo_gasto_extra_endpoint(
    costo_id: int,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    costo = obtener_costo_gasto_extra(
        db=db,
        costo_id=costo_id
    )

    if not costo:
        raise HTTPException(
            status_code=404,
            detail="El costo real del gasto extra no existe."
        )

    return costo


@router.put(
    "/{costo_id}",
    response_model=CostoGastoExtraRealRespuesta
)
def actualizar_costo_gasto_extra_endpoint(
    costo_id: int,
    datos: CostoGastoExtraRealActualizar,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    costo = actualizar_costo_gasto_extra(
        db=db,
        costo_id=costo_id,
        descripcion=datos.descripcion,
        cantidad=datos.cantidad,
        precio_unitario=datos.precio_unitario,
        fecha=datos.fecha
    )

    if not costo:
        raise HTTPException(
            status_code=404,
            detail="El costo real del gasto extra no existe."
        )

    return costo
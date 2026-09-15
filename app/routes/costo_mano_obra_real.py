from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencias import get_current_user
from app.database.dependencias import get_db
from app.models.usuario import Usuario

from app.models.costo_mano_obra_real_schema import (
    CostoManoObraRealCrear,
    CostoManoObraRealActualizar,
    CostoManoObraRealRespuesta
)

from app.services.costo_mano_obra_real import (
    crear_costo_mano_obra_real,
    obtener_costos_mano_obra,
    obtener_costo_mano_obra,
    actualizar_costo_mano_obra
)


router = APIRouter(
    prefix="/costos/mano-obra",
    tags=["Costos reales - Mano de obra"]
)


@router.post(
    "",
    response_model=CostoManoObraRealRespuesta
)
def crear_costo_mano_obra_real_endpoint(
    datos: CostoManoObraRealCrear,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        costo = crear_costo_mano_obra_real(
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
            detail="La venta o la mano de obra cotizada no existe."
        )

    return costo


@router.get(
    "",
    response_model=list[CostoManoObraRealRespuesta]
)
def listar_costos_mano_obra_endpoint(
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return obtener_costos_mano_obra(db)


@router.get(
    "/{costo_id}",
    response_model=CostoManoObraRealRespuesta
)
def obtener_costo_mano_obra_endpoint(
    costo_id: int,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    costo = obtener_costo_mano_obra(
        db=db,
        costo_id=costo_id
    )

    if not costo:
        raise HTTPException(
            status_code=404,
            detail="El costo real de mano de obra no existe."
        )

    return costo


@router.put(
    "/{costo_id}",
    response_model=CostoManoObraRealRespuesta
)
def actualizar_costo_mano_obra_endpoint(
    costo_id: int,
    datos: CostoManoObraRealActualizar,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    costo = actualizar_costo_mano_obra(
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
            detail="El costo real de mano de obra no existe."
        )

    return costo
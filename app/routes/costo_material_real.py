from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencias import get_current_user
from app.database.dependencias import get_db
from app.models.usuario import Usuario
from app.models.costo_material_real_schema import (
    CostoMaterialRealCrear,
    CostoMaterialRealRespuesta
)
from app.services.costo_material_real import crear_costo_material_real

from app.models.costo_material_real_schema import (
    CostoMaterialRealCrear,
    CostoMaterialRealActualizar,
    CostoMaterialRealRespuesta
)

from app.services.costo_material_real import (
    crear_costo_material_real,
    obtener_costos_materiales,
    obtener_costo_material,
    actualizar_costo_material
)

router = APIRouter(
    prefix="/costos/materiales",
    tags=["Costos reales - Materiales"]
)


@router.post(
    "",
    response_model=CostoMaterialRealRespuesta
)
def crear_costo_material_real_endpoint(
    datos: CostoMaterialRealCrear,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        costo = crear_costo_material_real(
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
            detail="La venta o el material cotizado no existe."
        )

    return costo


@router.get(
    "",
    response_model=list[CostoMaterialRealRespuesta]
)
def listar_costos_materiales_endpoint(
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return obtener_costos_materiales(db)


@router.get(
    "/{costo_id}",
    response_model=CostoMaterialRealRespuesta
)
def obtener_costo_material_endpoint(
    costo_id: int,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    costo = obtener_costo_material(
        db=db,
        costo_id=costo_id
    )

    if not costo:
        raise HTTPException(
            status_code=404,
            detail="El costo real de material no existe."
        )

    return costo

@router.put(
    "/{costo_id}",
    response_model=CostoMaterialRealRespuesta
)
def actualizar_costo_material_endpoint(
    costo_id: int,
    datos: CostoMaterialRealActualizar,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    costo = actualizar_costo_material(
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
            detail="El costo real de material no existe."
        )

    return costo
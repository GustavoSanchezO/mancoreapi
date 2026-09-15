from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencias import get_current_user
from app.database.dependencias import get_db
from app.models.usuario import Usuario
from app.models.material_schema import (
    MaterialCrear,
    MaterialActualizar,
    MaterialRespuesta
)
from app.services.material import (
    crear_material,
    obtener_materiales,
    obtener_material,
    actualizar_material,
    desactivar_material
)


router = APIRouter(
    prefix="/materiales",
    tags=["Materiales"]
)


@router.post(
    "",
    response_model=MaterialRespuesta
)
def crear_material_endpoint(
    datos: MaterialCrear,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        material = crear_material(
            db=db,
            nombre=datos.nombre,
            unidad=datos.unidad,
            codigo=datos.codigo
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    return material


@router.get(
    "",
    response_model=list[MaterialRespuesta]
)
def listar_materiales_endpoint(
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return obtener_materiales(db)


@router.get(
    "/{material_id}",
    response_model=MaterialRespuesta
)
def obtener_material_endpoint(
    material_id: int,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    material = obtener_material(
        db=db,
        material_id=material_id
    )

    if not material:
        raise HTTPException(
            status_code=404,
            detail="El material no existe."
        )

    return material


@router.put(
    "/{material_id}",
    response_model=MaterialRespuesta
)
def actualizar_material_endpoint(
    material_id: int,
    datos: MaterialActualizar,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        material = actualizar_material(
            db=db,
            material_id=material_id,
            nombre=datos.nombre,
            unidad=datos.unidad,
            codigo=datos.codigo
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    if not material:
        raise HTTPException(
            status_code=404,
            detail="El material no existe."
        )

    return material


@router.delete(
    "/{material_id}",
    response_model=MaterialRespuesta
)
def eliminar_material_endpoint(
    material_id: int,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    material = desactivar_material(
        db=db,
        material_id=material_id
    )

    if not material:
        raise HTTPException(
            status_code=404,
            detail="El material no existe."
        )

    return material
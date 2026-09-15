from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencias import get_current_user
from app.database.conexion import get_db
from app.models.usuario import Usuario
from app.models.cliente_schema import (
    ClienteCrear,
    ClienteActualizar,
    ClienteRespuesta
)
from app.services import cliente as cliente_service


router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"]
)


@router.post(
    "",
    response_model=ClienteRespuesta
)
def crear_cliente(
    datos: ClienteCrear,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    return cliente_service.crear_cliente(
        db,
        datos
    )


@router.get(
    "",
    response_model=list[ClienteRespuesta]
)
def listar_clientes(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    return cliente_service.obtener_clientes(db)


@router.get(
    "/{cliente_id}",
    response_model=ClienteRespuesta
)
def obtener_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    cliente = cliente_service.obtener_cliente(
        db,
        cliente_id
    )

    if not cliente:
        raise HTTPException(
            status_code=404,
            detail="Cliente no encontrado."
        )

    return cliente


@router.put(
    "/{cliente_id}",
    response_model=ClienteRespuesta
)
def actualizar_cliente(
    cliente_id: int,
    datos: ClienteActualizar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    cliente = cliente_service.obtener_cliente(
        db,
        cliente_id
    )

    if not cliente:
        raise HTTPException(
            status_code=404,
            detail="Cliente no encontrado."
        )

    return cliente_service.actualizar_cliente(
        db,
        cliente,
        datos
    )


@router.delete(
    "/{cliente_id}",
    response_model=ClienteRespuesta
)
def eliminar_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    cliente = cliente_service.obtener_cliente(
        db,
        cliente_id
    )

    if not cliente:
        raise HTTPException(
            status_code=404,
            detail="Cliente no encontrado."
        )

    return cliente_service.eliminar_cliente(
        db,
        cliente
    )
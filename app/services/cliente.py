from sqlalchemy.orm import Session

from app.models.cliente import Cliente
from app.models.cliente_schema import (
    ClienteCrear,
    ClienteActualizar
)


def crear_cliente(
    db: Session,
    datos: ClienteCrear
):
    cliente = Cliente(
        nombre_empresa=datos.nombre_empresa,
        direccion=datos.direccion
    )

    db.add(cliente)
    db.commit()
    db.refresh(cliente)

    return cliente


def obtener_clientes(db: Session):
    return db.query(Cliente).filter(
        Cliente.activo == True
    ).all()


def obtener_cliente(
    db: Session,
    cliente_id: int
):
    return db.query(Cliente).filter(
        Cliente.id == cliente_id,
        Cliente.activo == True
    ).first()


def actualizar_cliente(
    db: Session,
    cliente: Cliente,
    datos: ClienteActualizar
):
    cambios = datos.model_dump(
        exclude_unset=True
    )

    for campo, valor in cambios.items():
        setattr(cliente, campo, valor)

    db.commit()
    db.refresh(cliente)

    return cliente


def eliminar_cliente(
    db: Session,
    cliente: Cliente
):
    cliente.activo = False

    db.commit()
    db.refresh(cliente)

    return cliente
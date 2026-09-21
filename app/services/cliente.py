from sqlalchemy.orm import Session
from app.models.usuario import Usuario

from app.models.cliente import Cliente
from app.models.cliente_schema import (
    ClienteCrear,
    ClienteActualizar
)
from app.services.seguridad_db import aplicar_filtro_test


def crear_cliente(
    db: Session,
    datos: ClienteCrear,
    usuario: Usuario
):
    cliente = Cliente(
        nombre_empresa=datos.nombre_empresa,
        direccion=datos.direccion,
        usuario_id=usuario.id,
        es_test=usuario.es_test
    )

    db.add(cliente)
    db.commit()
    db.refresh(cliente)

    return cliente


def obtener_clientes(db: Session, usuario: Usuario):
    query = db.query(Cliente).filter(
        Cliente.activo == True
    )
    query = aplicar_filtro_test(query, Cliente, usuario)
    return query.all()


def obtener_cliente(
    db: Session,
    cliente_id: int,
    usuario: Usuario
):
    query = db.query(Cliente).filter(
        Cliente.id == cliente_id,
        Cliente.activo == True
    )
    query = aplicar_filtro_test(query, Cliente, usuario)
    return query.first()


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
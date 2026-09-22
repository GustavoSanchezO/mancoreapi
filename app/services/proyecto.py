from sqlalchemy.orm import Session
from app.models.usuario import Usuario

from app.models.proyecto import Proyecto
from app.models.cliente import Cliente
from app.models.proyecto_schema import (
    ProyectoCrear,
    ProyectoActualizar
)
from app.services.seguridad_db import aplicar_filtro_test


def crear_proyecto(
    db: Session,
    datos: ProyectoCrear,
    usuario: Usuario
):
    cliente = (
        db.query(Cliente)
        .filter(
            Cliente.id == datos.cliente_id,
            Cliente.activo == True
        )
        .first()
    )

    if not cliente:
        return None

    proyecto = Proyecto(
        nombre=datos.nombre,
        descripcion=datos.descripcion,
        cliente_id=datos.cliente_id,
        usuario_id=usuario.id,
        es_test=usuario.es_test
    )

    db.add(proyecto)
    db.commit()
    db.refresh(proyecto)

    return proyecto


def obtener_proyectos(db: Session, usuario: Usuario):
    query = db.query(Proyecto)
    if usuario and usuario.rol == "EMPLEADO":
        from sqlalchemy import or_
        query = query.filter(
            or_(
                Proyecto.usuario_id == usuario.id,
                Proyecto.usuarios.any(Usuario.id == usuario.id)
            )
        )
    query = aplicar_filtro_test(query, Proyecto, usuario)
    return query.all()


def obtener_proyecto(
    db: Session,
    proyecto_id: int,
    usuario: Usuario
):
    query = db.query(Proyecto).filter(Proyecto.id == proyecto_id)
    if usuario and usuario.rol == "EMPLEADO":
        from sqlalchemy import or_
        query = query.filter(
            or_(
                Proyecto.usuario_id == usuario.id,
                Proyecto.usuarios.any(Usuario.id == usuario.id)
            )
        )
    query = aplicar_filtro_test(query, Proyecto, usuario)
    return query.first()


def actualizar_proyecto(
    db: Session,
    proyecto: Proyecto,
    datos: ProyectoActualizar
):
    cambios = datos.model_dump(
        exclude_unset=True
    )

    if "cliente_id" in cambios:

        cliente = (
            db.query(Cliente)
            .filter(
                Cliente.id == cambios["cliente_id"],
                Cliente.activo == True
            )
            .first()
        )

        if not cliente:
            return None

    for campo, valor in cambios.items():
        setattr(proyecto, campo, valor)

    db.commit()
    db.refresh(proyecto)

    return proyecto


def eliminar_proyecto(
    db: Session,
    proyecto: Proyecto
):
    proyecto.estado = "CANCELADO"

    db.commit()
    db.refresh(proyecto)

    return proyecto

def obtener_proyectos_cancelados(db: Session, usuario: Usuario):
    query = db.query(Proyecto).filter(
        Proyecto.estado == "CANCELADO"
    )
    query = aplicar_filtro_test(query, Proyecto, usuario)
    return query.all()
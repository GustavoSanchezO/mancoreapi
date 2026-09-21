from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencias import get_current_user, require_admin
from app.database.dependencias import get_db
from app.models.usuario import Usuario
from app.models.proyecto_schema import (
    ProyectoCrear,
    ProyectoActualizar,
    ProyectoRespuesta
)
from app.services import proyecto as proyecto_service


router = APIRouter(
    prefix="/proyectos",
    tags=["Proyectos"]
)


@router.post(
    "",
    response_model=ProyectoRespuesta
)
def crear_proyecto(
    datos: ProyectoCrear,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    proyecto = proyecto_service.crear_proyecto(
        db,
        datos,
        usuario
    )

    if not proyecto:
        raise HTTPException(
            status_code=404,
            detail="El cliente no existe o está inactivo."
        )

    return proyecto


@router.get(
    "",
    response_model=list[ProyectoRespuesta]
)
def listar_proyectos(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    return proyecto_service.obtener_proyectos(db, usuario)

@router.get(
    "/cancelados",
    response_model=list[ProyectoRespuesta]
)
def listar_proyectos_cancelados(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_admin)
):
    return proyecto_service.obtener_proyectos_cancelados(db, usuario)

@router.get(
    "/{proyecto_id}",
    response_model=ProyectoRespuesta
)
def obtener_proyecto(
    proyecto_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    proyecto = proyecto_service.obtener_proyecto(
        db,
        proyecto_id,
        usuario
    )

    if not proyecto:
        raise HTTPException(
            status_code=404,
            detail="Proyecto no encontrado."
        )

    return proyecto


@router.put(
    "/{proyecto_id}",
    response_model=ProyectoRespuesta
)
def actualizar_proyecto(
    proyecto_id: int,
    datos: ProyectoActualizar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    proyecto = proyecto_service.obtener_proyecto(
        db,
        proyecto_id,
        usuario
    )

    if not proyecto:
        raise HTTPException(
            status_code=404,
            detail="Proyecto no encontrado."
        )

    actualizado = proyecto_service.actualizar_proyecto(
        db,
        proyecto,
        datos
    )

    if not actualizado:
        raise HTTPException(
            status_code=404,
            detail="El cliente no existe o está inactivo."
        )

    return actualizado


@router.delete(
    "/{proyecto_id}",
    response_model=ProyectoRespuesta
)
def eliminar_proyecto(
    proyecto_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    proyecto = proyecto_service.obtener_proyecto(
        db,
        proyecto_id,
        usuario
    )

    if not proyecto:
        raise HTTPException(
            status_code=404,
            detail="Proyecto no encontrado."
        )

    return proyecto_service.eliminar_proyecto(
        db,
        proyecto
    )
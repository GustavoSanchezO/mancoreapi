from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencias import get_current_user
from app.database.dependencias import get_db

from app.models.usuario import Usuario
from app.models.venta_schema import (
    VentaCrear,
    VentaRespuesta,
    VentaDetalleRespuesta,
    VentaDetalleCompletoRespuesta,
    VentaEstadoActualizar,
    VentaRentabilidadRespuesta,
    VentaActualizar
)

from app.services.venta import (
    crear_venta,
    obtener_ventas,
    obtener_venta_detalle,
    actualizar_estado_venta,
    obtener_rentabilidad_venta,
    actualizar_venta
)

router = APIRouter(
    prefix="/ventas",
    tags=["Ventas"]
)

@router.post(
    "",
    response_model=VentaRespuesta,
    status_code=201
)
def crear_venta_endpoint(
    venta: VentaCrear,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        nueva_venta = crear_venta(
            db=db,
            cotizacion_id=venta.cotizacion_id,
            fecha=venta.fecha,
            fecha_pago=venta.fecha_pago,
            usuario=usuario
        )
        return nueva_venta
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "",
    response_model=list[VentaRespuesta]
)
def listar_ventas(
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return obtener_ventas(db, usuario)


@router.get(
    "/{venta_id}",
    response_model=VentaDetalleCompletoRespuesta
)
def obtener_venta_endpoint(
    venta_id: int,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        venta_detalle = obtener_venta_detalle(db, venta_id, usuario)
        return venta_detalle
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch(
    "/{venta_id}/estado",
    response_model=VentaRespuesta
)
def actualizar_estado_venta_endpoint(
    venta_id: int,
    datos: VentaEstadoActualizar,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        venta_actualizada = actualizar_estado_venta(
            db=db,
            venta_id=venta_id,
            nuevo_estado=datos.estado
        )
        return venta_actualizada
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get(
    "/{venta_id}/rentabilidad",
    response_model=VentaRentabilidadRespuesta
)
def obtener_rentabilidad_venta_endpoint(
    venta_id: int,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        rentabilidad = obtener_rentabilidad_venta(db, venta_id, usuario)
        return rentabilidad
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put(
    "/{venta_id}",
    response_model=VentaRespuesta
)
def actualizar_venta_endpoint(
    venta_id: int,
    datos: VentaActualizar,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        venta_actualizada = actualizar_venta(db, venta_id, datos, usuario)
        return venta_actualizada
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.auth.dependencias import get_current_user
from app.database.dependencias import get_db
from app.models.reporte_mantenimiento_schema import (
    ReporteMantenimientoActualizar,
    ReporteMantenimientoCrear,
    ReporteMantenimientoDetalleRespuesta,
    ReporteMantenimientoListaRespuesta,
    SiguienteFolioRespuesta,
)
from app.models.usuario import Usuario
from app.services.pdf import generar_pdf_reporte_mantenimiento
from app.services.reporte_mantenimiento import (
    actualizar_reporte_mantenimiento,
    crear_reporte_mantenimiento,
    eliminar_reporte_mantenimiento,
    obtener_reporte_mantenimiento_detalle,
    obtener_reporte_para_pdf,
    obtener_reportes_mantenimiento,
    obtener_siguiente_folio,
)


router = APIRouter(
    prefix="/reportes-mantenimiento",
    tags=["Reportes de Mantenimiento"],
)


@router.get(
    "/siguiente-folio",
    response_model=SiguienteFolioRespuesta,
)
def siguiente_folio(
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return {"folio": obtener_siguiente_folio(db, usuario)}


@router.get(
    "",
    response_model=list[ReporteMantenimientoListaRespuesta],
)
def listar_reportes_mantenimiento(
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return obtener_reportes_mantenimiento(db, usuario)


@router.post(
    "",
    response_model=ReporteMantenimientoDetalleRespuesta,
    status_code=201,
)
def crear_reporte_endpoint(
    datos: ReporteMantenimientoCrear,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        reporte = crear_reporte_mantenimiento(
            db=db,
            datos=datos,
            usuario=usuario,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not reporte:
        raise HTTPException(
            status_code=400,
            detail="El cliente seleccionado no es válido o está inactivo.",
        )

    return reporte


@router.get(
    "/{reporte_id}",
    response_model=ReporteMantenimientoDetalleRespuesta,
)
def obtener_reporte_endpoint(
    reporte_id: int,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    reporte = obtener_reporte_mantenimiento_detalle(
        db=db,
        reporte_id=reporte_id,
        usuario=usuario,
    )
    if not reporte:
        raise HTTPException(
            status_code=404,
            detail="El reporte de mantenimiento no existe.",
        )
    return reporte


@router.put(
    "/{reporte_id}",
    response_model=ReporteMantenimientoDetalleRespuesta,
)
def actualizar_reporte_endpoint(
    reporte_id: int,
    datos: ReporteMantenimientoActualizar,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        reporte = actualizar_reporte_mantenimiento(
            db=db,
            reporte_id=reporte_id,
            datos=datos,
            usuario=usuario,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not reporte:
        raise HTTPException(
            status_code=404,
            detail="El reporte de mantenimiento no existe.",
        )

    return reporte


@router.delete("/{reporte_id}")
def eliminar_reporte_endpoint(
    reporte_id: int,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    eliminado = eliminar_reporte_mantenimiento(
        db=db,
        reporte_id=reporte_id,
        usuario=usuario,
    )
    if not eliminado:
        raise HTTPException(
            status_code=404,
            detail="El reporte de mantenimiento no existe.",
        )
    return {"ok": True}


@router.get("/{reporte_id}/pdf")
def generar_pdf_reporte_endpoint(
    reporte_id: int,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    datos_pdf = obtener_reporte_para_pdf(
        db=db,
        reporte_id=reporte_id,
        usuario=usuario,
    )
    if not datos_pdf:
        raise HTTPException(
            status_code=404,
            detail="El reporte de mantenimiento no existe.",
        )

    pdf = generar_pdf_reporte_mantenimiento(datos_pdf)
    nombre_archivo = datos_pdf["nombre_archivo_pdf"]

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="{nombre_archivo}"',
        },
    )

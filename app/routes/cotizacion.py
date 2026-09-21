import re
import unicodedata

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.auth.dependencias import get_current_user
from app.database.dependencias import get_db

from app.models.usuario import Usuario
from app.models.cotizacion import Cotizacion
from app.models.cotizacion_db import CotizacionDB
from app.models.cotizacion_schema import (
    CotizacionCrear,
    CotizacionActualizar,
    CotizacionEstadoActualizar,
    CotizacionDetalleRespuesta,
    CotizacionListaRespuesta
)

from app.services.cotizacion import calcular_cotizacion
from app.services.cotizacion_db import (
    crear_cotizacion,
    obtener_cotizacion_detalle,
    obtener_cotizaciones,
    actualizar_cotizacion,
    actualizar_estado_cotizacion
)
from app.services.seguridad_db import aplicar_filtro_test
from app.services.pdf import generar_pdf


router = APIRouter(
    tags=["Cotizaciones"]
)


def limpiar_nombre_archivo(texto: str) -> str:
    # Eliminar acentos
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("ascii")

    # Reemplazar cualquier cosa que no sea letra o número
    # por un guion
    texto = re.sub(r"[^a-zA-Z0-9]+", "-", texto)

    # Eliminar guiones al principio y al final
    texto = texto.strip("-")

    return texto


# ============================================================
# ENDPOINT ANTIGUO - SOLO PDF
# ============================================================

@router.post("/generar/cotizacion")
def generar_cotizacion(
    cotizacion: Cotizacion,
    usuario: Usuario = Depends(get_current_user)
):

    datos = calcular_cotizacion(cotizacion)

    pdf = generar_pdf(datos)

    nombre_proyecto = limpiar_nombre_archivo(
        cotizacion.proyecto.nombre
    )

    nombre_archivo = (
        f"cotizacion-{cotizacion.rfq}-{nombre_proyecto}.pdf"
    )

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f'inline; filename="{nombre_archivo}"'
            )
        }
    )


# ============================================================
# NUEVO ENDPOINT - CREAR COTIZACIÓN + PDF
# ============================================================

@router.post("/cotizaciones", response_model=CotizacionDetalleRespuesta)
def crear_cotizacion_endpoint(
    datos: CotizacionCrear,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    cotizacion = crear_cotizacion(
        db=db,
        datos=datos,
        usuario=usuario
    )

    if not cotizacion:
        raise HTTPException(
            status_code=400,
            detail="El cliente o proyecto no es válido."
        )

    cotizacion_detalle = obtener_cotizacion_detalle(
        db=db,
        cotizacion_id=cotizacion.id,
        usuario=usuario
    )

    return cotizacion_detalle

@router.get(
    "/cotizaciones",
    response_model=list[CotizacionListaRespuesta]
)
def listar_cotizaciones(
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return obtener_cotizaciones(db, usuario)

@router.get(
    "/cotizaciones/{cotizacion_id}",
    response_model=CotizacionDetalleRespuesta
)
def obtener_cotizacion(
    cotizacion_id: int,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cotizacion = obtener_cotizacion_detalle(
        db=db,
        cotizacion_id=cotizacion_id,
        usuario=usuario
    )

    if not cotizacion:
        raise HTTPException(
            status_code=404,
            detail="La cotización no existe."
        )

    return cotizacion

@router.get("/cotizaciones/{cotizacion_id}/pdf")
def generar_pdf_cotizacion(
    cotizacion_id: int,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(CotizacionDB).filter(CotizacionDB.id == cotizacion_id)
    query = aplicar_filtro_test(query, CotizacionDB, usuario)
    cotizacion = query.first()

    if not cotizacion:
        raise HTTPException(
            status_code=404,
            detail="La cotización no existe."
        )

    datos_pdf = calcular_cotizacion(
        cotizacion=cotizacion,
        db=db
    )

    pdf = generar_pdf(datos_pdf)

    proyecto_obj = datos_pdf.get("proyecto")
    nombre_raw = getattr(proyecto_obj, "nombre", "proyecto") if proyecto_obj else "proyecto"
    nombre_proyecto = limpiar_nombre_archivo(nombre_raw)

    nombre_archivo = (
        f"cotizacion-{cotizacion.rfq}-{nombre_proyecto}.pdf"
    )

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f'inline; filename="{nombre_archivo}"'
            )
        }
    )

@router.put(
    "/cotizaciones/{cotizacion_id}",
    response_model=CotizacionDetalleRespuesta
)
def actualizar_cotizacion_endpoint(
    cotizacion_id: int,
    datos: CotizacionActualizar,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        cotizacion = actualizar_cotizacion(
            db=db,
            cotizacion_id=cotizacion_id,
            datos=datos
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    if not cotizacion:
        raise HTTPException(
            status_code=404,
            detail="La cotización, cliente o proyecto no es válido."
        )

    return obtener_cotizacion_detalle(
        db=db,
        cotizacion_id=cotizacion.id,
        usuario=usuario
    )

@router.patch(
    "/cotizaciones/{cotizacion_id}/estado"
)
def cambiar_estado_cotizacion(
    cotizacion_id: int,
    datos: CotizacionEstadoActualizar,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        cotizacion = actualizar_estado_cotizacion(
            db=db,
            cotizacion_id=cotizacion_id,
            nuevo_estado=datos.estado
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    if not cotizacion:
        raise HTTPException(
            status_code=404,
            detail="La cotización no existe."
        )

    return {
        "id": cotizacion.id,
        "rfq": cotizacion.rfq,
        "estado": cotizacion.estado
    }
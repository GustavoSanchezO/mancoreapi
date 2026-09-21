from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.cotizacion_db import CotizacionDB
from app.models.cliente import Cliente
from app.models.proyecto import Proyecto
from app.models.partida_cotizacion import PartidaCotizacion

from num2words import num2words



IVA = Decimal("0.16")


def calcular_cotizacion(
    cotizacion,
    db: Session | None = None
):
    """
    Prepara los datos de una cotización (almacenada en BD o en memoria)
    para generar el PDF.
    """
    # Si viene como CotizacionDB o se especificó db, procesamos vía SQLAlchemy
    if isinstance(cotizacion, CotizacionDB) or db is not None:
        if not isinstance(cotizacion, CotizacionDB) and db is not None:
            # Si cotizacion es un ID o se pasó cotizacion como CotizacionDB implícito
            pass

        cliente = (
            db.query(Cliente)
            .filter(Cliente.id == cotizacion.cliente_id)
            .first()
        )

        proyecto = (
            db.query(Proyecto)
            .filter(Proyecto.id == cotizacion.proyecto_id)
            .first()
        )

        partidas = (
            db.query(PartidaCotizacion)
            .filter(
                PartidaCotizacion.cotizacion_id == cotizacion.id
            )
            .all()
        )

        partidas_pdf = []
        for partida in partidas:
            partidas_pdf.append({
                "descripcion": partida.descripcion,
                "cantidad": partida.cantidad,
                "precio_unitario": partida.precio_unitario,
                "total": partida.total
            })

        subtotal = cotizacion.subtotal
        iva = cotizacion.iva
        total = cotizacion.total
        rfq = cotizacion.rfq
        fecha = cotizacion.fecha
        tiempo_entrega = cotizacion.tiempo_entrega_estimado
        nota_importante_texto = getattr(cotizacion, "nota_importante_texto", None)
        anexos_fotograficos = [anexo.ruta_imagen for anexo in cotizacion.anexos] if hasattr(cotizacion, "anexos") else []
    else:
        # Cotización en memoria (modelo Pydantic)
        cliente = cotizacion.cliente
        # Aseguramos que el proyecto tenga el campo descripcion para la plantilla HTML
        proyecto_nombre = getattr(cotizacion.proyecto, "nombre", "")
        proyecto_desc = getattr(cotizacion.proyecto, "descripcion", None) or getattr(cotizacion.proyecto, "descripcion_corta", "")
        
        class ProyectoWrapper:
            def __init__(self, nombre, descripcion):
                self.nombre = nombre
                self.descripcion = descripcion

        proyecto = ProyectoWrapper(proyecto_nombre, proyecto_desc)

        partidas_pdf = []
        subtotal = Decimal("0.00")

        for partida in cotizacion.partidas:
            total_partida = Decimal(str(partida.cantidad)) * Decimal(str(partida.precio_unitario))
            partidas_pdf.append({
                "descripcion": partida.descripcion,
                "cantidad": partida.cantidad,
                "precio_unitario": partida.precio_unitario,
                "total": total_partida
            })
            subtotal += total_partida

        iva = subtotal * IVA
        total = subtotal + iva
        rfq = cotizacion.rfq
        fecha = cotizacion.fecha
        tiempo_entrega = cotizacion.tiempo_entrega_estimado
        nota_importante_texto = getattr(cotizacion, "nota_importante_texto", None)
        anexos_fotograficos = getattr(cotizacion, "anexos_fotograficos", [])

    # Construimos la estructura normalizada para Jinja
    cotizacion_wrapper = {
        "rfq": rfq,
        "fecha": fecha,
        "cliente": cliente,
        "proyecto": proyecto,
        "tiempo_entrega_estimado": tiempo_entrega,
        "nota_importante_texto": nota_importante_texto
    }

    return {
        "rfq": rfq,
        "fecha": fecha,
        "cliente": cliente,
        "proyecto": proyecto,
        "cotizacion": cotizacion_wrapper,
        "partidas": partidas_pdf,
        "subtotal": subtotal,
        "iva": iva,
        "total": total,
        "fecha_letras": fecha_en_letras(fecha),
        "total_letras": numero_a_letras(total),
        "tiempo_entrega_estimado": tiempo_entrega,
        "nota_importante_texto": nota_importante_texto,
        "anexos_fotograficos": anexos_fotograficos
    }


def numero_a_letras(numero: Decimal) -> str:

    entero = int(numero)

    centavos = round(
        (numero - entero) * 100
    )

    letras = num2words(
        entero,
        lang="es"
    )

    letras = letras.capitalize()

    return (
        f"{letras} "
        f"pesos "
        f"{centavos:02d}/100 M.N."
    )


MESES = [
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre"
]


def fecha_en_letras(fecha):

    return (
        f"{fecha.day} de "
        f"{MESES[fecha.month - 1]} del "
        f"{fecha.year}"
    )
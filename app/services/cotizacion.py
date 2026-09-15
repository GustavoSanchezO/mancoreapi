from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.cotizacion_db import CotizacionDB
from app.models.cliente import Cliente
from app.models.proyecto import Proyecto
from app.models.partida_cotizacion import PartidaCotizacion

from num2words import num2words



IVA = Decimal("0.16")


def calcular_cotizacion(
    db: Session,
    cotizacion: CotizacionDB
):
    """
    Prepara los datos de una cotización almacenada en BD
    para generar el PDF.
    """

    # ---------------------------------------------------------
    # Obtener cliente
    # ---------------------------------------------------------

    cliente = (
        db.query(Cliente)
        .filter(Cliente.id == cotizacion.cliente_id)
        .first()
    )

    # ---------------------------------------------------------
    # Obtener proyecto
    # ---------------------------------------------------------

    proyecto = (
        db.query(Proyecto)
        .filter(Proyecto.id == cotizacion.proyecto_id)
        .first()
    )

    # ---------------------------------------------------------
    # Obtener partidas
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # Preparar datos para Jinja
    # ---------------------------------------------------------

    return {
        "rfq": cotizacion.rfq,
        "fecha": cotizacion.fecha,

        "cliente": cliente,

        "proyecto": proyecto,

        "partidas": partidas_pdf,

        "subtotal": cotizacion.subtotal,
        "iva": cotizacion.iva,
        "total": cotizacion.total,

        "fecha_letras": fecha_en_letras(
            cotizacion.fecha
        ),

        "total_letras": numero_a_letras(
            cotizacion.total
        ),

        "tiempo_entrega_estimado":
            cotizacion.tiempo_entrega_estimado
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
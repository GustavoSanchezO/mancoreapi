from io import BytesIO
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML


BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATES_DIR = BASE_DIR / "templates"


templates = Environment(
    loader=FileSystemLoader("app/templates") 
)


def generar_pdf(datos):

    template = templates.get_template("cotizacion.html")

    html = template.render(
        cotizacion=datos,

        partidas=datos["partidas"],

        subtotal=datos["subtotal"],

        iva=datos["iva"],

        total=datos["total"],

        fecha_letras=datos["fecha_letras"],

        total_letras=datos["total_letras"]
    )

    pdf = HTML(
        string=html,
        base_url=str(TEMPLATES_DIR)
    ).write_pdf()

    return BytesIO(pdf)
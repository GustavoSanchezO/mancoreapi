import sys
from datetime import date
from decimal import Decimal
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Asegurar que la raíz del proyecto esté en sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.main import app
from app.auth.dependencias import get_current_user, require_admin
from app.database.base import Base
from app.database.dependencias import get_db

# Importar modelos requeridos para el esquema de base de datos
from app.models.usuario import Usuario
from app.models.cliente import Cliente
from app.models.proyecto import Proyecto
from app.models.cotizacion_db import CotizacionDB
from app.models.partida_cotizacion import PartidaCotizacion
from app.models.material_cotizacion import MaterialCotizacion
from app.models.mano_obra_cotizada import ManoObraCotizada
from app.models.gasto_extra_cotizado import GastoExtraCotizado
from app.models.costo_material_real import CostoMaterialReal
from app.models.costo_mano_obra_real import CostoManoObraReal
from app.models.costo_gasto_extra_real import CostoGastoExtraReal
from app.models.venta import Venta


@pytest.fixture
def db_engine():
    """Crea una base de datos SQLite en memoria para cada prueba."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(db_engine):
    """Crea una sesión de base de datos aislada por prueba con datos base."""
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestingSession()

    # Usuario de prueba con rol ADMIN
    usuario = Usuario(
        id=1,
        email="admin_test@mancore.mx",
        nombre="Admin Pruebas",
        rol="ADMIN",
        activo=True,
        es_test=True
    )
    session.add(usuario)
    session.flush()

    # Cliente base
    cliente = Cliente(
        id=1,
        nombre_empresa="Empresa Demo S.A.",
        direccion="Av. Principal 123",
        activo=True,
        usuario_id=usuario.id,
        es_test=True
    )
    session.add(cliente)
    session.flush()

    # Proyecto base
    proyecto = Proyecto(
        id=1,
        nombre="Proyecto Demo",
        descripcion="Descripción demo",
        cliente_id=cliente.id,
        usuario_id=usuario.id,
        es_test=True
    )
    session.add(proyecto)
    session.flush()

    # Cotización base para validar estructuras
    cotizacion = CotizacionDB(
        id=1,
        rfq="RFQ-TEST-001",
        nombre_archivo="RFQ REQ RFQ-TEST-001",
        fecha=date(2026, 1, 15),
        cliente_id=cliente.id,
        proyecto_id=proyecto.id,
        usuario_id=usuario.id,
        tiempo_entrega_estimado="10 días",
        estado="PENDIENTE",
        subtotal=Decimal("1000.00"),
        iva=Decimal("160.00"),
        total=Decimal("1160.00"),
        es_test=True
    )
    session.add(cotizacion)
    session.commit()

    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    """Configura el TestClient inyectando dependencias simuladas (caja blanca)."""
    # Obtenemos el usuario administrador de la base de datos de pruebas
    usuario_admin = db_session.query(Usuario).filter(Usuario.id == 1).first()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: usuario_admin
    app.dependency_overrides[require_admin] = lambda: usuario_admin

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# ==============================================================================
# PRUEBAS UNITARIAS DE CAJA BLANCA
# ==============================================================================

def test_get_health(client):
    """Valida el endpoint de salud GET /health (código 200 y payload esperado)."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_cotizaciones_estructura(client):
    """Valida que GET /cotizaciones responda 200 y su estructura de datos sea correcta."""
    response = client.get("/cotizaciones")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    item = data[0]
    # Validación de campos requeridos por el esquema CotizacionListaRespuesta
    claves_esperadas = {
        "id",
        "rfq",
        "fecha",
        "cliente_id",
        "proyecto_id",
        "usuario_id",
        "tiempo_entrega_estimado",
        "estado",
        "subtotal",
        "iva",
        "total"
    }
    assert claves_esperadas.issubset(item.keys())
    assert item["rfq"] == "RFQ-TEST-001"
    assert item["estado"] == "PENDIENTE"


def test_get_cotizacion_inexistente_retorna_404(client):
    """Valida que GET /cotizaciones/99999 retorne error 404 al no encontrar el recurso."""
    response = client.get("/cotizaciones/99999")
    assert response.status_code == 404

    body = response.json()
    assert "detail" in body
    assert body["detail"] == "La cotización no existe."


def test_post_cotizaciones_sin_body_retorna_422(client):
    """Valida que POST /cotizaciones retorne error 422 (Unprocessable Entity) si falta el body."""
    # Envío sin payload body para activar el error de validación de FastAPI / Pydantic
    response = client.post("/cotizaciones")
    assert response.status_code == 422

    body = response.json()
    assert "detail" in body
    assert isinstance(body["detail"], list)
    assert any(err.get("type") == "missing" for err in body["detail"])

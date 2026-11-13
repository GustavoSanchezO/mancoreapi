import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.auth.dependencias import get_current_user
from app.database.base import Base
from app.database.dependencias import get_db
from app.main import app
from app.models.cliente import Cliente
from app.models.reporte_mantenimiento import ReporteMantenimiento
from app.models.usuario import Usuario
from app.services.usuario import purgar_usuario_test


@pytest.fixture
def db_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(db_engine):
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestingSession()

    usuario = Usuario(
        id=1,
        email="admin_rep@mancore.mx",
        nombre="Admin Reportes",
        rol="ADMIN",
        activo=True,
        es_test=False,
    )
    usuario_test = Usuario(
        id=2,
        email="test_rep@mancore.test",
        nombre="Test Reportes",
        rol="EMPLEADO",
        activo=True,
        es_test=True,
    )
    session.add_all([usuario, usuario_test])
    session.flush()

    cliente = Cliente(
        id=1,
        nombre_empresa="YAZAKI LAGUNA",
        direccion="Parque Industrial Laguna",
        activo=True,
        usuario_id=usuario.id,
        es_test=False,
    )
    cliente_inactivo = Cliente(
        id=2,
        nombre_empresa="CLIENTE INACTIVO",
        direccion="N/A",
        activo=False,
        usuario_id=usuario.id,
        es_test=False,
    )
    cliente_test = Cliente(
        id=3,
        nombre_empresa="CLIENTE TEST",
        direccion="Test 123",
        activo=True,
        usuario_id=usuario_test.id,
        es_test=True,
    )
    session.add_all([cliente, cliente_inactivo, cliente_test])
    session.commit()

    yield session
    session.close()


@pytest.fixture
def client(db_session):
    usuario_activo = db_session.query(Usuario).filter(Usuario.id == 1).first()

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_get_current_user():
        return usuario_activo

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


def _payload_ejemplo(cliente_id=1, folio="0301"):
    return {
        "folio": folio,
        "nombre_documento": "Reporte de Mantenimiento",
        "cliente_id": cliente_id,
        "tipo_mantenimiento": "MTTO. PREVENTIVO A EMPLAYADORA LANTECH.",
        "unidad": "EMPLAYADORA",
        "marca": "LANTECH",
        "modelo": "Q-400",
        "observaciones_generales": "<p>Equipo listo para operación continua.</p>",
        "secciones": [
            {
                "titulo": "SISTEMA ELÉCTRICO Y DE CONTROL",
                "actividades": [
                    {
                        "actividad": "Inspección de tablero eléctrico.",
                        "estado": "CONFORME",
                        "observaciones": "Tablero limpio, revisión de ajuste y sellado hermético en buen estado.",
                    },
                    {
                        "actividad": "Inspección de cableado de poder.",
                        "estado": "CONFORME",
                        "observaciones": "Aislamiento en óptimas condiciones.",
                    },
                ],
            },
            {
                "titulo": "SISTEMAS MECÁNICOS.",
                "actividades": [
                    {
                        "actividad": "Tensión, alineación de correas/bandas de transmisión.",
                        "estado": "AJUSTE",
                        "observaciones": "Se realiza ajuste de tensor de banda con torquímetro a 34 N-m.",
                    },
                    {
                        "actividad": "Inspección de rodillos de dirección de la emplayadora.",
                        "estado": "REQUIERE ATENCIÓN.",
                        "observaciones": "Presentan desgaste normal por rodamiento. (ANEXO PARTES DE REEMPLAZO PAG.2)",
                    },
                ],
            },
        ],
        "anexos_fotograficos": [],
        "partes_reemplazo": [
            {
                "descripcion": "(PN-30232873 ROLLER IDLER ASM 1.9 OD X 20.88 GALVANIZED)",
                "imagenes": [],
            }
        ],
    }


def test_crear_reporte_fecha_automatica_y_titulo(client):
    res = client.post("/reportes-mantenimiento", json=_payload_ejemplo())
    assert res.status_code == 201, res.text
    data = res.json()

    hoy_mx = datetime.now(ZoneInfo("America/Mexico_City")).date().isoformat()
    assert data["fecha"] == hoy_mx
    assert data["folio"] == "0301"
    assert data["nombre_documento"] == "Reporte de Mantenimiento"
    assert data["titulo_documento"] == "Reporte de Mantenimiento 0301"
    assert data["cliente_nombre"] == "YAZAKI LAGUNA"
    assert data["cliente_direccion"] == "Parque Industrial Laguna"
    assert len(data["secciones"]) == 2
    assert data["secciones"][0]["actividades"][0]["item_numero"] == 1
    assert data["secciones"][0]["actividades"][1]["item_numero"] == 2
    assert len(data["partes_reemplazo"]) == 1

    # Siguiente folio sugerido debe incrementar 0301 -> 0302
    sig = client.get("/reportes-mantenimiento/siguiente-folio")
    assert sig.status_code == 200
    assert sig.json()["folio"] == "0302"


def test_cliente_invalido_o_inactivo_retorna_400(client):
    res_inactivo = client.post("/reportes-mantenimiento", json=_payload_ejemplo(cliente_id=2))
    assert res_inactivo.status_code == 400

    res_inexistente = client.post("/reportes-mantenimiento", json=_payload_ejemplo(cliente_id=999))
    assert res_inexistente.status_code == 400

    res_otro_ambito = client.post("/reportes-mantenimiento", json=_payload_ejemplo(cliente_id=3))
    assert res_otro_ambito.status_code == 400


def test_folio_duplicado_retorna_400(client):
    res1 = client.post("/reportes-mantenimiento", json=_payload_ejemplo(folio="0301"))
    assert res1.status_code == 201

    res2 = client.post("/reportes-mantenimiento", json=_payload_ejemplo(folio="0301"))
    assert res2.status_code == 400


def test_listar_actualizar_eliminar_y_generar_pdf(client):
    res = client.post("/reportes-mantenimiento", json=_payload_ejemplo(folio="0301"))
    assert res.status_code == 201
    reporte_id = res.json()["id"]

    # Listar
    lista = client.get("/reportes-mantenimiento")
    assert lista.status_code == 200
    items = lista.json()
    assert len(items) == 1
    assert items[0]["titulo_documento"] == "Reporte de Mantenimiento 0301"
    assert items[0]["total_secciones"] == 2
    assert items[0]["total_actividades"] == 4

    # PDF generation
    pdf_res = client.get(f"/reportes-mantenimiento/{reporte_id}/pdf")
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert 'filename="Reporte de Mantenimiento 0301.pdf"' in pdf_res.headers["content-disposition"]
    assert pdf_res.content.startswith(b"%PDF-")

    # Actualizar (cambiando nombre del documento y folio)
    payload_upd = _payload_ejemplo(folio="0305")
    payload_upd["nombre_documento"] = "Mtto Preventivo Lantech"
    upd = client.put(f"/reportes-mantenimiento/{reporte_id}", json=payload_upd)
    assert upd.status_code == 200
    assert upd.json()["titulo_documento"] == "Mtto Preventivo Lantech 0305"

    # PDF con nuevo titulo
    pdf_res2 = client.get(f"/reportes-mantenimiento/{reporte_id}/pdf")
    assert pdf_res2.status_code == 200
    assert 'filename="Mtto Preventivo Lantech 0305.pdf"' in pdf_res2.headers["content-disposition"]

    # Eliminar
    del_res = client.delete(f"/reportes-mantenimiento/{reporte_id}")
    assert del_res.status_code == 200
    assert client.get(f"/reportes-mantenimiento/{reporte_id}").status_code == 404


def test_purgar_usuario_test_elimina_reportes_mantenimiento(db_session):
    usuario_test = db_session.query(Usuario).filter(Usuario.id == 2).first()

    def override_get_db():
        yield db_session

    def override_user_test():
        return usuario_test

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_user_test

    with TestClient(app) as c:
        res = c.post("/reportes-mantenimiento", json=_payload_ejemplo(cliente_id=3, folio="0301"))
        assert res.status_code == 201

    app.dependency_overrides.clear()

    assert db_session.query(ReporteMantenimiento).filter(ReporteMantenimiento.es_test == True).count() == 1
    purgado = purgar_usuario_test(db_session, usuario_test.id)
    assert purgado is True
    assert db_session.query(ReporteMantenimiento).filter(ReporteMantenimiento.es_test == True).count() == 0

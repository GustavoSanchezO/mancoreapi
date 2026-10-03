from datetime import date
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.models.cliente import Cliente
from app.models.costo_gasto_extra_real import CostoGastoExtraReal
from app.models.costo_mano_obra_real import CostoManoObraReal
from app.models.costo_material_real import CostoMaterialReal
from app.models.cotizacion_db import CotizacionDB
from app.models.gasto_extra_cotizado import GastoExtraCotizado
from app.models.mano_obra_cotizada import ManoObraCotizada
from app.models.material_cotizacion import MaterialCotizacion
from app.models.partida_cotizacion import PartidaCotizacion
from app.models.proyecto import Proyecto
from app.models.usuario import Usuario
from app.models.venta import Venta
from app.services.costo_material_real import crear_costo_material_real
from app.services.venta import crear_venta


def test_crear_costo_material_real_manual_sin_material_cotizado():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    usuario = Usuario(
        email="admin2@test.com",
        nombre="Admin",
        rol="ADMIN",
        activo=True,
        es_test=False,
    )
    session.add(usuario)
    session.flush()

    cliente = Cliente(
        nombre_empresa="ACME",
        direccion="Calle 2",
        activo=True,
        usuario_id=usuario.id,
        es_test=False,
    )
    session.add(cliente)
    session.flush()

    proyecto = Proyecto(
        nombre="Proyecto 2",
        descripcion="Desc",
        cliente_id=cliente.id,
        usuario_id=usuario.id,
        es_test=False,
    )
    session.add(proyecto)
    session.flush()

    cotizacion = CotizacionDB(
        rfq="RFQ-002",
        nombre_archivo="RFQ REQ RFQ-002",
        fecha=date(2026, 2, 10),
        cliente_id=cliente.id,
        proyecto_id=proyecto.id,
        usuario_id=usuario.id,
        tiempo_entrega_estimado="15 días",
        estado="ACEPTADA",
        subtotal=Decimal("50.00"),
        iva=Decimal("8.00"),
        total=Decimal("58.00"),
        es_test=False,
    )
    session.add(cotizacion)
    session.flush()

    venta = Venta(
        cotizacion_id=cotizacion.id,
        fecha=date(2026, 2, 12),
        fecha_pago=date(2026, 2, 20),
        subtotal=cotizacion.subtotal,
        iva=cotizacion.iva,
        total=cotizacion.total,
        estado="PENDIENTE",
        usuario_id=usuario.id,
        es_test=False,
    )
    session.add(venta)
    session.commit()

    datos = type(
        "DatosManual",
        (),
        {
            "venta_id": venta.id,
            "material_cotizacion_id": None,
            "descripcion": "Material extra manual",
            "cantidad": Decimal("3.00"),
            "precio_unitario": Decimal("12.50"),
            "fecha": date(2026, 2, 13),
        },
    )()

    costo = crear_costo_material_real(session, datos)

    assert costo is not None
    assert costo.material_cotizacion_id is None
    assert costo.total == Decimal("37.50")


def test_crear_venta_genera_costos_reales_cero():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    usuario = Usuario(
        email="admin@test.com",
        nombre="Admin",
        rol="ADMIN",
        activo=True,
        es_test=False,
    )
    session.add(usuario)
    session.flush()

    cliente = Cliente(
        nombre_empresa="ACME",
        direccion="Calle 1",
        activo=True,
        usuario_id=usuario.id,
        es_test=False,
    )
    session.add(cliente)
    session.flush()

    proyecto = Proyecto(
        nombre="Proyecto 1",
        descripcion="Desc",
        cliente_id=cliente.id,
        usuario_id=usuario.id,
        es_test=False,
    )
    session.add(proyecto)
    session.flush()

    cotizacion = CotizacionDB(
        rfq="RFQ-001",
        nombre_archivo="RFQ REQ RFQ-001",
        fecha=date(2026, 1, 10),
        cliente_id=cliente.id,
        proyecto_id=proyecto.id,
        usuario_id=usuario.id,
        tiempo_entrega_estimado="10 días",
        estado="ACEPTADA",
        subtotal=Decimal("100.00"),
        iva=Decimal("16.00"),
        total=Decimal("116.00"),
        es_test=False,
    )
    session.add(cotizacion)
    session.flush()

    partida = PartidaCotizacion(
        cotizacion_id=cotizacion.id,
        descripcion="Partida 1",
        cantidad=Decimal("1.00"),
        precio_unitario=Decimal("100.00"),
        total=Decimal("100.00"),
    )
    session.add(partida)
    session.flush()

    material = MaterialCotizacion(
        partida_id=partida.id,
        material_id=None,
        descripcion="Material A",
        cantidad=Decimal("2.00"),
        precio_unitario=Decimal("10.00"),
        total=Decimal("20.00"),
    )
    session.add(material)
    session.flush()

    mano_obra = ManoObraCotizada(
        partida_id=partida.id,
        descripcion="Mano de obra A",
        cantidad=Decimal("3.00"),
        precio_unitario=Decimal("5.00"),
        total=Decimal("15.00"),
    )
    session.add(mano_obra)
    session.flush()

    gasto = GastoExtraCotizado(
        partida_id=partida.id,
        descripcion="Gasto extra A",
        cantidad=Decimal("1.00"),
        precio_unitario=Decimal("4.00"),
        total=Decimal("4.00"),
    )
    session.add(gasto)
    session.flush()

    session.commit()

    venta = crear_venta(
        db=session,
        cotizacion_id=cotizacion.id,
        fecha=date(2026, 1, 12),
        fecha_pago=date(2026, 1, 20),
        usuario=usuario,
    )

    assert venta is not None
    assert session.query(CostoMaterialReal).filter_by(venta_id=venta.id, material_cotizacion_id=material.id).count() == 1
    assert session.query(CostoManoObraReal).filter_by(venta_id=venta.id, mano_obra_cotizada_id=mano_obra.id).count() == 1
    assert session.query(CostoGastoExtraReal).filter_by(venta_id=venta.id, gasto_extra_cotizado_id=gasto.id).count() == 1

    costo_material = session.query(CostoMaterialReal).filter_by(venta_id=venta.id, material_cotizacion_id=material.id).one()
    assert costo_material.cantidad == Decimal("0.00")
    assert costo_material.total == Decimal("0.00")

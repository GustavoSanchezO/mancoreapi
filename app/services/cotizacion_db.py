from decimal import Decimal
from sqlalchemy.orm import Session

from app.models.usuario import Usuario
from app.models.cliente import Cliente
from app.models.proyecto import Proyecto
from app.models.cotizacion_db import CotizacionDB
from app.models.partida_cotizacion import PartidaCotizacion
from app.models.material_cotizacion import MaterialCotizacion
from app.models.mano_obra_cotizada import ManoObraCotizada
from app.models.gasto_extra_cotizado import GastoExtraCotizado
from app.models.costo_material_real import CostoMaterialReal
from app.services.seguridad_db import aplicar_filtro_test


IVA = Decimal("0.16")


def crear_cotizacion(db: Session, datos, usuario: Usuario):
    # Validar cliente
    cliente = (
        db.query(Cliente)
        .filter(
            Cliente.id == datos.cliente_id,
            Cliente.activo == True
        )
        .first()
    )

    if not cliente:
        return None

    # Validar proyecto
    proyecto = (
        db.query(Proyecto)
        .filter(Proyecto.id == datos.proyecto_id)
        .first()
    )

    if not proyecto:
        return None

    # El proyecto debe pertenecer al cliente
    if proyecto.cliente_id != datos.cliente_id:
        return None

    try:
        # Crear cotización
        cotizacion = CotizacionDB(
            rfq=datos.rfq,
            fecha=datos.fecha,
            cliente_id=datos.cliente_id,
            proyecto_id=datos.proyecto_id,
            usuario_id=usuario.id,
            es_test=usuario.es_test,
            tiempo_entrega_estimado=datos.tiempo_entrega_estimado,
            estado="COTIZACION",
            subtotal=Decimal("0.00"),
            iva=Decimal("0.00"),
            total=Decimal("0.00")
        )

        db.add(cotizacion)
        db.flush()

        subtotal = Decimal("0.00")

        # Crear partidas
        for partida_datos in datos.partidas:

            total_partida = (
                partida_datos.cantidad *
                partida_datos.precio_unitario
            )

            partida = PartidaCotizacion(
                cotizacion_id=cotizacion.id,
                descripcion=partida_datos.descripcion,
                cantidad=partida_datos.cantidad,
                precio_unitario=partida_datos.precio_unitario,
                total=total_partida
            )

            db.add(partida)
            db.flush()

            # Materiales
            for material_datos in partida_datos.materiales:

                total_material = (
                    material_datos.cantidad *
                    material_datos.precio_unitario
                )

                material = MaterialCotizacion(
                    partida_id=partida.id,
                    material_id=material_datos.material_id,
                    descripcion=material_datos.descripcion,
                    cantidad=material_datos.cantidad,
                    precio_unitario=material_datos.precio_unitario,
                    total=total_material
                )

                db.add(material)

            # Mano de obra
            for mano_obra_datos in partida_datos.mano_obra:

                total_mano_obra = (
                    mano_obra_datos.cantidad *
                    mano_obra_datos.precio_unitario
                )

                mano_obra = ManoObraCotizada(
                    partida_id=partida.id,
                    descripcion=mano_obra_datos.descripcion,
                    cantidad=mano_obra_datos.cantidad,
                    precio_unitario=mano_obra_datos.precio_unitario,
                    total=total_mano_obra
                )

                db.add(mano_obra)

            # Gastos extra
            for gasto_datos in partida_datos.gastos_extra:

                total_gasto = (
                    gasto_datos.cantidad *
                    gasto_datos.precio_unitario
                )

                gasto = GastoExtraCotizado(
                    partida_id=partida.id,
                    descripcion=gasto_datos.descripcion,
                    cantidad=gasto_datos.cantidad,
                    precio_unitario=gasto_datos.precio_unitario,
                    total=total_gasto
                )

                db.add(gasto)

            # El subtotal utiliza el precio de venta
            # de las partidas, no sus costos internos.
            subtotal += total_partida

        # Calcular IVA y total
        iva = subtotal * IVA
        total = subtotal + iva

        cotizacion.subtotal = subtotal
        cotizacion.iva = iva
        cotizacion.total = total

        # Confirmar toda la operación
        db.commit()
        db.refresh(cotizacion)

        return cotizacion

    except Exception:
        db.rollback()
        raise

def obtener_cotizacion_detalle(db: Session, cotizacion_id: int, usuario: Usuario):
    query = db.query(CotizacionDB).filter(CotizacionDB.id == cotizacion_id)
    if usuario and usuario.rol == "EMPLEADO":
        from app.models.usuario_proyecto import usuario_proyecto
        query = query.join(
            usuario_proyecto, 
            CotizacionDB.proyecto_id == usuario_proyecto.c.proyecto_id
        ).filter(
            usuario_proyecto.c.usuario_id == usuario.id
        )
    query = aplicar_filtro_test(query, CotizacionDB, usuario)
    cotizacion = query.first()

    if not cotizacion:
        return None

    partidas = (
        db.query(PartidaCotizacion)
        .filter(
            PartidaCotizacion.cotizacion_id == cotizacion.id
        )
        .all()
    )

    resultado_partidas = []

    for partida in partidas:

        materiales = (
            db.query(MaterialCotizacion)
            .filter(
                MaterialCotizacion.partida_id == partida.id
            )
            .all()
        )

        mano_obra = (
            db.query(ManoObraCotizada)
            .filter(
                ManoObraCotizada.partida_id == partida.id
            )
            .all()
        )

        gastos_extra = (
            db.query(GastoExtraCotizado)
            .filter(
                GastoExtraCotizado.partida_id == partida.id
            )
            .all()
        )

        resultado_partidas.append({
            "id": partida.id,
            "descripcion": partida.descripcion,
            "cantidad": partida.cantidad,
            "precio_unitario": partida.precio_unitario,
            "total": partida.total,
            "materiales": materiales,
            "mano_obra": mano_obra,
            "gastos_extra": gastos_extra
        })

    return {
        "id": cotizacion.id,
        "rfq": cotizacion.rfq,
        "fecha": cotizacion.fecha,
        "cliente_id": cotizacion.cliente_id,
        "proyecto_id": cotizacion.proyecto_id,
        "usuario_id": cotizacion.usuario_id,
        "tiempo_entrega_estimado": cotizacion.tiempo_entrega_estimado,
        "estado": cotizacion.estado,
        "subtotal": cotizacion.subtotal,
        "iva": cotizacion.iva,
        "total": cotizacion.total,
        "fecha_creacion": cotizacion.fecha_creacion,
        "partidas": resultado_partidas
    }

def obtener_cotizaciones(db: Session, usuario: Usuario):
    query = db.query(CotizacionDB)
    if usuario and usuario.rol == "EMPLEADO":
        from app.models.usuario_proyecto import usuario_proyecto
        query = query.join(
            usuario_proyecto, 
            CotizacionDB.proyecto_id == usuario_proyecto.c.proyecto_id
        ).filter(
            usuario_proyecto.c.usuario_id == usuario.id
        )
    query = aplicar_filtro_test(query, CotizacionDB, usuario)
    return query.order_by(CotizacionDB.fecha_creacion.desc()).all()

def actualizar_cotizacion(
    db: Session,
    cotizacion_id: int,
    datos
):
    cotizacion = (
        db.query(CotizacionDB)
        .filter(CotizacionDB.id == cotizacion_id)
        .first()
    )

    if not cotizacion:
        return None

    # -------------------------
    # VALIDAR CLIENTE
    # -------------------------

    cliente = (
        db.query(Cliente)
        .filter(
            Cliente.id == datos.cliente_id,
            Cliente.activo == True
        )
        .first()
    )

    if not cliente:
        return None

    # -------------------------
    # VALIDAR PROYECTO
    # -------------------------

    proyecto = (
        db.query(Proyecto)
        .filter(
            Proyecto.id == datos.proyecto_id
        )
        .first()
    )

    if not proyecto:
        return None

    if proyecto.cliente_id != datos.cliente_id:
        return None

    # -------------------------
    # VALIDAR RFQ
    # -------------------------

    rfq_existente = (
        db.query(CotizacionDB)
        .filter(
            CotizacionDB.rfq == datos.rfq,
            CotizacionDB.id != cotizacion.id
        )
        .first()
    )

    if rfq_existente:
        raise ValueError(
            f"El RFQ '{datos.rfq}' ya existe."
        )

    try:
        # =========================
        # DATOS GENERALES
        # =========================

        cotizacion.rfq = datos.rfq
        cotizacion.fecha = datos.fecha
        cotizacion.cliente_id = datos.cliente_id
        cotizacion.proyecto_id = datos.proyecto_id
        cotizacion.tiempo_entrega_estimado = (
            datos.tiempo_entrega_estimado
        )

        # =========================
        # PARTIDAS ACTUALES
        # =========================

        partidas_actuales = (
            db.query(PartidaCotizacion)
            .filter(
                PartidaCotizacion.cotizacion_id == cotizacion.id
            )
            .all()
        )

        partidas_por_id = {
            partida.id: partida
            for partida in partidas_actuales
        }

        ids_partidas_recibidas = set()

        subtotal = Decimal("0.00")

        # =========================
        # PROCESAR PARTIDAS
        # =========================

        for partida_datos in datos.partidas:

            total_partida = (
                partida_datos.cantidad
                * partida_datos.precio_unitario
            )

            # -------------------------
            # PARTIDA EXISTENTE
            # -------------------------

            if partida_datos.id is not None:

                partida = partidas_por_id.get(
                    partida_datos.id
                )

                if not partida:
                    raise ValueError(
                        "Una partida no pertenece "
                        "a esta cotización."
                    )

                ids_partidas_recibidas.add(
                    partida.id
                )

                partida.descripcion = (
                    partida_datos.descripcion
                )

                partida.cantidad = (
                    partida_datos.cantidad
                )

                partida.precio_unitario = (
                    partida_datos.precio_unitario
                )

                partida.total = total_partida

            # -------------------------
            # PARTIDA NUEVA
            # -------------------------

            else:

                partida = PartidaCotizacion(
                    cotizacion_id=cotizacion.id,
                    descripcion=partida_datos.descripcion,
                    cantidad=partida_datos.cantidad,
                    precio_unitario=partida_datos.precio_unitario,
                    total=total_partida
                )

                db.add(partida)
                db.flush()

                ids_partidas_recibidas.add(
                    partida.id
                )

            # =========================
            # MATERIALES
            # =========================

            materiales_actuales = (
                db.query(MaterialCotizacion)
                .filter(
                    MaterialCotizacion.partida_id == partida.id
                )
                .all()
            )

            materiales_por_id = {
                material.id: material
                for material in materiales_actuales
            }

            ids_materiales_recibidos = set()

            for material_datos in partida_datos.materiales:

                total_material = (
                    material_datos.cantidad
                    * material_datos.precio_unitario
                )

                if material_datos.id is not None:

                    material = materiales_por_id.get(
                        material_datos.id
                    )

                    if not material:
                        raise ValueError(
                            "Un material no pertenece "
                            "a esta partida."
                        )

                    ids_materiales_recibidos.add(
                        material.id
                    )

                    material.material_id = (
                        material_datos.material_id
                    )

                    material.descripcion = (
                        material_datos.descripcion
                    )

                    material.cantidad = (
                        material_datos.cantidad
                    )

                    material.precio_unitario = (
                        material_datos.precio_unitario
                    )

                    material.total = total_material

                else:

                    material = MaterialCotizacion(
                        partida_id=partida.id,
                        material_id=material_datos.material_id,
                        descripcion=material_datos.descripcion,
                        cantidad=material_datos.cantidad,
                        precio_unitario=material_datos.precio_unitario,
                        total=total_material
                    )

                    db.add(material)

            # Eliminar materiales que ya no vienen
            for material in materiales_actuales:

                if material.id not in ids_materiales_recibidos:
                    db.delete(material)

            # =========================
            # MANO DE OBRA
            # =========================

            mano_obra_actual = (
                db.query(ManoObraCotizada)
                .filter(
                    ManoObraCotizada.partida_id == partida.id
                )
                .all()
            )

            mano_obra_por_id = {
                mano.id: mano
                for mano in mano_obra_actual
            }

            ids_mano_obra_recibidos = set()

            for mano_datos in partida_datos.mano_obra:

                total_mano = (
                    mano_datos.cantidad
                    * mano_datos.precio_unitario
                )

                if mano_datos.id is not None:

                    mano = mano_obra_por_id.get(
                        mano_datos.id
                    )

                    if not mano:
                        raise ValueError(
                            "Una mano de obra no pertenece "
                            "a esta partida."
                        )

                    ids_mano_obra_recibidos.add(
                        mano.id
                    )

                    mano.descripcion = (
                        mano_datos.descripcion
                    )

                    mano.cantidad = (
                        mano_datos.cantidad
                    )

                    mano.precio_unitario = (
                        mano_datos.precio_unitario
                    )

                    mano.total = total_mano

                else:

                    mano = ManoObraCotizada(
                        partida_id=partida.id,
                        descripcion=mano_datos.descripcion,
                        cantidad=mano_datos.cantidad,
                        precio_unitario=mano_datos.precio_unitario,
                        total=total_mano
                    )

                    db.add(mano)

            # Eliminar mano de obra que ya no viene
            for mano in mano_obra_actual:

                if mano.id not in ids_mano_obra_recibidos:
                    db.delete(mano)

            # =========================
            # GASTOS EXTRA
            # =========================

            gastos_actuales = (
                db.query(GastoExtraCotizado)
                .filter(
                    GastoExtraCotizado.partida_id == partida.id
                )
                .all()
            )

            gastos_por_id = {
                gasto.id: gasto
                for gasto in gastos_actuales
            }

            ids_gastos_recibidos = set()

            for gasto_datos in partida_datos.gastos_extra:

                total_gasto = (
                    gasto_datos.cantidad
                    * gasto_datos.precio_unitario
                )

                if gasto_datos.id is not None:

                    gasto = gastos_por_id.get(
                        gasto_datos.id
                    )

                    if not gasto:
                        raise ValueError(
                            "Un gasto extra no pertenece "
                            "a esta partida."
                        )

                    ids_gastos_recibidos.add(
                        gasto.id
                    )

                    gasto.descripcion = (
                        gasto_datos.descripcion
                    )

                    gasto.cantidad = (
                        gasto_datos.cantidad
                    )

                    gasto.precio_unitario = (
                        gasto_datos.precio_unitario
                    )

                    gasto.total = total_gasto

                else:

                    gasto = GastoExtraCotizado(
                        partida_id=partida.id,
                        descripcion=gasto_datos.descripcion,
                        cantidad=gasto_datos.cantidad,
                        precio_unitario=gasto_datos.precio_unitario,
                        total=total_gasto
                    )

                    db.add(gasto)

            # Eliminar gastos que ya no vienen
            for gasto in gastos_actuales:

                if gasto.id not in ids_gastos_recibidos:
                    db.delete(gasto)

            # =========================
            # SUBTOTAL
            # =========================

            subtotal += total_partida

        # =========================
        # ELIMINAR PARTIDAS
        # =========================

        for partida in partidas_actuales:

            if partida.id not in ids_partidas_recibidas:

                db.query(MaterialCotizacion).filter(
                    MaterialCotizacion.partida_id == partida.id
                ).delete(
                    synchronize_session=False
                )

                db.query(ManoObraCotizada).filter(
                    ManoObraCotizada.partida_id == partida.id
                ).delete(
                    synchronize_session=False
                )

                db.query(GastoExtraCotizado).filter(
                    GastoExtraCotizado.partida_id == partida.id
                ).delete(
                    synchronize_session=False
                )

                db.delete(partida)

        # =========================
        # TOTALES
        # =========================

        iva = subtotal * IVA
        total = subtotal + iva

        cotizacion.subtotal = subtotal
        cotizacion.iva = iva
        cotizacion.total = total

        db.commit()
        db.refresh(cotizacion)

        return cotizacion

    except Exception:
        db.rollback()
        raise

ESTADOS_COTIZACION = {
    "COTIZACION",
    "ENVIADA",
    "ACEPTADA",
    "RECHAZADA",
    "CANCELADA"
}

TRANSICIONES_COTIZACION = {
    "COTIZACION": {
        "ENVIADA",
        "CANCELADA"
    },
    "ENVIADA": {
        "ACEPTADA",
        "RECHAZADA",
        "CANCELADA"
    },
    "ACEPTADA": {
        "CANCELADA"
    },
    "RECHAZADA": {
        "COTIZACION"
    },
    "CANCELADA": set()
}


def actualizar_estado_cotizacion(
    db: Session,
    cotizacion_id: int,
    nuevo_estado: str
):
    cotizacion = (
        db.query(CotizacionDB)
        .filter(CotizacionDB.id == cotizacion_id)
        .first()
    )

    if not cotizacion:
        return None

    estado_actual = cotizacion.estado

    estados_permitidos = TRANSICIONES_COTIZACION.get(
        estado_actual,
        set()
    )

    if nuevo_estado not in estados_permitidos:
        raise ValueError(
            f"No se puede cambiar una cotización "
            f"de '{estado_actual}' a '{nuevo_estado}'."
        )

    cotizacion.estado = nuevo_estado

    db.commit()
    db.refresh(cotizacion)

    return cotizacion
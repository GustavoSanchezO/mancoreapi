from sqlalchemy.orm import Session

from app.models.impuesto_mensual import ImpuestoMensual


from app.models.usuario import Usuario
from app.services.seguridad_db import aplicar_filtro_test

def crear_impuesto_mensual(
    db: Session,
    año: int,
    mes: int,
    total_impuestos,
    usuario: Usuario
):
    query = db.query(ImpuestoMensual).filter(
        ImpuestoMensual.año == año,
        ImpuestoMensual.mes == mes
    )
    query = aplicar_filtro_test(query, ImpuestoMensual, usuario)
    impuesto_existente = query.first()

    if impuesto_existente:
        raise ValueError(
            "Ya existe un registro de impuestos para ese mes."
        )

    try:
        impuesto = ImpuestoMensual(
            año=año,
            mes=mes,
            total_impuestos=total_impuestos,
            usuario_id=usuario.id,
            es_test=usuario.es_test
        )

        db.add(impuesto)
        db.commit()
        db.refresh(impuesto)

        return impuesto

    except Exception:
        db.rollback()
        raise


def obtener_impuestos_mensuales(db: Session, usuario: Usuario):
    query = db.query(ImpuestoMensual).order_by(
        ImpuestoMensual.año.desc(),
        ImpuestoMensual.mes.desc()
    )
    query = aplicar_filtro_test(query, ImpuestoMensual, usuario)
    return query.all()


def obtener_impuesto_mensual(
    db: Session,
    impuesto_id: int,
    usuario: Usuario
):
    query = db.query(ImpuestoMensual).filter(ImpuestoMensual.id == impuesto_id)
    query = aplicar_filtro_test(query, ImpuestoMensual, usuario)
    return query.first()


def actualizar_impuesto_mensual(
    db: Session,
    impuesto_id: int,
    total_impuestos,
    usuario: Usuario
):
    impuesto = obtener_impuesto_mensual(db, impuesto_id, usuario)

    if not impuesto:
        return None

    try:
        impuesto.total_impuestos = total_impuestos

        db.commit()
        db.refresh(impuesto)

        return impuesto

    except Exception:
        db.rollback()
        raise
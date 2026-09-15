from sqlalchemy.orm import Session

from app.models.impuesto_mensual import ImpuestoMensual


def crear_impuesto_mensual(
    db: Session,
    año: int,
    mes: int,
    total_impuestos
):
    impuesto_existente = (
        db.query(ImpuestoMensual)
        .filter(
            ImpuestoMensual.año == año,
            ImpuestoMensual.mes == mes
        )
        .first()
    )

    if impuesto_existente:
        raise ValueError(
            "Ya existe un registro de impuestos para ese mes."
        )

    try:
        impuesto = ImpuestoMensual(
            año=año,
            mes=mes,
            total_impuestos=total_impuestos
        )

        db.add(impuesto)
        db.commit()
        db.refresh(impuesto)

        return impuesto

    except Exception:
        db.rollback()
        raise


def obtener_impuestos_mensuales(db: Session):
    return (
        db.query(ImpuestoMensual)
        .order_by(
            ImpuestoMensual.año.desc(),
            ImpuestoMensual.mes.desc()
        )
        .all()
    )


def obtener_impuesto_mensual(
    db: Session,
    impuesto_id: int
):
    return (
        db.query(ImpuestoMensual)
        .filter(ImpuestoMensual.id == impuesto_id)
        .first()
    )


def actualizar_impuesto_mensual(
    db: Session,
    impuesto_id: int,
    total_impuestos
):
    impuesto = (
        db.query(ImpuestoMensual)
        .filter(ImpuestoMensual.id == impuesto_id)
        .first()
    )

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
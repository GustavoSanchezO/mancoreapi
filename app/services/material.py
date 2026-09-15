from sqlalchemy.orm import Session

from app.models.material import Material


def crear_material(
    db: Session,
    nombre: str,
    unidad: str,
    codigo: str | None
):
    # Verificar que el código no esté utilizado
    if codigo:
        material_existente = (
            db.query(Material)
            .filter(Material.codigo == codigo)
            .first()
        )

        if material_existente:
            raise ValueError(
                "Ya existe un material con ese código."
            )

    try:
        material = Material(
            nombre=nombre,
            unidad=unidad,
            codigo=codigo,
            activo=True
        )

        db.add(material)
        db.commit()
        db.refresh(material)

        return material

    except Exception:
        db.rollback()
        raise


def obtener_materiales(db: Session):
    return (
        db.query(Material)
        .filter(Material.activo == True)
        .order_by(Material.id)
        .all()
    )


def obtener_material(
    db: Session,
    material_id: int
):
    return (
        db.query(Material)
        .filter(Material.id == material_id)
        .first()
    )


def actualizar_material(
    db: Session,
    material_id: int,
    nombre: str,
    unidad: str,
    codigo: str | None
):
    material = (
        db.query(Material)
        .filter(Material.id == material_id)
        .first()
    )

    if not material:
        return None

    # Verificar que el nuevo código no pertenezca
    # a otro material
    if codigo:
        material_existente = (
            db.query(Material)
            .filter(
                Material.codigo == codigo,
                Material.id != material_id
            )
            .first()
        )

        if material_existente:
            raise ValueError(
                "Ya existe otro material con ese código."
            )

    try:
        material.nombre = nombre
        material.unidad = unidad
        material.codigo = codigo

        db.commit()
        db.refresh(material)

        return material

    except Exception:
        db.rollback()
        raise


def desactivar_material(
    db: Session,
    material_id: int
):
    material = (
        db.query(Material)
        .filter(Material.id == material_id)
        .first()
    )

    if not material:
        return None

    try:
        material.activo = False

        db.commit()
        db.refresh(material)

        return material

    except Exception:
        db.rollback()
        raise
from sqlalchemy.orm import Session
from app.models.usuario import Usuario

from app.models.material import Material
from app.services.seguridad_db import aplicar_filtro_test


def crear_material(
    db: Session,
    nombre: str,
    unidad: str,
    codigo: str | None,
    usuario: Usuario
):
    # Verificar que el código no esté utilizado
    if codigo:
        query = db.query(Material).filter(Material.codigo == codigo)
        query = aplicar_filtro_test(query, Material, usuario)
        material_existente = query.first()

        if material_existente:
            raise ValueError(
                "Ya existe un material con ese código."
            )

    try:
        material = Material(
            nombre=nombre,
            unidad=unidad,
            codigo=codigo,
            activo=True,
            usuario_id=usuario.id,
            es_test=usuario.es_test
        )

        db.add(material)
        db.commit()
        db.refresh(material)

        return material

    except Exception:
        db.rollback()
        raise


def obtener_materiales(db: Session, usuario: Usuario):
    query = (
        db.query(Material)
        .filter(Material.activo == True)
        .order_by(Material.id)
    )
    query = aplicar_filtro_test(query, Material, usuario)
    return query.all()


def obtener_material(
    db: Session,
    material_id: int,
    usuario: Usuario
):
    query = (
        db.query(Material)
        .filter(Material.id == material_id)
    )
    query = aplicar_filtro_test(query, Material, usuario)
    return query.first()


def actualizar_material(
    db: Session,
    material_id: int,
    nombre: str,
    unidad: str,
    codigo: str | None,
    usuario: Usuario
):
    query = (
        db.query(Material)
        .filter(Material.id == material_id)
    )
    query = aplicar_filtro_test(query, Material, usuario)
    material = query.first()

    if not material:
        return None

    # Verificar que el nuevo código no pertenezca
    # a otro material
    if codigo:
        query_existente = (
            db.query(Material)
            .filter(
                Material.codigo == codigo,
                Material.id != material_id
            )
        )
        query_existente = aplicar_filtro_test(query_existente, Material, usuario)
        material_existente = query_existente.first()

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
    material_id: int,
    usuario: Usuario
):
    query = (
        db.query(Material)
        .filter(Material.id == material_id)
    )
    query = aplicar_filtro_test(query, Material, usuario)
    material = query.first()

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
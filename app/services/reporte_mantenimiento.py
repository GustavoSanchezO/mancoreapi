import os
import re
import unicodedata
from datetime import date, datetime
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session, joinedload

from app.models.anexo_fotografico import AnexoFotografico
from app.models.cliente import Cliente
from app.models.reporte_mantenimiento import (
    ReporteMantenimiento,
    ReporteMantenimientoActividad,
    ReporteMantenimientoAnexo,
    ReporteMantenimientoParte,
    ReporteMantenimientoParteImagen,
    ReporteMantenimientoSeccion,
)
from app.models.reporte_mantenimiento_schema import (
    ReporteMantenimientoActualizar,
    ReporteMantenimientoCrear,
)
from app.models.usuario import Usuario
from app.services.cotizacion import fecha_en_letras
from app.services.seguridad_db import aplicar_filtro_test
from app.services.usuario import registrar_cambio_test


NOMBRE_DOCUMENTO_DEFAULT = "Reporte de Mantenimiento"


def fecha_actual_mexico() -> date:
    try:
        return datetime.now(ZoneInfo("America/Mexico_City")).date()
    except Exception:
        return date.today()


def normalizar_nombre_documento(nombre_documento: str | None) -> str:
    limpio = (nombre_documento or NOMBRE_DOCUMENTO_DEFAULT).strip()
    return limpio or NOMBRE_DOCUMENTO_DEFAULT


def construir_titulo_documento(nombre_documento: str | None, folio: str) -> str:
    base = normalizar_nombre_documento(nombre_documento)
    folio_limpio = str(folio or "").strip()
    if not folio_limpio:
        return base

    if base.lower().endswith(folio_limpio.lower()):
        return base

    return f"{base} {folio_limpio}"


def construir_nombre_archivo_pdf(reporte: ReporteMantenimiento) -> str:
    titulo = construir_titulo_documento(reporte.nombre_documento, reporte.folio)
    if titulo.lower().endswith(".pdf"):
        titulo = titulo[:-4]

    nombre_ascii = unicodedata.normalize("NFKD", titulo)
    nombre_ascii = nombre_ascii.encode("ascii", "ignore").decode("ascii")
    nombre_ascii = re.sub(r"[^A-Za-z0-9\s-]+", " ", nombre_ascii)
    nombre_ascii = re.sub(r"\s+", " ", nombre_ascii).strip().strip(".")

    if not nombre_ascii:
        nombre_ascii = f"Reporte de Mantenimiento {reporte.folio}".strip()

    return f"{nombre_ascii}.pdf"


def _incrementar_folio(folio_actual: str) -> str:
    match = re.search(r"(\d+)(?!.*\d)", folio_actual)
    if not match:
        return f"{folio_actual.strip()}-1"

    numero = match.group(1)
    inicio, fin = match.span(1)
    siguiente = str(int(numero) + 1).zfill(len(numero))
    return f"{folio_actual[:inicio]}{siguiente}{folio_actual[fin:]}"


def obtener_siguiente_folio(db: Session, usuario: Usuario) -> str:
    query = db.query(ReporteMantenimiento)
    query = aplicar_filtro_test(query, ReporteMantenimiento, usuario)
    ultimo = query.order_by(ReporteMantenimiento.id.desc()).first()
    if not ultimo or not ultimo.folio:
        return "0001"
    return _incrementar_folio(ultimo.folio)


def _validar_cliente_activo(db: Session, cliente_id: int, usuario: Usuario) -> Cliente | None:
    query = db.query(Cliente).filter(
        Cliente.id == cliente_id,
        Cliente.activo == True,
    )
    query = aplicar_filtro_test(query, Cliente, usuario)
    return query.first()


def _limpiar_archivos_huerfanos(db: Session, rutas: list[str]) -> None:
    for ruta in set(rutas):
        if not ruta or not ruta.startswith("/static/anexos/"):
            continue
        en_cotizacion = db.query(AnexoFotografico.id).filter(AnexoFotografico.ruta_imagen == ruta).first()
        en_anexo_rep = db.query(ReporteMantenimientoAnexo.id).filter(ReporteMantenimientoAnexo.ruta_imagen == ruta).first()
        en_parte_rep = db.query(ReporteMantenimientoParteImagen.id).filter(ReporteMantenimientoParteImagen.ruta_imagen == ruta).first()
        if en_cotizacion or en_anexo_rep or en_parte_rep:
            continue

        file_name = ruta.split("/")[-1]
        file_path = os.path.join("app/static/anexos", file_name)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass


def _construir_hijos_reporte(reporte: ReporteMantenimiento, datos) -> None:
    for sec_idx, sec_datos in enumerate(datos.secciones, start=1):
        seccion = ReporteMantenimientoSeccion(
            orden=sec_datos.orden or sec_idx,
            titulo=sec_datos.titulo.strip(),
        )
        for act_idx, act_datos in enumerate(sec_datos.actividades, start=1):
            actividad = ReporteMantenimientoActividad(
                item_numero=act_datos.item_numero or act_idx,
                actividad=act_datos.actividad.strip(),
                estado=act_datos.estado.strip(),
                observaciones=act_datos.observaciones.strip() if act_datos.observaciones else None,
            )
            seccion.actividades.append(actividad)
        reporte.secciones.append(seccion)

    for idx, ruta in enumerate(datos.anexos_fotograficos or []):
        ruta_limpia = str(ruta).strip()
        if ruta_limpia:
            reporte.anexos.append(
                ReporteMantenimientoAnexo(
                    ruta_imagen=ruta_limpia,
                    orden=idx,
                )
            )

    for p_idx, parte_datos in enumerate(datos.partes_reemplazo or [], start=1):
        parte = ReporteMantenimientoParte(
            orden=parte_datos.orden or p_idx,
            descripcion=parte_datos.descripcion.strip(),
        )
        for img_idx, ruta in enumerate(parte_datos.imagenes or []):
            ruta_limpia = str(ruta).strip()
            if ruta_limpia:
                parte.imagenes.append(
                    ReporteMantenimientoParteImagen(
                        ruta_imagen=ruta_limpia,
                        orden=img_idx,
                    )
                )
        reporte.partes_reemplazo.append(parte)


def _serializar_reporte_detalle(reporte: ReporteMantenimiento) -> dict:
    return {
        "id": reporte.id,
        "folio": reporte.folio,
        "nombre_documento": reporte.nombre_documento,
        "titulo_documento": construir_titulo_documento(reporte.nombre_documento, reporte.folio),
        "fecha": reporte.fecha,
        "cliente_id": reporte.cliente_id,
        "cliente_nombre": reporte.cliente.nombre_empresa if reporte.cliente else "",
        "cliente_direccion": reporte.cliente.direccion if reporte.cliente else "",
        "usuario_id": reporte.usuario_id,
        "tipo_mantenimiento": reporte.tipo_mantenimiento,
        "unidad": reporte.unidad,
        "marca": reporte.marca,
        "modelo": reporte.modelo,
        "observaciones_generales": reporte.observaciones_generales,
        "fecha_creacion": reporte.fecha_creacion,
        "secciones": [
            {
                "id": sec.id,
                "orden": sec.orden,
                "titulo": sec.titulo,
                "actividades": [
                    {
                        "id": act.id,
                        "item_numero": act.item_numero,
                        "actividad": act.actividad,
                        "estado": act.estado,
                        "observaciones": act.observaciones,
                    }
                    for act in sorted(sec.actividades, key=lambda a: a.item_numero)
                ],
            }
            for sec in sorted(reporte.secciones, key=lambda s: s.orden)
        ],
        "anexos_fotograficos": [
            a.ruta_imagen for a in sorted(reporte.anexos, key=lambda a: a.orden)
        ],
        "partes_reemplazo": [
            {
                "id": p.id,
                "orden": p.orden,
                "descripcion": p.descripcion,
                "imagenes": [img.ruta_imagen for img in sorted(p.imagenes, key=lambda i: i.orden)],
            }
            for p in sorted(reporte.partes_reemplazo, key=lambda p: p.orden)
        ],
    }


def _cargar_reporte_por_id(db: Session, reporte_id: int, usuario: Usuario) -> ReporteMantenimiento | None:
    query = (
        db.query(ReporteMantenimiento)
        .options(
            joinedload(ReporteMantenimiento.cliente),
            joinedload(ReporteMantenimiento.secciones).joinedload(ReporteMantenimientoSeccion.actividades),
            joinedload(ReporteMantenimiento.anexos),
            joinedload(ReporteMantenimiento.partes_reemplazo).joinedload(ReporteMantenimientoParte.imagenes),
        )
        .filter(ReporteMantenimiento.id == reporte_id)
    )
    query = aplicar_filtro_test(query, ReporteMantenimiento, usuario)
    return query.first()


def crear_reporte_mantenimiento(
    db: Session,
    datos: ReporteMantenimientoCrear,
    usuario: Usuario,
) -> dict | None:
    cliente = _validar_cliente_activo(db, datos.cliente_id, usuario)
    if not cliente:
        return None

    folio_limpio = datos.folio.strip()
    if not folio_limpio:
        raise ValueError("El folio es obligatorio.")

    folio_existente = (
        db.query(ReporteMantenimiento.id)
        .filter(
            ReporteMantenimiento.folio == folio_limpio,
            ReporteMantenimiento.es_test == usuario.es_test,
        )
        .first()
    )
    if folio_existente:
        raise ValueError(f"Ya existe un reporte con el folio '{folio_limpio}'.")

    try:
        reporte = ReporteMantenimiento(
            folio=folio_limpio,
            nombre_documento=normalizar_nombre_documento(datos.nombre_documento),
            fecha=fecha_actual_mexico(),
            cliente_id=cliente.id,
            usuario_id=usuario.id,
            tipo_mantenimiento=datos.tipo_mantenimiento.strip(),
            unidad=datos.unidad.strip(),
            marca=datos.marca.strip(),
            modelo=datos.modelo.strip(),
            observaciones_generales=(
                datos.observaciones_generales.strip()
                if datos.observaciones_generales and datos.observaciones_generales.strip()
                else None
            ),
            es_test=usuario.es_test,
        )

        _construir_hijos_reporte(reporte, datos)

        db.add(reporte)
        db.commit()
        registrar_cambio_test(db, usuario)

        creado = _cargar_reporte_por_id(db, reporte.id, usuario)
        return _serializar_reporte_detalle(creado) if creado else None
    except Exception:
        db.rollback()
        raise


def obtener_reportes_mantenimiento(db: Session, usuario: Usuario) -> list[dict]:
    query = (
        db.query(ReporteMantenimiento)
        .options(
            joinedload(ReporteMantenimiento.cliente),
            joinedload(ReporteMantenimiento.secciones).joinedload(ReporteMantenimientoSeccion.actividades),
        )
    )
    query = aplicar_filtro_test(query, ReporteMantenimiento, usuario)
    reportes = query.order_by(ReporteMantenimiento.fecha.desc(), ReporteMantenimiento.id.desc()).all()

    resultado = []
    for rep in reportes:
        total_secciones = len(rep.secciones)
        total_actividades = sum(len(sec.actividades) for sec in rep.secciones)
        resultado.append(
            {
                "id": rep.id,
                "folio": rep.folio,
                "nombre_documento": rep.nombre_documento,
                "titulo_documento": construir_titulo_documento(rep.nombre_documento, rep.folio),
                "fecha": rep.fecha,
                "cliente_id": rep.cliente_id,
                "cliente_nombre": rep.cliente.nombre_empresa if rep.cliente else "",
                "usuario_id": rep.usuario_id,
                "tipo_mantenimiento": rep.tipo_mantenimiento,
                "unidad": rep.unidad,
                "marca": rep.marca,
                "modelo": rep.modelo,
                "fecha_creacion": rep.fecha_creacion,
                "total_secciones": total_secciones,
                "total_actividades": total_actividades,
            }
        )
    return resultado


def obtener_reporte_mantenimiento_detalle(
    db: Session,
    reporte_id: int,
    usuario: Usuario,
) -> dict | None:
    reporte = _cargar_reporte_por_id(db, reporte_id, usuario)
    if not reporte:
        return None
    return _serializar_reporte_detalle(reporte)


def obtener_reporte_para_pdf(
    db: Session,
    reporte_id: int,
    usuario: Usuario,
) -> dict | None:
    reporte = _cargar_reporte_por_id(db, reporte_id, usuario)
    if not reporte:
        return None

    detalle = _serializar_reporte_detalle(reporte)
    detalle["fecha_letras"] = fecha_en_letras(reporte.fecha)
    detalle["nombre_archivo_pdf"] = construir_nombre_archivo_pdf(reporte)
    return detalle


def actualizar_reporte_mantenimiento(
    db: Session,
    reporte_id: int,
    datos: ReporteMantenimientoActualizar,
    usuario: Usuario,
) -> dict | None:
    reporte = _cargar_reporte_por_id(db, reporte_id, usuario)
    if not reporte:
        return None

    cliente = _validar_cliente_activo(db, datos.cliente_id, usuario)
    if not cliente:
        raise ValueError("El cliente seleccionado no existe o está inactivo.")

    folio_limpio = datos.folio.strip()
    if not folio_limpio:
        raise ValueError("El folio es obligatorio.")

    folio_existente = (
        db.query(ReporteMantenimiento.id)
        .filter(
            ReporteMantenimiento.folio == folio_limpio,
            ReporteMantenimiento.es_test == usuario.es_test,
            ReporteMantenimiento.id != reporte.id,
        )
        .first()
    )
    if folio_existente:
        raise ValueError(f"Ya existe otro reporte con el folio '{folio_limpio}'.")

    rutas_anteriores = [a.ruta_imagen for a in reporte.anexos] + [
        img.ruta_imagen
        for p in reporte.partes_reemplazo
        for img in p.imagenes
    ]

    try:
        reporte.folio = folio_limpio
        reporte.nombre_documento = normalizar_nombre_documento(datos.nombre_documento)
        reporte.cliente_id = cliente.id
        reporte.tipo_mantenimiento = datos.tipo_mantenimiento.strip()
        reporte.unidad = datos.unidad.strip()
        reporte.marca = datos.marca.strip()
        reporte.modelo = datos.modelo.strip()
        reporte.observaciones_generales = (
            datos.observaciones_generales.strip()
            if datos.observaciones_generales and datos.observaciones_generales.strip()
            else None
        )

        reporte.secciones.clear()
        reporte.anexos.clear()
        reporte.partes_reemplazo.clear()
        db.flush()

        _construir_hijos_reporte(reporte, datos)

        db.commit()
        registrar_cambio_test(db, usuario)

        rutas_nuevas = {a.ruta_imagen for a in reporte.anexos} | {
            img.ruta_imagen
            for p in reporte.partes_reemplazo
            for img in p.imagenes
        }
        rutas_removidas = [r for r in rutas_anteriores if r not in rutas_nuevas]
        if rutas_removidas:
            _limpiar_archivos_huerfanos(db, rutas_removidas)

        actualizado = _cargar_reporte_por_id(db, reporte.id, usuario)
        return _serializar_reporte_detalle(actualizado) if actualizado else None
    except Exception:
        db.rollback()
        raise


def eliminar_reporte_mantenimiento(
    db: Session,
    reporte_id: int,
    usuario: Usuario,
) -> bool:
    reporte = _cargar_reporte_por_id(db, reporte_id, usuario)
    if not reporte:
        return False

    rutas = [a.ruta_imagen for a in reporte.anexos] + [
        img.ruta_imagen
        for p in reporte.partes_reemplazo
        for img in p.imagenes
    ]

    try:
        db.delete(reporte)
        db.commit()
        registrar_cambio_test(db, usuario)
        _limpiar_archivos_huerfanos(db, rutas)
        return True
    except Exception:
        db.rollback()
        raise

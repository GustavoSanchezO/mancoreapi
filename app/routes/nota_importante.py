from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from app.database.conexion import get_db
from app.models.nota_importante import NotaImportante
from app.models.usuario import Usuario
from app.auth.dependencias import require_admin
from app.services.seguridad_db import aplicar_filtro_test

router = APIRouter(prefix="/notas-importantes", tags=["Notas Importantes"])

class NotaImportanteCrear(BaseModel):
    nombre: str
    contenido: str

class NotaImportanteRespuesta(BaseModel):
    id: int
    nombre: str
    contenido: str

    class Config:
        from_attributes = True

@router.get("", response_model=List[NotaImportanteRespuesta])
def listar_notas_importantes(
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_admin)
):
    query = db.query(NotaImportante)
    query = aplicar_filtro_test(query, NotaImportante, admin)
    return query.order_by(NotaImportante.id.asc()).all()

@router.post("", response_model=NotaImportanteRespuesta)
def crear_nota_importante(
    nota: NotaImportanteCrear,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_admin)
):
    nueva_nota = NotaImportante(
        nombre=nota.nombre,
        contenido=nota.contenido,
        es_test=admin.es_test
    )
    db.add(nueva_nota)
    db.commit()
    db.refresh(nueva_nota)
    return nueva_nota

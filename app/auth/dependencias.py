from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database.dependencias import get_db
from app.models.usuario import Usuario


def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> Usuario:

    user_id = request.session.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="No has iniciado sesión."
        )

    usuario = (
        db.query(Usuario)
        .filter(Usuario.id == user_id)
        .first()
    )

    if not usuario:
        request.session.clear()

        raise HTTPException(
            status_code=401,
            detail="La sesión no es válida."
        )

    if not usuario.activo:
        request.session.clear()

        raise HTTPException(
            status_code=403,
            detail="Tu usuario está desactivado."
        )

    return usuario

def require_admin(
    usuario: Usuario = Depends(get_current_user)
) -> Usuario:

    if usuario.rol != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos de administrador."
        )

    return usuario
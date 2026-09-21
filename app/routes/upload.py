import os
import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends

from app.models.usuario import Usuario
from app.auth.dependencias import get_current_user

router = APIRouter(prefix="/upload", tags=["Uploads"])

UPLOAD_DIR = Path("app/static/anexos")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}

@router.post("/anexo")
async def upload_anexo(
    file: UploadFile = File(...),
    usuario: Usuario = Depends(get_current_user)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Formato de archivo no soportado. Usa JPG, JPEG o PNG.")

    unique_id = str(uuid.uuid4())
    new_filename = f"{unique_id}{ext}"
    
    file_path = UPLOAD_DIR / new_filename

    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error guardando el archivo: {str(e)}")

    # We return the absolute path for Weasyprint local resolution, or a relative path?
    # Actually, returning a relative URL path (like /static/anexos/filename) is best for the frontend,
    # and the backend can resolve it when making the PDF.
    return {"ruta_imagen": f"/static/anexos/{new_filename}"}

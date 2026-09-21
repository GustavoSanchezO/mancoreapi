from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.cotizacion import router as cotizacion_router
from app.routes.usuario import router as usuario_router
from app.routes.cliente import router as cliente_router
from app.routes.proyecto import router as proyecto_router
from app.routes.costo_material_real import router as costo_material_real_router
from app.routes.material import router as material_router
from app.routes.costo_mano_obra_real import (
    router as costo_mano_obra_real_router
)
from app.routes.costo_gasto_extra_real import router as costo_gasto_extra_real_router
from app.routes.impuesto_mensual import router as impuesto_mensual_router
from app.routes.dashboard import router as dashboard_router
from app.routes.nota_importante import router as nota_importante_router
from app.routes.upload import router as upload_router

import asyncio
from contextlib import asynccontextmanager
import os 
from dotenv import load_dotenv
from starlette.middleware.sessions import SessionMiddleware
from app.routes import venta

from app.database.dependencias import get_db
from app.services.usuario import purgar_usuarios_test_inactivos
from fastapi.staticfiles import StaticFiles


async def tareas_limpieza_test_loop():
    while True:
        try:
            await asyncio.sleep(60)
            db = next(get_db())
            try:
                purgar_usuarios_test_inactivos(db, minutos_inactividad=3)
            finally:
                db.close()
        except asyncio.CancelledError:
            break
        except Exception:
            pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(tareas_limpieza_test_loop())
    yield
    task.cancel()


load_dotenv()

app = FastAPI(
    title="Mancore API",
    description="API de Mancore",
    version="1.0.0",
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "https://mancore.mx",
        "https://administracion.mancore.mx"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET")
)


@app.get("/")
def root():
    return {
        "mensaje": "Mancore API funcionando",
        "version": "1.0.0"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }

#incluimos las rutas que definimos en app/routes/cotizacion.py, que es donde definimos la ruta /generar/cotizacion
app.include_router(cotizacion_router)

app.include_router(usuario_router)
app.include_router(cliente_router)
app.include_router(proyecto_router)
app.include_router(venta.router)
app.include_router(costo_material_real_router)
app.include_router(material_router)
app.include_router(costo_mano_obra_real_router)
app.include_router(costo_gasto_extra_real_router)
app.include_router(impuesto_mensual_router)
app.include_router(dashboard_router)
app.include_router(nota_importante_router)
app.include_router(upload_router)
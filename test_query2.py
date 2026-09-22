import sys
from app.database.conexion import SessionLocal
from app.models.usuario import Usuario
from app.models.proyecto import Proyecto

db = SessionLocal()
empleados = db.query(Usuario).filter(Usuario.rol == "EMPLEADO").all()
for emp in empleados:
    print(f"Empleado: {emp.nombre} (Test: {emp.es_test})")
    print(f" - Proyectos: {[p.id for p in emp.proyectos]}")

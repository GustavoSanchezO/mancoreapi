import sys
import os
from sqlalchemy.orm import Session
from app.database.conexion import SessionLocal
from app.services.proyecto import obtener_proyectos
from app.models.usuario import Usuario
from app.models.proyecto import Proyecto

db = SessionLocal()
empleado = db.query(Usuario).filter(Usuario.rol == "EMPLEADO", Usuario.es_test == False).first()
if not empleado:
    print("No real employee found")
    sys.exit(0)

print(f"Employee ID: {empleado.id}, Name: {empleado.nombre}")
print(f"Employee projects (from relationship): {[p.id for p in empleado.proyectos]}")

proyectos = obtener_proyectos(db, empleado)
print(f"Projects returned by obtener_proyectos: {[p.id for p in proyectos]}")

admin = db.query(Usuario).filter(Usuario.rol == "ADMIN", Usuario.es_test == False).first()
admin_proyectos = obtener_proyectos(db, admin)
print(f"Projects returned for Admin ID {admin.id}: {[p.id for p in admin_proyectos]}")

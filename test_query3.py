import sys
from app.database.conexion import SessionLocal
from app.models.usuario import Usuario
from app.services.proyecto import obtener_proyectos

db = SessionLocal()
emp = db.query(Usuario).filter(Usuario.nombre == "GUSTAVO SANCHEZ ORTIZ").first()
proyectos = obtener_proyectos(db, emp)
print(f"Projects returned by obtener_proyectos for {emp.nombre}: {[p.id for p in proyectos]}")

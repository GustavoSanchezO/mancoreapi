from app.models.usuario import Usuario

def aplicar_filtro_test(query, modelo, usuario: Usuario | None):
    """
    Aplica el filtro de aislamiento de datos basado en el modo test.
    """
    if not usuario:
        return query.filter(modelo.es_test == False)
        
    if usuario.es_test:
        if usuario.rol == "ADMIN":
            return query.filter(modelo.es_test == True)
        else:
            return query.filter(modelo.es_test == True, modelo.usuario_id == usuario.id)
    else:
        return query.filter(modelo.es_test == False)

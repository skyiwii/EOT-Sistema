def pedir_input(mensaje, cnx=None, opcional=False):
    valor = input(mensaje).strip()
    if valor.lower() in ("0", "cancelar", "exit"):
        print("Operación cancelada.")
        if cnx:
            cnx.rollback()
        return None
    if not valor and not opcional:
        print("El campo no puede estar vacío.")
        return pedir_input(mensaje, cnx, opcional)
    return valor


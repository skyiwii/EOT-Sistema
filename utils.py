from itertools import cycle
import re
from getpass import getpass

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



def pedir_contrasena(mensaje, cnx=None, opcional=False):
    """
    oculta lo que el usuario escribe.
    """
    valor = getpass(mensaje).strip()
    if valor.lower() in ("0", "cancelar", "exit"):
        print("Operación cancelada.")
        if cnx:
            cnx.rollback()
        return None
    if not valor and not opcional:
        print("El campo no puede estar vacío.")
        return pedir_contrasena(mensaje, cnx, opcional)
    return valor


def validar_rut(rut):
    rut = rut.upper().replace("-", "").replace(".", "")
    rut_aux = rut[:-1]
    dv = rut[-1:]

    if not rut_aux.isdigit() or not (1_000_000 <= int(rut_aux) <= 25_000_000):
        return False

    revertido = map(int, reversed(rut_aux))
    factors = cycle(range(2, 8))
    suma = sum(d * f for d, f in zip(revertido, factors))
    residuo = suma % 11

    if dv == 'K':
        return residuo == 1
    if dv == '0':
        return residuo == 11
    return residuo == 11 - int(dv)


def validar_email(email):
    regex_email = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}$'
    return bool(re.fullmatch(regex_email, email))

def validar_telefono(telefono):
    telefono = telefono.strip()
    
    # Si el número empieza sin +56, pero es celular, se agrega
    if re.fullmatch(r'^9\d{8}$', telefono):
        telefono = "+56" + telefono
    
    patrones = [
        r'^\+569\d{8}$',          # Celular
        r'^\+56[2-9]\d{7,8}$',    # Fijo
    ]
    
    for patron in patrones:
        if re.fullmatch(patron, telefono):
            return telefono  # Normalizado
    
    return False


def validar_contrasena(contrasena):
    regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    return bool(re.fullmatch(regex, contrasena))
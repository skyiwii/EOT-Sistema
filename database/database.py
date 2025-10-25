from __future__ import print_function
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import mysql.connector
from mysql.connector import errorcode
from clases.Rol import Rol
from clases.Direccion import Direccion
from clases.UsuarioSistema import UsuarioSistema
from clases.Departamento import Departamento
from clases.DetalleEmpleado import DetalleEmpleado
from clases.Proyecto import Proyecto
from clases.EmpleadoProyecto import EmpleadoProyecto
from clases.Informe import Informe
from clases.EmpleadoDepartamento import EmpleadoDepartamento
from clases.Administrador import Admin
from clases.Empleado import Empleado


def conectarBaseDeDatos():
    # Las credenciales menos la base de datos son valores predeterminados
    # Deben ir en otro archivo.py
    while True:
        try:
            usuario = input("Ingresa usuario de la base de datos: ")
            contraseña = input("Ingresa contraseña de la base de datos: ")
            host = input("Ingresa host de la base de datos: ")
            database = input("Ingresa nombre de la base de datos: ")

            cnx = mysql.connector.connect(user=usuario,
                                            password=contraseña,
                                            host=host,
                                            database=database,
                                            connection_timeout=5)
            
            cursor = cnx.cursor()
            
            print(f"Conexión creada a {database} en {host} con usuario {usuario}")

            return cnx, cursor, database
        
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print(f"Comprueba user o password")
                op = input("¿Desea seguir intentando conectarse (s/n)? ").lower()
                if op != "s" and op != "si":
                    print("Saliendo del programa...")
                    return None, None, None
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print(f"La base de datos {database} no existe")
                crear_base = input("¿Desea crearla (s/n)? ").lower()
                if crear_base in ('s', 'si'):
                    cnx = mysql.connector.connect(
                        user=usuario,
                        password=contraseña,
                        host=host,
                        connection_timeout=5
                    )

                    cursor = cnx.cursor()
                    crearBaseDeDatos(cursor, cnx, database)
                    cnx.database = database
                    return cnx, cursor, database
                else:
                    print("Saliendo del programa...")
                    return None, None, None
            else:
                print(err)
                op = input("¿Desea seguir intentando conectarse (s/n)? ").lower()
                if op != "s" and op != "si":
                    print("Saliendo del programa...")
                    return None, None, None

# funcion para crear la base de datos si es que no existe

def crearBaseDeDatos(cursor, cnx, DB_NAME):
    try:
        cursor.execute(
        f"CREATE DATABASE {DB_NAME} DEFAULT CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_general_ci'")
        print(f"Base de datos {DB_NAME} creada con codificación UTF8")
        cnx.database = DB_NAME
        cursor.execute(f"USE {DB_NAME}")
    except mysql.connector.Error as err:
        print(f"Error creando la base de datos: {err}")
        return None 


# función para crear las tablas

def crearTablas(cursor):
    tablas = [
        Rol, 
        Direccion, 
        UsuarioSistema, 
        DetalleEmpleado,
        Departamento,
        EmpleadoDepartamento,
        Proyecto, 
        EmpleadoProyecto, 
        Informe
    ]

    for tabla_clase in tablas:
        nombre_tabla = tabla_clase.__name__  # nombre de la tabla = nombre de la clase
        cursor.execute(f"SHOW TABLES LIKE '{nombre_tabla}'")
        existe = cursor.fetchone()

        if existe:
            print(f"Tabla {nombre_tabla} ya existente, prosiguiendo...")
            continue

        columnas_sql = ", ".join([f"`{col}` {tipo}" for col, tipo in tabla_clase.columnas.items()])

        # agregar constraints si existen
        if hasattr(tabla_clase, "constraints") and tabla_clase.constraints:
            columnas_sql += ", " + ", ".join(tabla_clase.constraints)

        sentencia = f"CREATE TABLE `{nombre_tabla}` ({columnas_sql}) ENGINE=InnoDB;"

        try:
            cursor.execute(sentencia)
            print(f"Tabla '{nombre_tabla}' creada correctamente.")
        except mysql.connector.Error as err:
            print(f"Error al crear tabla {nombre_tabla}: {err.msg}")

# esto iria despues en el menu cuando se desea salir del programa

def cerrarConexion(cnx, cursor):
    try:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()
    except mysql.connector.Error as err:
        print(f"Error al cerrar la conexión: {err}")
    finally:
        print("Conexión cerrada correctamente.")


def limpiarBaseDeDatos(cursor, cnx):
    tablas = [
        "Informe",
        "EmpleadoProyecto",
        "EmpleadoDepartamento",
        "DetalleEmpleado",
        "Proyecto",
        "Departamento",
        "UsuarioSistema",
        "Direccion",
        "Rol"
    ]
    
    try:
        print("Limpiando base de datos...")
        
        # Se desactiva la verificación de claves foráneas
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        
        for tabla in tablas:
            try:
                cursor.execute(f"TRUNCATE TABLE `{tabla}`;")
                print(f"Tabla '{tabla}' vaciada correctamente.")
            except mysql.connector.Error as err:
                print(f"No se pudo vaciar la tabla '{tabla}': {err}")
        
        # Se reactiva la verificación de claves foráneas
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        
        cnx.commit()
        print("\n¡Base de datos limpiada completamente!")
        
    except Exception as e:
        cnx.rollback()
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")  # Para asegurar que se reactive
        print(f"\nError al limpiar la base de datos: {e}")



# Crear autoscript para insertar un admin predeterminado

# Contraseñas deben ir encriptadas

def identificarse(cnx, cursor):
    while True:
        print("--- INICIE SESIÓN EN EL SISTEMA ---")
        usuario = input("Usuario: ").strip()
        contraseña = input("Contraseña: ").strip()
        
        try:
            consulta_usuario = """
                SELECT
                    U.id_UsuarioSistema,
                    U.Nombre,
                    U.Apellido,
                    U.RUT,
                    U.Email,
                    U.Telefono,
                    U.NombreUsuario,
                    U.Contraseña,
                    U.Direccion_idDireccion,
                    U.Rol_idRol,
                    R.tipo_Rol
                FROM UsuarioSistema U
                JOIN Rol R ON U.Rol_idRol = R.id_Rol
                WHERE U.NombreUsuario = %s
            """
            cursor.execute(consulta_usuario, (usuario,))
            resultado = cursor.fetchone()
            
            if resultado:
                (
                    id_usuario,
                    nombre,
                    apellido,
                    rut,
                    email,
                    telefono,
                    nombre_usuario_db,
                    contraseña_guardada,
                    id_direccion,
                    id_rol,
                    tipo_rol
                ) = resultado
                
                if contraseña == contraseña_guardada:
                    if tipo_rol.lower() == "admin":
                        usuario_obj = Admin(
                            Nombre=nombre,
                            Apellido=apellido,
                            RUT=rut,
                            Email=email,
                            Telefono=telefono,
                            NombreUsuario=nombre_usuario_db,
                            Contraseña=contraseña_guardada,
                            id_Direccion=id_direccion,
                            id_Rol=id_rol,
                            id_UsuarioSistema=id_usuario  # por si el __init__ lo usa
                        )
                        # Aseguramos el atributo aunque el __init__ lo ignore o lo nombre distinto
                        usuario_obj.id_UsuarioSistema = id_usuario
                        print(f"¡Bienvenido, {nombre}! Accediendo al menú de administrador...")
                        return usuario_obj, "admin"
                    else:
                        usuario_obj = Empleado(
                            Nombre=nombre,
                            Apellido=apellido,
                            RUT=rut,
                            Email=email,
                            Telefono=telefono,
                            NombreUsuario=nombre_usuario_db,
                            Contraseña=contraseña_guardada,
                            id_Direccion=id_direccion,
                            id_Rol=id_rol,
                            id_UsuarioSistema=id_usuario  # por si el __init__ lo usa
                        )
                        # Aseguramos el atributo aunque el __init__ lo ignore o lo nombre distinto
                        usuario_obj.id_UsuarioSistema = id_usuario
                        print(f"¡Bienvenido, {nombre}! Accediendo al menú de empleado...")
                        return usuario_obj, "empleado"
                else:
                    print("Contraseña incorrecta.")
            else:
                print(f"El usuario '{usuario}' no existe en el sistema.")
                
        except Exception as e:
            print(f"Ocurrió un error en la base de datos: {e}")
        
        opcion_usuario = input("¿Desea seguir intentando? (s/n): ").lower()
        if opcion_usuario not in ("s", "si"):
            return None, None

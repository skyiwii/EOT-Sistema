from __future__ import print_function
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import hashlib
from datetime import datetime
from getpass import getpass
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
from database.keys import credenciales
from clases.IndicadorEconomico import IndicadorEconomico     
from clases.ConsultaEconomica import ConsultaEconomica        

def conectarBaseDeDatos():
    # Las credenciales menos la base de datos son valores predeterminados
    # Deben ir en otro archivo.py
    while True:
        try:
            usuario = credenciales["user"]
            contraseña = credenciales["password"]
            host =  credenciales["host"]
            database = credenciales["database"]

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
        Informe,
        IndicadorEconomico,     
        ConsultaEconomica        
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
        "ConsultaEconomica",        
        "Informe",
        "EmpleadoProyecto",
        "EmpleadoDepartamento",
        "Proyecto",
        "Departamento",
        "DetalleEmpleado",
        "UsuarioSistema",
        "IndicadorEconomico",        
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
        contraseña = getpass("Contraseña: ").strip()
        
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

                # ---- Compatibilidad con SHA256 y texto plano ----
                hash_ingresado = hashlib.sha256(contraseña.encode()).hexdigest()
                contraseña_valida = (contraseña == contraseña_guardada) or (hash_ingresado == contraseña_guardada)

                if contraseña_valida:
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
                            id_UsuarioSistema=id_usuario
                        )
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
                            id_UsuarioSistema=id_usuario
                        )
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
        
# Tkinter

def autenticar_usuario(nombre_usuario, contraseña_plana, cursor):
    """
    Autentica a un usuario SIN usar input() ni print().
    Devuelve (objeto_usuario, rol) si las credenciales son correctas,
    o (None, None) si son inválidas.
    """
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
    cursor.execute(consulta_usuario, (nombre_usuario,))
    resultado = cursor.fetchone()

    if not resultado:
        # Usuario no existe
        return None, None

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

    # Mismo criterio que en identificarse: texto plano o SHA256
    hash_ingresado = hashlib.sha256(contraseña_plana.encode()).hexdigest()
    contraseña_valida = (contraseña_plana == contraseña_guardada) or (hash_ingresado == contraseña_guardada)

    if not contraseña_valida:
        return None, None

    # Instanciar Admin o Empleado igual que en identificarse, pero sin prints
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
            id_UsuarioSistema=id_usuario
        )
        usuario_obj.id_UsuarioSistema = id_usuario
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
            id_UsuarioSistema=id_usuario
        )
        usuario_obj.id_UsuarioSistema = id_usuario
        return usuario_obj, "empleado"


# crear datos que se inserten que son default en el sistema para
# iniciar sesion

def crear_admin(cnx, cursor):
    try:
        print("\n--- Creando administrador por defecto ---")

        # Roles base
        cursor.execute("SELECT COUNT(*) FROM Rol WHERE tipo_Rol = 'admin'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO Rol (tipo_Rol) VALUES ('admin')")
            print("Rol 'admin' creado.")
        cursor.execute("SELECT COUNT(*) FROM Rol WHERE tipo_Rol = 'empleado'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO Rol (tipo_Rol) VALUES ('empleado')")
            print("Rol 'empleado' creado.")

        # Dirección base
        cursor.execute("SELECT id_Direccion FROM Direccion WHERE Calle = 'Oficina Central'")
        direccion = cursor.fetchone()
        if direccion:
            id_direccion = direccion[0]
        else:
            cursor.execute("""
                INSERT INTO Direccion (Calle, Numero, Ciudad, Region, Pais, CodigoPostal)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, ('Oficina Central', 1, 'Santiago', 'RM', 'Chile', 8320000))
            id_direccion = cursor.lastrowid
            print("Dirección base creada.")

        # 3Crear admin si no existe
        cursor.execute("SELECT id_UsuarioSistema FROM UsuarioSistema WHERE NombreUsuario = 'admin'")
        admin_existe = cursor.fetchone()

        if admin_existe:
            print("Ya existe un administrador registrado.")
            return

        # Hash seguro de la contraseña
        contrasena_hash = hashlib.sha256("Admin123!".encode()).hexdigest()

        # Obtener id del rol admin
        cursor.execute("SELECT id_Rol FROM Rol WHERE tipo_Rol = 'admin'")
        id_rol_admin = cursor.fetchone()[0]

        # Insertar usuario administrador
        cursor.execute("""
            INSERT INTO UsuarioSistema 
            (Nombre, Apellido, RUT, Email, Telefono, NombreUsuario, Contraseña, Direccion_idDireccion, Rol_idRol)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, ("Administrador", "Principal", "11.111.111-1", "admin@sistema.cl", "999999999", "admin", contrasena_hash, id_direccion, id_rol_admin))
        
        cnx.commit()
        print("\n¡Administrador creado exitosamente!'\n")

    except Exception as e:
        cnx.rollback()
        print(f"Error al crear el administrador: {e}")

def crear_datos_ejemplo(cnx, cursor):
    """
    Carga un set mínimo de datos para que el sistema sea navegable:
    - Indicadores económicos base (UF, USD, USD_INTERCAMBIO, EUR, UTM, IPC, IPSA)
    - Roles (empleado si falta)
    - Direcciones base
    - Usuario empleado demo (hash SHA-256)
    - Departamentos
    - Proyecto demo
    - Asignaciones y detalle
    """
    try:
        print("--- Insertando datos de ejemplo ---")

        # 0) Indicadores económicos base
        #    (se insertan solo si NO existen para ese CodigoIndicador)
        indicadores_seed = [
            ("USD_CLP",             "Dólar observado",                         "USD",  "CLP",
             "Tipo de cambio dólar estadounidense / peso chileno"),

            ("USD_INTERCAMBIO_CLP", "Dólar acuerdo (intercambio)",            "USD",  "CLP",
             "Dólar acuerdo publicado por Banco Central / intercambio"),

            ("EUR_CLP",             "Euro",                                   "EUR",  "CLP",
             "Tipo de cambio euro / peso chileno"),

            ("UF_CLP",              "Unidad de Fomento (UF)",                 "UF",   "CLP",
             "Unidad de cuenta chilena indexada a la inflación"),

            ("UTM_CLP",             "Unidad Tributaria Mensual (UTM)",        "UTM",  "CLP",
             "Unidad tributaria mensual utilizada por el SII"),

            ("IPC",                 "Índice de Precios al Consumidor (IPC)",  "%",    "N/A",
             "Variación porcentual del IPC"),

            ("IVP",                 "Índice de Valor Promedio (IVP)",         "IVP",  "CLP",
             "Índice de valor promedio de instrumentos reajustables"),

            ("IPSA",                "IPSA (Índice de Precios Selectivo de Acciones)", "Puntos", "N/A",
             "Índice bursátil IPSA de la Bolsa de Santiago"),
        ]


        for cod, nom, base, cot, desc in indicadores_seed:
            cursor.execute(
                "SELECT id_IndicadorEconomico FROM IndicadorEconomico WHERE CodigoIndicador = %s",
                (cod,)
            )
            existe = cursor.fetchone()
            if existe:
                continue  # ya está en BD, no lo duplicamos

            cursor.execute(
                """
                INSERT INTO IndicadorEconomico
                    (CodigoIndicador, NombreIndicador, MonedaBase, MonedaCotizada, DescripcionIndicador)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (cod, nom, base, cot, desc)
            )

        print("Indicadores económicos base verificados/creados.")

        # 1) Roles
        cursor.execute("SELECT id_Rol FROM Rol WHERE tipo_Rol='empleado'")
        row = cursor.fetchone()
        if row:
            id_rol_emp = row[0]
        else:
            cursor.execute("INSERT INTO Rol (tipo_Rol) VALUES ('empleado')")
            id_rol_emp = cursor.lastrowid

        # 2) Direcciones
        direcciones_seed = [
            ("Av. Principal", 100, "Copiapó", "Atacama", "Chile", 1530000),
            ("Calle Secundaria", 55, "Copiapó", "Atacama", "Chile", 1530001),
        ]
        ids_dir = []
        for d in direcciones_seed:
            cursor.execute("""
                INSERT INTO Direccion (Calle, Numero, Ciudad, Region, Pais, CodigoPostal)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, d)
            ids_dir.append(cursor.lastrowid)
        print("Direcciones de ejemplo creadas o existentes.")

        # 3) Usuario empleado DEMO (si no existe)
        cursor.execute(
            "SELECT id_UsuarioSistema FROM UsuarioSistema WHERE NombreUsuario=%s",
            ("empleado1",)
        )
        row = cursor.fetchone()
        if row:
            id_emp = row[0]
        else:
            pwd_hash = hashlib.sha256("Empleado123!".encode()).hexdigest()
            cursor.execute("""
                INSERT INTO UsuarioSistema
                    (Nombre, Apellido, RUT, Email, Telefono, NombreUsuario,
                     Contraseña, Direccion_idDireccion, Rol_idRol)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, ("María", "Pérez", "13.456.789-K", "maria.perez@sistema.cl",
                  "+56922222222", "empleado1", pwd_hash, ids_dir[0], id_rol_emp))
            id_emp = cursor.lastrowid

            # DetalleEmpleado
            cursor.execute("""
                INSERT INTO DetalleEmpleado (Salario, TipoEmpleado, UsuarioSistema_idUsuarioSistema)
                VALUES (%s, %s, %s)
            """, (900000, "Analista", id_emp))

        # 4) Departamentos
        departamentos_seed = [
            ("Operaciones", "Operativo", "Coordina operaciones internas", ids_dir[1]),
            ("TI",          "Soporte",   "Soporte y desarrollo sistemas", ids_dir[0]),
        ]
        id_departamento_principal = None
        for (nom, tipo, desc, id_dir) in departamentos_seed:
            cursor.execute(
                "SELECT id_Departamento FROM Departamento WHERE NombreDepartamento=%s",
                (nom,)
            )
            dep = cursor.fetchone()
            if dep:
                dep_id = dep[0]
            else:
                cursor.execute("""
                    INSERT INTO Departamento
                        (NombreDepartamento, TipoDepartamento,
                         DescripcionDepartamento, Direccion_idDireccion)
                    VALUES (%s, %s, %s, %s)
                """, (nom, tipo, desc, id_dir))
                dep_id = cursor.lastrowid
            if id_departamento_principal is None:
                id_departamento_principal = dep_id

        # 5) Asignación empleado a depto (EmpleadoDepartamento)
        cursor.execute("""
            SELECT id_EmpleadoDepartamento
            FROM EmpleadoDepartamento
            WHERE UsuarioSistema_idUsuarioSistema=%s
              AND Departamento_idDepartamento=%s
        """, (id_emp, id_departamento_principal))
        ed = cursor.fetchone()
        if ed:
            id_ed = ed[0]
        else:
            cursor.execute("""
                INSERT INTO EmpleadoDepartamento
                    (Departamento_idDepartamento, UsuarioSistema_idUsuarioSistema)
                VALUES (%s, %s)
            """, (id_departamento_principal, id_emp))
            id_ed = cursor.lastrowid

        # 6) Proyecto demo
        cursor.execute(
            "SELECT id_Proyecto FROM Proyecto WHERE NombreProyecto=%s",
            ("Onboarding",)
        )
        pr = cursor.fetchone()
        if pr:
            id_proy = pr[0]
        else:
            cursor.execute("""
                INSERT INTO Proyecto (DescripcionProyecto, NombreProyecto)
                VALUES (%s, %s)
            """, ("Proyecto de inducción y pruebas", "Onboarding"))
            id_proy = cursor.lastrowid

        # 7) EmpleadoProyecto
        cursor.execute("""
            SELECT id_DetalleProyecto FROM EmpleadoProyecto
            WHERE EmpleadoDepartamento_idEmpleadoDepartamento=%s
              AND Proyecto_idProyecto=%s
        """, (id_ed, id_proy))
        ep = cursor.fetchone()
        if not ep:
            cursor.execute("""
                INSERT INTO EmpleadoProyecto
                    (CantidadHorasEmpleadoProyecto, DescripcionTareaProyecto,
                     EmpleadoDepartamento_idEmpleadoDepartamento, Proyecto_idProyecto)
                VALUES (%s, %s, %s, %s)
            """, (20, "Configuración inicial y documentación", id_ed, id_proy))

        cnx.commit()
        print("Datos de ejemplo cargados correctamente.")

    except Exception as e:
        try:
            cnx.rollback()
        except:
            pass
        print(f"Error al crear los datos de ejemplo: {e}")
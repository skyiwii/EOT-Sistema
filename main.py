from database.database import conectarBaseDeDatos, crearTablas, limpiarBaseDeDatos, cerrarConexion, identificarse

def conexion_total():
    print("Bienvenido. Primero crea tu conexión a la base de datos MySQL.")
    cnx, cursor, db_name = conectarBaseDeDatos()

    if cnx is None or cursor is None:
        print("No se pudo conectar a la base de datos. Programa terminado.")
        return

    crearTablas(cursor)

    usuario_obj, tipo_rol = identificarse(cnx, cursor)
    if not usuario_obj:
        print("Sesión terminada.")
        return

    if tipo_rol == "admin":
        menu_admin(cnx, cursor, usuario_obj)
    else:
        menu_empleado(cnx, cursor, usuario_obj)


# ===================== MENÚ ADMIN =====================

def menu_admin(cnx, cursor, usuario_obj):
    while True:
        print(f"\nADMIN: {usuario_obj.Nombre}")
        print("""
        ======== MENÚ PRINCIPAL ADMIN ========
        1. Gestión de Usuarios
        2. Gestión de Departamentos
        3. Gestión de Proyectos
        4. Asignaciones (Deptos / Proyectos)
        5. Generar Informes
        6. LIMPIAR BASE DE DATOS (PELIGRO)
        7. Cerrar sesión
        """)
        opcion = input("Elija una opción: ").strip()

        if opcion == "1":
            menu_crear_usuario(cnx, cursor, usuario_obj)
        elif opcion == "2":
            menu_crear_departamento(cnx, cursor, usuario_obj)
        elif opcion == "3":
            menu_crear_proyecto(cnx, cursor, usuario_obj)
        elif opcion == "4":
            menu_asignar_empleado(cnx, cursor, usuario_obj)
        elif opcion == "5":
            print("Aquí irán los informes más adelante.")
        elif opcion == "6":
            confirmar = input("Esto borrará TODOS los registros. ¿Seguro? (s/n): ").lower()
            if confirmar in ("s", "si"):
                limpiarBaseDeDatos(cursor, cnx)
                print("Base de datos limpiada.")
            else:
                print("Operación cancelada.")
        elif opcion == "7":
            cerrarConexion(cnx, cursor)
            print("Sesión finalizada.")
            break
        else:
            print("Opción no válida.")


# ============ SUBMENÚ: GESTIÓN DE USUARIOS ============

def menu_crear_usuario(cnx, cursor, usuario_obj):
    while True:
        print(f"\nADMIN: {usuario_obj.Nombre}")
        print("""
        ---- GESTIÓN DE USUARIOS ----
        1. Crear usuario
        2. Editar usuario
        3. Eliminar usuario
        4. Listar usuarios
        5. Buscar usuario específico
        6. Volver
        """)
        opcion = input("Elija una opción: ").strip()

        if opcion == "1":
            usuario_obj.crear_usuario(cnx, cursor)
        elif opcion == "2":
            usuario_obj.editar_usuario(cnx, cursor)
        elif opcion == "3":
            usuario_obj.eliminar_usuario(cnx, cursor, usuario_obj.id_UsuarioSistema)
        elif opcion == "4":
            usuario_obj.listar_usuarios(cursor)
        elif opcion == "5":
            usuario_obj.buscar_usuarios_especificos(cursor)
        elif opcion == "6":
            break
        else:
            print("Opción no válida.")


# ============ SUBMENÚ: GESTIÓN DE DEPARTAMENTOS ============

def menu_crear_departamento(cnx, cursor, usuario_obj):
    while True:
        print(f"\nADMIN: {usuario_obj.Nombre}")
        print("""
            ---- GESTIÓN DE DEPARTAMENTOS ----
            1. Crear departamento
            2. Editar departamento
            3. Eliminar departamento
            4. Listar departamentos
            5. Volver
            """)
        opcion = input("Elija una opción: ").strip()

        if opcion == "1":
            usuario_obj.crear_departamento(cnx, cursor)
        elif opcion == "2":
            usuario_obj.editar_departamento(cnx, cursor)
        elif opcion == "3":
            usuario_obj.eliminar_departamento(cnx, cursor)
        elif opcion == "4":
            usuario_obj.listar_departamentos(cursor)
        elif opcion == "5":
            break
        else:
            print("Opción no válida.")


# ============ SUBMENÚ: GESTIÓN DE PROYECTOS ============

def menu_crear_proyecto(cnx, cursor, usuario_obj):
    while True:
        print(f"\nADMIN: {usuario_obj.Nombre}")
        print("""
            ---- GESTIÓN DE PROYECTOS ----
            1. Crear proyecto
            2. Editar proyecto
            3. Eliminar proyecto
            4. Listar proyectos
            5. Volver
            """)
        opcion = input("Elija una opción: ").strip()

        if opcion == "1":
            usuario_obj.crear_proyecto(cnx, cursor)
        elif opcion == "2":
            usuario_obj.editar_proyecto(cnx, cursor)
        elif opcion == "3":
            usuario_obj.eliminar_proyecto(cnx, cursor)
        elif opcion == "4":
            usuario_obj.listar_proyectos(cursor)
        elif opcion == "5":
            break
        else:
            print("Opción no válida.")

# ============ SUBMENÚ: ASIGNACIONES (Departamento / Proyecto) ============

def menu_asignar_empleado(cnx, cursor, usuario_obj):
    while True:
        print(f"\nADMIN: {usuario_obj.Nombre}")
        print("""
        ---- ASIGNACIONES (Empleados - Depto / Proyecto) ----
        1. Asignar empleado a departamento
        2. Desasignar empleado de departamento
        3. Asignar empleado a proyecto
        4. Desasignar empleado de proyecto
        5. Ver detalle histórico (emp - depto / proyecto)
        6. Volver
        """)
        opcion = input("Elija una opción: ").strip()

        if opcion == "1":
            usuario_obj.asignar_empleado_a_departamento(cnx, cursor)
        elif opcion == "2":
            usuario_obj.eliminar_asignacion_empleado_departamento(cnx, cursor)
        elif opcion == "3":
            usuario_obj.asignar_empleado_a_proyecto(cnx, cursor)
        elif opcion == "4":
            usuario_obj.desasignar_empleado_a_proyecto(cnx, cursor)
        elif opcion == "5":
            usuario_obj.ver_detalle_empleado_proyecto(cursor)
        elif opcion == "6":
            break
        else:
            print("Opción no válida.")

# ============ MENÚ: Empleado ============

def menu_empleado(cnx, cursor, usuario_obj):
    while True:
        print(f"\nEMPLEADO: {usuario_obj.Nombre}")
        print("""
        ---- MENÚ EMPLEADO ----
        1. Ver mis datos personales completos
        2. Ver detalle laboral (contrato, salario, estado)
        3. Ver proyectos activos
        4. Ver historial de proyectos
        5. Ver mis compañeros de departamento
        6. Editar mis datos personales
        7. Cerrar sesión
        """)

        opcion = input("Elija una opción: ").strip()

        if opcion == "1":
            usuario_obj.ver_datos_personales(cursor)
        elif opcion == "2":
            usuario_obj.ver_detalle_laboral(cursor)
        elif opcion == "3":
            usuario_obj.ver_proyectos(cursor)
        elif opcion == "4":
            usuario_obj.ver_historial_proyectos(cursor)
        elif opcion == "5":
            usuario_obj.ver_compañeros(cursor)
        elif opcion == "6":
            usuario_obj.editar_datos_personales(cnx, cursor)
        elif opcion == "7":
            cerrarConexion(cnx, cursor)
            print("Cerrando sesión...")
            break
        else:
            print("Por favor elija una opción entre 1 y 7.")



conexion_total()
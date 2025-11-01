from database.database import (
    conectarBaseDeDatos,
    crearTablas,
    limpiarBaseDeDatos,
    cerrarConexion,
    identificarse,
    crear_admin,
    crear_datos_ejemplo
)


def conexion_total():
    print("Iniciando sistema de gestión...")
    cnx, cursor, db_name = conectarBaseDeDatos()

    if cnx is None or cursor is None:
        print("No se pudo conectar a la base de datos. Programa terminado.")
        return

    # --- Inicialización automática del sistema ---
    crearTablas(cursor)                # Crea las tablas si no existen
    crear_admin(cnx, cursor)           # Crea el admin base si no existe
    crear_datos_ejemplo(cnx, cursor)   # Carga datos iniciales mínimos

    # --- Inicio de sesión ---
    usuario_obj, tipo_rol = identificarse(cnx, cursor)
    if not usuario_obj:
        print("Sesión terminada.")
        return

    # --- Menús principales según rol ---
    if tipo_rol == "admin":
        menu_admin(cnx, cursor, usuario_obj)
    else:
        menu_empleado(cnx, cursor, usuario_obj)


# ===================== MENÚ ADMIN =====================

def menu_admin(cnx, cursor, usuario_obj):
    while True:
        print(f"\n=== ADMINISTRADOR: {usuario_obj.Nombre} ===")

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
            menu_informes(cnx, cursor, usuario_obj)
        elif opcion == "6":
            confirmar = input("Esto borrará TODOS los registros. ¿Seguro? (s/n): ").lower()
            if confirmar in ("s", "si"):
                limpiarBaseDeDatos(cursor, cnx)
                print("Base de datos limpiada.")
                input("\nPresione ENTER para volver al menú...")
            else:
                print("Operación cancelada.")
                input("\nPresione ENTER para volver al menú...")
        elif opcion == "7":
            cerrarConexion(cnx, cursor)
            print("Sesión finalizada.")
            break
        else:
            print("Opción no válida.")
            input("\nPresione ENTER para volver al menú...")


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
            input("\nPresione ENTER para volver al menú...")
        elif opcion == "2":
            usuario_obj.editar_usuario(cnx, cursor)
            input("\nPresione ENTER para volver al menú...")
        elif opcion == "3":
            usuario_obj.eliminar_usuario(cnx, cursor, usuario_obj.id_UsuarioSistema)
            input("\nPresione ENTER para volver al menú...")
        elif opcion == "4":
            usuario_obj.listar_usuarios(cursor)
            input("\nPresione ENTER para volver al menú...")
        elif opcion == "5":
            usuario_obj.buscar_usuarios_especificos(cursor)
            input("\nPresione ENTER para volver al menú...")
        elif opcion == "6":
            break
        else:
            print("Opción no válida.")
            input("\nPresione ENTER para volver al menú...")


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
            input("\nPresione ENTER para volver al menú...")
        elif opcion == "2":
            usuario_obj.editar_departamento(cnx, cursor)
            input("\nPresione ENTER para volver al menú...")
        elif opcion == "3":
            usuario_obj.eliminar_departamento(cnx, cursor)
            input("\nPresione ENTER para volver al menú...")
        elif opcion == "4":
            usuario_obj.listar_departamentos(cursor)
            input("\nPresione ENTER para volver al menú...")
        elif opcion == "5":
            break
        else:
            print("Opción no válida.")
            input("\nPresione ENTER para volver al menú...")


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
            input("\nPresione ENTER para volver al menú...")
        elif opcion == "2":
            usuario_obj.editar_proyecto(cnx, cursor)
            input("\nPresione ENTER para volver al menú...")
        elif opcion == "3":
            usuario_obj.eliminar_proyecto(cnx, cursor)
            input("\nPresione ENTER para volver al menú...")
        elif opcion == "4":
            usuario_obj.listar_proyectos(cursor)
            input("\nPresione ENTER para volver al menú...")
        elif opcion == "5":
            break
        else:
            print("Opción no válida.")
            input("\nPresione ENTER para volver al menú...")


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
            input("\nPresione ENTER para volver al menú...")
        elif opcion == "2":
            usuario_obj.eliminar_asignacion_empleado_departamento(cnx, cursor)
            input("\nPresione ENTER para volver al menú...")
        elif opcion == "3":
            usuario_obj.asignar_empleado_a_proyecto(cnx, cursor)
            input("\nPresione ENTER para volver al menú...")
        elif opcion == "4":
            usuario_obj.desasignar_empleado_a_proyecto(cnx, cursor)
            input("\nPresione ENTER para volver al menú...")
        elif opcion == "5":
            usuario_obj.ver_detalle_empleado_proyecto(cursor)
            input("\nPresione ENTER para volver al menú...")
        elif opcion == "6":
            break
        else:
            print("Opción no válida.")
            input("\nPresione ENTER para volver al menú...")


# ============ SUBMENÚ: Menu Informes ============

def menu_informes(cnx, cursor, usuario_obj):
    while True:
        print(f"\nADMIN: {usuario_obj.Nombre}")
        print("""
        ---- GESTIÓN DE INFORMES ----
        1. Generar informe de Departamentos/Proyectos
        2. Generar informe de Empleado
        3. Listar informes generados
        4. Ver detalle de un informe
        5. Eliminar informe
        6. Exportar Excel rápido (sin registrar)
        7. Volver
        """)
        opcion = input("Elija una opción: ").strip()

        if opcion == "1":
            usuario_obj.generar_informe_empleado_proyecto(cnx, cursor)
            input("\nPresione ENTER para volver al menú...")
        elif opcion == "2":
            usuario_obj.generar_informe_por_empleado(cnx, cursor)
            input("\nPresione ENTER para volver al menú...")
        elif opcion == "3":
            usuario_obj.listar_informes(cursor)
            input("\nPresione ENTER para volver al menú...")
        elif opcion == "4":
            usuario_obj.ver_detalle_informe(cursor)
            input("\nPresione ENTER para volver al menú...")
        elif opcion == "5":
            usuario_obj.eliminar_informe(cnx, cursor)
            input("\nPresione ENTER para volver al menú...")
        elif opcion == "6":
            usuario_obj.exportar_excel_empleado_proyecto(cursor)
            input("\nPresione ENTER para volver al menú...")
        elif opcion == "7":
            break
        else:
            print("Opción no válida.")
            input("\nPresione ENTER para volver al menú...")


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
        7. Cambiar nombre de usuario
        8. Cambiar contraseña
        9. Cerrar sesión
        """)
        opcion = input("Elija una opción: ").strip()

        if opcion == "1":
            usuario_obj.ver_datos_personales(cursor)
            input("\nPresione ENTER para volver al menú...")
        elif opcion == "2":
            usuario_obj.ver_detalle_laboral(cursor)
            input("\nPresione ENTER para volver al menú...")
        elif opcion == "3":
            usuario_obj.ver_proyectos(cursor)
            input("\nPresione ENTER para volver al menú...")
        elif opcion == "4":
            usuario_obj.ver_historial_proyectos(cursor)
            input("\nPresione ENTER para volver al menú...")
        elif opcion == "5":
            usuario_obj.ver_compañeros(cursor)
            input("\nPresione ENTER para volver al menú...")
        elif opcion == "6":
            usuario_obj.editar_datos_personales(cnx, cursor)
            input("\nPresione ENTER para volver al menú...")
        elif opcion == "7":
            usuario_obj.cambiar_nombre_usuario(cnx, cursor)
            input("\nPresione ENTER para volver al menú...")
        elif opcion == "8":
            usuario_obj.cambiar_contrasena(cnx, cursor)
            input("\nPresione ENTER para volver al menú...")
        elif opcion == "9":
            cerrarConexion(cnx, cursor)
            print("Cerrando sesión...")
            break
        else:
            print("Por favor elija una opción válida.")
            input("\nPresione ENTER para volver al menú...")


conexion_total()

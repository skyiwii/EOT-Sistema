from clases.UsuarioSistema import UsuarioSistema
from utils import pedir_input
from datetime import datetime

class Admin(UsuarioSistema):

    def __init__(self, Nombre, Apellido, RUT, Email, Telefono, NombreUsuario, Contraseña, id_Direccion, id_Rol, id_UsuarioSistema=None):
        super().__init__(Nombre, Apellido, RUT, Email, Telefono, NombreUsuario, Contraseña, id_Direccion, id_Rol, id_UsuarioSistema)
    
    
    # Creacion del Usuario: Admin/Empleado en sistema 
    # Falta rellenar datos hacia DetalleEmpleado y EmpleadoProyecto
    
    # Contraseñas deben ir encriptadas

    # Falta agregar la opción de cancelar operación para cada una de las funciones

    # --- CREAR USUARIOS: Listo ---

    def crear_usuario(self, cnx, cursor):
        try:
            nombre = pedir_input("Nombre (0 para cancelar): ", cnx)
            if nombre is None: return

            apellido = pedir_input("Apellido (0 para cancelar): ", cnx)
            if apellido is None: return

            rut = pedir_input("RUT (0 para cancelar): ", cnx)
            if rut is None: return

            email = pedir_input("Email (0 para cancelar): ", cnx)
            if email is None: return

            telefono = pedir_input("Teléfono (opcional, 0 para cancelar): ", cnx, opcional=True)
            if telefono is None: return

            nombre_usuario = pedir_input("Nombre de usuario (0 para cancelar): ", cnx)
            if nombre_usuario is None: return

            contrasena = pedir_input("Contraseña (0 para cancelar): ", cnx)
            if contrasena is None: return

            print("Ingrese la dirección del usuario:")
            calle = pedir_input("Calle (0 para cancelar): ", cnx)
            if calle is None: return

            while True:
                numero = pedir_input("Número (0 para cancelar): ", cnx)
                if numero is None: return
                try:
                    numero = int(numero)
                    break
                except ValueError:
                    print("Número inválido. Debe ser un número entero.")

            ciudad = pedir_input("Ciudad (0 para cancelar): ", cnx)
            if ciudad is None: return

            region = pedir_input("Región (0 para cancelar): ", cnx)
            if region is None: return

            pais = pedir_input("País (0 para cancelar): ", cnx)
            if pais is None: return

            while True:
                codigo_postal = pedir_input("Código Postal (0 para cancelar): ", cnx)
                if codigo_postal is None: return
                try:
                    codigo_postal = int(codigo_postal)
                    break
                except ValueError:
                    print("Código postal inválido. Debe ser un número entero.")

            cursor.execute("""
                INSERT INTO Direccion (Calle, Numero, Ciudad, Region, Pais, CodigoPostal)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (calle, numero, ciudad, region, pais, codigo_postal))
            cnx.commit()
            id_direccion = cursor.lastrowid

            while True:
                tipo_rol = pedir_input("Tipo de rol (admin/empleado, 0 para cancelar): ", cnx)
                if tipo_rol is None: return
                tipo_rol = tipo_rol.lower()
                if tipo_rol in ("admin", "empleado"):
                    break
                print("Opción inválida. Debe ser 'admin' o 'empleado'.")

            cursor.execute("INSERT INTO Rol (tipo_Rol) VALUES (%s)", (tipo_rol,))
            cnx.commit()
            id_rol = cursor.lastrowid

            cursor.execute("""
                INSERT INTO UsuarioSistema 
                (Nombre, Apellido, RUT, Email, Telefono, NombreUsuario, Contraseña, Direccion_idDireccion, Rol_idRol)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (nombre, apellido, rut, email, telefono, nombre_usuario, contrasena, id_direccion, id_rol))
            cnx.commit()
            id_usuario = cursor.lastrowid

            while True:
                salario = pedir_input("Salario (en CLP, 0 para cancelar): ", cnx)
                if salario is None: return
                try:
                    salario = int(salario)
                    if salario > 0:
                        break
                    print("El salario debe ser mayor a 0.")
                except ValueError:
                    print("Salario inválido. Debe ser un número entero.")

            tipo_empleado = pedir_input("Tipo de empleado (por defecto 'No especificado', 0 para cancelar): ", cnx, opcional=True)
            if tipo_empleado is None: return
            if not tipo_empleado:
                tipo_empleado = "No especificado"

            fecha_contrato = pedir_input("Fecha de contrato (YYYY-MM-DD, dejar vacío para actual, 0 para cancelar): ", cnx, opcional=True)
            if fecha_contrato is None: return

            if not fecha_contrato:
                cursor.execute("""
                    INSERT INTO DetalleEmpleado (Salario, TipoEmpleado, UsuarioSistema_idUsuarioSistema)
                    VALUES (%s, %s, %s)
                """, (salario, tipo_empleado, id_usuario))
            else:
                try:
                    datetime.strptime(fecha_contrato, "%Y-%m-%d")
                    cursor.execute("""
                        INSERT INTO DetalleEmpleado (FechaContrato, Salario, TipoEmpleado, UsuarioSistema_idUsuarioSistema)
                        VALUES (%s, %s, %s, %s)
                    """, (fecha_contrato, salario, tipo_empleado, id_usuario))
                except ValueError:
                    print("Formato de fecha inválido. Se usará fecha actual.")
                    cursor.execute("""
                        INSERT INTO DetalleEmpleado (Salario, TipoEmpleado, UsuarioSistema_idUsuarioSistema)
                        VALUES (%s, %s, %s)
                    """, (salario, tipo_empleado, id_usuario))

            cnx.commit()
            print(f"Usuario creado con ID: {id_usuario}, Rol: {tipo_rol}")

        except Exception as e:
            cnx.rollback()
            print(f"Ocurrió un error: {e}")

    def editar_usuario(self, cnx, cursor):
        try:
            print("\n--- EDITAR USUARIO ---")

            cursor.execute("""
                SELECT U.id_UsuarioSistema, U.Nombre, U.Apellido, U.NombreUsuario, R.tipo_Rol
                FROM UsuarioSistema U
                INNER JOIN Rol R ON U.Rol_idRol = R.id_Rol
                ORDER BY U.id_UsuarioSistema
            """)
            usuarios = cursor.fetchall()

            if not usuarios:
                print("No hay usuarios registrados.")
                return

            print("\n--- LISTADO DE USUARIOS ---")
            for u in usuarios:
                print(f"ID: {u[0]} - {u[1]} {u[2]} (Usuario: {u[3]}, Rol: {u[4]})")

            id_usuario = pedir_input("Ingrese el ID del usuario a editar (0 para cancelar): ", cnx)
            if id_usuario is None:
                return
            if not id_usuario.isdigit():
                print("ID inválido.")
                return
            id_usuario = int(id_usuario)

            cursor.execute("""
                SELECT U.Nombre, U.Apellido, U.RUT, U.Email, U.Telefono, U.NombreUsuario, U.Contraseña,
                    U.Direccion_idDireccion, U.Rol_idRol,
                    D.Calle, D.Numero, D.Ciudad, D.Region, D.Pais, D.CodigoPostal,
                    R.tipo_Rol,
                    E.id_DetalleEmpleado, E.FechaContrato, E.Salario, E.TipoEmpleado
                FROM UsuarioSistema U
                INNER JOIN Direccion D ON U.Direccion_idDireccion = D.id_Direccion
                INNER JOIN Rol R ON U.Rol_idRol = R.id_Rol
                LEFT JOIN DetalleEmpleado E ON U.id_UsuarioSistema = E.UsuarioSistema_idUsuarioSistema
                WHERE U.id_UsuarioSistema = %s
            """, (id_usuario,))
            usuario = cursor.fetchone()

            if not usuario:
                print("Usuario no encontrado.")
                return

            print("\n--- EDITAR DATOS DEL USUARIO ---")
            nombre = pedir_input(f"Nombre [{usuario[0]}] (0 para cancelar): ", cnx, opcional=True)
            if nombre is None: return
            nombre = nombre or usuario[0]

            apellido = pedir_input(f"Apellido [{usuario[1]}] (0 para cancelar): ", cnx, opcional=True)
            if apellido is None: return
            apellido = apellido or usuario[1]

            rut = pedir_input(f"RUT [{usuario[2]}] (0 para cancelar): ", cnx, opcional=True)
            if rut is None: return
            rut = rut or usuario[2]

            email = pedir_input(f"Email [{usuario[3]}] (0 para cancelar): ", cnx, opcional=True)
            if email is None: return
            email = email or usuario[3]

            telefono = pedir_input(f"Teléfono [{usuario[4]}] (0 para cancelar): ", cnx, opcional=True)
            if telefono is None: return
            telefono = telefono or usuario[4]

            nombre_usuario = pedir_input(f"Nombre de usuario [{usuario[5]}] (0 para cancelar): ", cnx, opcional=True)
            if nombre_usuario is None: return
            nombre_usuario = nombre_usuario or usuario[5]

            contrasena = pedir_input("Contraseña [dejar vacío para mantener, 0 para cancelar]: ", cnx, opcional=True)
            if contrasena is None: return
            contrasena = contrasena or usuario[6]

            print("\n--- EDITAR DIRECCIÓN ---")
            calle = pedir_input(f"Calle [{usuario[9]}] (0 para cancelar): ", cnx, opcional=True)
            if calle is None: return
            calle = calle or usuario[9]

            numero = pedir_input(f"Número [{usuario[10]}] (0 para cancelar): ", cnx, opcional=True)
            if numero is None: return
            numero = int(numero) if numero else usuario[10]

            ciudad = pedir_input(f"Ciudad [{usuario[11]}] (0 para cancelar): ", cnx, opcional=True)
            if ciudad is None: return
            ciudad = ciudad or usuario[11]

            region = pedir_input(f"Región [{usuario[12]}] (0 para cancelar): ", cnx, opcional=True)
            if region is None: return
            region = region or usuario[12]

            pais = pedir_input(f"País [{usuario[13]}] (0 para cancelar): ", cnx, opcional=True)
            if pais is None: return
            pais = pais or usuario[13]

            codigo_postal = pedir_input(f"Código Postal [{usuario[14]}] (0 para cancelar): ", cnx, opcional=True)
            if codigo_postal is None: return
            codigo_postal = int(codigo_postal) if codigo_postal else usuario[14]

            print(f"\nTipo de rol actual: {usuario[15]}")
            tipo_rol = pedir_input("Nuevo tipo de rol (admin/empleado, dejar vacío para mantener, 0 para cancelar): ", cnx, opcional=True)
            if tipo_rol is None: return
            tipo_rol = tipo_rol.lower() if tipo_rol else usuario[15]
            if tipo_rol not in ("admin", "empleado"):
                tipo_rol = usuario[15]

            cursor.execute("UPDATE Rol SET tipo_Rol = %s WHERE id_Rol = %s", (tipo_rol, usuario[8]))

            cursor.execute("""
                UPDATE Direccion
                SET Calle=%s, Numero=%s, Ciudad=%s, Region=%s, Pais=%s, CodigoPostal=%s
                WHERE id_Direccion=%s
            """, (calle, numero, ciudad, region, pais, codigo_postal, usuario[7]))

            cursor.execute("""
                UPDATE UsuarioSistema
                SET Nombre=%s, Apellido=%s, RUT=%s, Email=%s, Telefono=%s, NombreUsuario=%s, Contraseña=%s
                WHERE id_UsuarioSistema=%s
            """, (nombre, apellido, rut, email, telefono, nombre_usuario, contrasena, id_usuario))

            print("\n--- EDITAR DETALLE DE EMPLEADO ---")
            id_detalle = usuario[16]
            fecha_actual = usuario[17]
            salario_actual = usuario[18]
            tipo_actual = usuario[19]

            salario = pedir_input(f"Salario [{salario_actual}] (0 para cancelar): ", cnx, opcional=True)
            if salario is None: return
            if salario != "":
                try:
                    salario = int(salario)
                except ValueError:
                    print("Salario inválido. Se mantendrá el valor anterior.")
                    salario = salario_actual
            else:
                salario = salario_actual

            tipo_empleado = pedir_input(f"Tipo de empleado [{tipo_actual}] (0 para cancelar): ", cnx, opcional=True)
            if tipo_empleado is None: return
            tipo_empleado = tipo_empleado if tipo_empleado != "" else tipo_actual

            fecha_contrato = pedir_input(
                f"Fecha de contrato [{fecha_actual}] (YYYY-MM-DD, dejar vacío para mantener, 0 para cancelar): ",
                cnx, opcional=True
            )
            if fecha_contrato is None: return

            fecha_final = fecha_actual
            if fecha_contrato:
                import datetime
                try:
                    datetime.datetime.strptime(fecha_contrato, "%Y-%m-%d")
                    fecha_final = fecha_contrato
                except ValueError:
                    print("Formato de fecha inválido. No se modificó la fecha.")

            if id_detalle is None:
                cursor.execute("""
                    INSERT INTO DetalleEmpleado (UsuarioSistema_idUsuarioSistema, FechaContrato, Salario, TipoEmpleado)
                    VALUES (%s, %s, %s, %s)
                """, (id_usuario, fecha_final, salario, tipo_empleado))
            else:
                if fecha_final is not None:
                    cursor.execute("""
                        UPDATE DetalleEmpleado
                        SET FechaContrato=%s, Salario=%s, TipoEmpleado=%s
                        WHERE id_DetalleEmpleado=%s
                    """, (fecha_final, salario, tipo_empleado, id_detalle))
                else:
                    cursor.execute("""
                        UPDATE DetalleEmpleado
                        SET Salario=%s, TipoEmpleado=%s
                        WHERE id_DetalleEmpleado=%s
                    """, (salario, tipo_empleado, id_detalle))

            cnx.commit()
            print("Usuario y detalle actualizados correctamente.")

        except Exception as e:
            try:
                cnx.rollback()
            except Exception:
                pass
            print(f"Ocurrió un error: {e}")

    def eliminar_usuario(self, cnx, cursor, current_user_id):
        try:
            while True:
                usuario_a_eliminar = pedir_input("Ingrese el ID del usuario a eliminar (0 para cancelar): ", cnx)
                if usuario_a_eliminar is None:
                    return
                if usuario_a_eliminar.isdigit():
                    usuario_a_eliminar = int(usuario_a_eliminar)
                    break
                print("Error: Debe ingresar un número entero válido.")

            cursor.execute("""
                SELECT U.id_UsuarioSistema, U.NombreUsuario, U.Direccion_idDireccion, U.Rol_idRol, R.tipo_Rol
                FROM UsuarioSistema U
                JOIN Rol R ON U.Rol_idRol = R.id_Rol
                WHERE U.id_UsuarioSistema = %s
            """, (usuario_a_eliminar,))
            usuario = cursor.fetchone()

            if not usuario:
                print(f"No se encontró ningún usuario con ID: {usuario_a_eliminar}")
                return

            id_usuario, nombre_usuario, id_direccion, id_rol, tipo_rol = usuario

            if id_usuario == current_user_id:
                print("Acción prohibida: no puedes eliminar el usuario con el que estás autenticado.")
                return

            if tipo_rol.lower() == "admin":
                cursor.execute("""
                    SELECT COUNT(*) FROM UsuarioSistema U
                    JOIN Rol R ON U.Rol_idRol = R.id_Rol
                    WHERE R.tipo_Rol = 'admin'
                """)
                cantidad_admins = cursor.fetchone()[0]
                if cantidad_admins <= 1:
                    print("Acción prohibida: no se puede eliminar al último usuario con rol 'admin'.")
                    return

            print(f"Usuario a eliminar: ID={id_usuario}, NombreUsuario='{nombre_usuario}', Rol='{tipo_rol}'")
            print("ADVERTENCIA: Esta acción es irreversible y borrará todos los datos dependientes.")
            confirmacion = pedir_input("Si está seguro, escriba DELETE (mayúsculas) para confirmar o 0 para cancelar: ", cnx)
            if confirmacion is None or confirmacion != "DELETE":
                print("Operación cancelada.")
                cnx.rollback()
                return

            cursor.execute("DELETE FROM UsuarioSistema WHERE id_UsuarioSistema = %s", (id_usuario,))
            cnx.commit()
            print(f"Usuario '{nombre_usuario}' (ID {id_usuario}) eliminado correctamente.")

            if id_direccion is not None:
                cursor.execute("SELECT COUNT(*) FROM UsuarioSistema WHERE Direccion_idDireccion = %s", (id_direccion,))
                direccion_en_uso = cursor.fetchone()[0]
                if direccion_en_uso == 0:
                    cursor.execute("DELETE FROM Direccion WHERE id_Direccion = %s", (id_direccion,))
                    cnx.commit()
                    print(f"Dirección asociada (ID {id_direccion}) eliminada correctamente.")

            if id_rol is not None:
                cursor.execute("SELECT COUNT(*) FROM UsuarioSistema WHERE Rol_idRol = %s", (id_rol,))
                rol_en_uso = cursor.fetchone()[0]
                if rol_en_uso == 0:
                    cursor.execute("DELETE FROM Rol WHERE id_Rol = %s", (id_rol,))
                    cnx.commit()
                    print(f"Rol asociado (ID {id_rol}) eliminado correctamente.")

        except Exception as err:
            try:
                cnx.rollback()
            except Exception:
                pass
            print(f"Se produjo un error al eliminar el usuario: {err}")

    def listar_usuarios(self, cursor):
        try:
            cursor.execute("""
                SELECT U.id_UsuarioSistema, U.Nombre, U.Apellido, U.RUT, U.Email, U.Telefono,
                    U.NombreUsuario, R.tipo_Rol,
                    D.Calle, D.Numero, D.Ciudad, D.Region, D.Pais, D.CodigoPostal,
                    E.FechaContrato, E.Salario, E.TipoEmpleado
                FROM UsuarioSistema U
                INNER JOIN Rol R ON U.Rol_idRol = R.id_Rol
                INNER JOIN Direccion D ON U.Direccion_idDireccion = D.id_Direccion
                LEFT JOIN DetalleEmpleado E ON U.id_UsuarioSistema = E.UsuarioSistema_idUsuarioSistema
                ORDER BY U.id_UsuarioSistema
            """)
            usuarios = cursor.fetchall()

            if not usuarios:
                print("No hay usuarios registrados.")
                return

            pagina = 0
            por_pagina = 5
            total = len(usuarios)

            while True:
                inicio = pagina * por_pagina
                fin = inicio + por_pagina
                pag_usuarios = usuarios[inicio:fin]

                if not pag_usuarios:
                    print("No hay más usuarios para mostrar.")
                    break

                print(f"\n--- PÁGINA {pagina + 1} ---")
                for u in pag_usuarios:
                    print(f"""
                        ID: {u[0]} - {u[1]} {u[2]} (Usuario: {u[6]}, Rol: {u[7]})
                        RUT: {u[3]}, Email: {u[4]}, Teléfono: {u[5]}
                        Dirección: {u[8]} {u[9]}, {u[10]}, {u[11]}, {u[12]}, CP: {u[13]}
                        Detalle Empleado → Fecha Contrato: {u[14]}, Salario: {u[15]}, Tipo: {u[16]}
                        ----------------------------------------
                    """)

                if fin >= total:
                    print("Fin del listado de usuarios.")
                    break

                continuar = pedir_input("¿Ver siguiente página? (s/n, 0 para cancelar): ")
                if continuar is None or continuar.lower() != 's':
                    print("Operación cancelada o fin del listado.")
                    break

                pagina += 1

        except Exception as e:
            print(f"Ocurrió un error al listar usuarios: {e}")

    def buscar_usuarios_especificos(self, cursor):
        print("\n--- Buscar Usuarios Específicos ---")
        print("""
        ¿Por qué desea buscar?
        1. ID de usuario
        2. Nombre de usuario
        3. Correo electrónico
        4. Teléfono
        0. Cancelar
        """)

        opcion = pedir_input("Seleccione una opción: ")
        if opcion is None or opcion == "0":
            print("Operación cancelada.")
            return

        filtro = ""
        valor = None

        if opcion == "1":
            id_usuario = pedir_input("Ingrese el ID del usuario (0 para cancelar): ")
            if id_usuario is None: return
            if not id_usuario.isdigit():
                print("Error: El ID debe ser un número entero.")
                return
            filtro = "U.id_UsuarioSistema = %s"
            valor = (int(id_usuario),)

        elif opcion == "2":
            nombre = pedir_input("Ingrese el nombre de usuario (o parte del nombre, 0 para cancelar): ")
            if nombre is None: return
            filtro = "U.NombreUsuario LIKE %s"
            valor = (f"%{nombre}%",)

        elif opcion == "3":
            correo = pedir_input("Ingrese el correo (o parte del correo, 0 para cancelar): ")
            if correo is None: return
            filtro = "U.Email LIKE %s"
            valor = (f"%{correo}%",)

        elif opcion == "4":
            telefono = pedir_input("Ingrese el teléfono (o parte del teléfono, 0 para cancelar): ")
            if telefono is None: return
            filtro = "U.Telefono LIKE %s"
            valor = (f"%{telefono}%",)

        else:
            print("Opción no válida.")
            return

        try:
            cursor.execute(f"""
                SELECT 
                    U.id_UsuarioSistema, U.Nombre, U.Apellido, U.RUT, U.Email, U.Telefono, 
                    U.NombreUsuario, R.tipo_Rol,
                    D.Calle, D.Numero, D.Ciudad, D.Region, D.Pais, D.CodigoPostal,
                    E.FechaContrato, E.Salario, E.TipoEmpleado
                FROM UsuarioSistema U
                INNER JOIN Rol R ON U.Rol_idRol = R.id_Rol
                INNER JOIN Direccion D ON U.Direccion_idDireccion = D.id_Direccion
                LEFT JOIN DetalleEmpleado E ON U.id_UsuarioSistema = E.UsuarioSistema_idUsuarioSistema
                WHERE {filtro}
            """, valor)

            resultados = cursor.fetchall()

            if not resultados:
                print("No se encontraron usuarios que coincidan con la búsqueda.")
                return

            print("\n--- Resultados encontrados ---")
            for u in resultados:
                print(f"""
                        ID: {u[0]} - {u[1]} {u[2]} (Usuario: {u[6]}, Rol: {u[7]})
                        RUT: {u[3]}, Email: {u[4]}, Teléfono: {u[5]}
                        Dirección: {u[8]} {u[9]}, {u[10]}, {u[11]}, {u[12]}, CP: {u[13]}
                        Detalle Empleado → Fecha Contrato: {u[14]}, Salario: {u[15]}, Tipo: {u[16]}
                        ----------------------------------------
                        """)

        except Exception as err:
            print(f"Error al buscar usuarios: {err}")

    # --- DEPARTAMENTOS: Listo ---

    def crear_departamento(self, cnx, cursor):
        try:
            print("\n--- CREAR DEPARTAMENTO ---")

            # Nombre (obligatorio)
            while True:
                nombre = pedir_input("Nombre del departamento (0 para cancelar): ", cnx)
                if nombre is None:
                    return
                if not nombre:
                    print("El nombre no puede estar vacío.")
                    continue
                break

            # Tipo (obligatorio)
            while True:
                tipo = pedir_input("Tipo de departamento (0 para cancelar): ", cnx)
                if tipo is None:
                    return
                if not tipo:
                    print("El tipo no puede estar vacío.")
                    continue
                break

            # Descripción (opcional)
            descripcion = pedir_input("Descripción del departamento (opcional, 0 para cancelar): ", cnx, opcional=True)
            if descripcion is None:
                return

            # Validación opcional de Direccion_idDireccion si aplica
            # (solo si quieres garantizar que existe la dirección en BD)
            # cursor.execute("SELECT 1 FROM Direccion WHERE id_Direccion = %s", (self.Direccion_idDireccion,))
            # if cursor.fetchone() is None:
            #     print("La dirección asociada al administrador no existe.")
            #     return

            cursor.execute("""
                INSERT INTO Departamento (NombreDepartamento, TipoDepartamento, DescripcionDepartamento, Direccion_idDireccion)
                VALUES (%s, %s, %s, %s)
            """, (nombre, tipo, descripcion, getattr(self, "Direccion_idDireccion", None)))

            cnx.commit()
            id_departamento = cursor.lastrowid
            print(f"Departamento creado con ID: {id_departamento}, Nombre: {nombre}, Tipo: {tipo}")

        except Exception as e:
            try:
                cnx.rollback()
            except Exception:
                pass
            print(f"Ocurrió un error al crear el departamento: {e}")

    def listar_departamentos(self, cursor):
        try:
            print("\n--- LISTADO DE DEPARTAMENTOS ---")

            cursor.execute("""
                SELECT id_Departamento, NombreDepartamento, TipoDepartamento, DescripcionDepartamento
                FROM Departamento
                ORDER BY id_Departamento
            """)
            departamentos = cursor.fetchall()

            if not departamentos:
                print("No hay departamentos registrados.")
                return

            cantidad_por_pagina = 5
            total = len(departamentos)
            pagina = 0

            while True:
                inicio = pagina * cantidad_por_pagina
                fin = inicio + cantidad_por_pagina
                bloque = departamentos[inicio:fin]

                for dep in bloque:
                    print(f"""
                            ID: {dep[0]}
                            Nombre: {dep[1]}
                            Tipo: {dep[2]}
                            Descripción: {dep[3] if dep[3] else "(sin descripción)"}
                            ------------------------------
                            """.rstrip())

                if fin >= total:
                    print("No hay más departamentos.")
                    break

                # Control de paginación con posibilidad de cancelar
                avanzar = pedir_input("Presione ENTER para ver los siguientes (0 para cancelar): ", opcional=True)
                if avanzar is None:
                    # pedir_input ya imprimió "Operación cancelada."
                    return
                # Cualquier entrada distinta de None continúa
                pagina += 1

        except Exception as e:
            print(f"Ocurrió un error al listar departamentos: {e}")

    def editar_departamento(self, cnx, cursor):
        try:
            print("\n--- EDITAR DEPARTAMENTO ---")

            # Listar existentes (vista rápida)
            cursor.execute("SELECT id_Departamento, NombreDepartamento, TipoDepartamento FROM Departamento ORDER BY id_Departamento")
            departamentos = cursor.fetchall()
            if not departamentos:
                print("No hay departamentos registrados.")
                return

            print("\nDepartamentos existentes:")
            for dep in departamentos:
                print(f"  {dep[0]} - {dep[1]} ({dep[2]})")

            # Seleccionar ID
            while True:
                id_dep = pedir_input("Ingrese el ID del departamento a editar (0 para cancelar): ", cnx)
                if id_dep is None:
                    return
                if not id_dep.isdigit():
                    print("Debe ingresar un número válido.")
                    continue
                id_dep = int(id_dep)

                cursor.execute("""
                    SELECT id_Departamento, NombreDepartamento, TipoDepartamento, DescripcionDepartamento
                    FROM Departamento
                    WHERE id_Departamento = %s
                """, (id_dep,))
                depto = cursor.fetchone()
                if not depto:
                    print("ID de departamento no existe. Intente nuevamente.")
                    continue
                break

            # Pedir nuevos datos (vacío => mantiene)
            actual_nombre, actual_tipo, actual_desc = depto[1], depto[2], depto[3]

            nuevo_nombre = pedir_input(f"Nuevo nombre (actual: {actual_nombre}) [ENTER para mantener, 0 para cancelar]: ",
                                    cnx, opcional=True)
            if nuevo_nombre is None:
                return
            if nuevo_nombre == "":
                nuevo_nombre = actual_nombre

            nuevo_tipo = pedir_input(f"Nuevo tipo (actual: {actual_tipo}) [ENTER para mantener, 0 para cancelar]: ",
                                    cnx, opcional=True)
            if nuevo_tipo is None:
                return
            if nuevo_tipo == "":
                nuevo_tipo = actual_tipo

            nueva_descripcion = pedir_input(
                f"Nueva descripción (actual: {actual_desc if actual_desc else '(sin descripción)'}) "
                f"[ENTER para mantener, 0 para cancelar]: ",
                cnx, opcional=True
            )
            if nueva_descripcion is None:
                return
            if nueva_descripcion == "":
                nueva_descripcion = actual_desc

            # Si no hubo cambios, evitar UPDATE innecesario
            if (nuevo_nombre == actual_nombre
                    and nuevo_tipo == actual_tipo
                    and nueva_descripcion == actual_desc):
                print("No se realizaron cambios.")
                return

            # Ejecutar actualización
            cursor.execute("""
                UPDATE Departamento
                SET NombreDepartamento = %s,
                    TipoDepartamento = %s,
                    DescripcionDepartamento = %s
                WHERE id_Departamento = %s
            """, (nuevo_nombre, nuevo_tipo, nueva_descripcion, id_dep))
            cnx.commit()

            print(f"Departamento ID {id_dep} actualizado correctamente.")

        except Exception as e:
            try:
                cnx.rollback()
            except Exception:
                pass
            print(f"Ocurrió un error al editar el departamento: {e}")

    def eliminar_departamento(self, cnx, cursor):
        try:
            print("\n--- ELIMINAR DEPARTAMENTO ---")

            cursor.execute("""
                SELECT id_Departamento, NombreDepartamento
                FROM Departamento
                ORDER BY id_Departamento
            """)
            departamentos = cursor.fetchall()

            if not departamentos:
                print("No hay departamentos para eliminar.")
                return

            print("\nDepartamentos:")
            for dep in departamentos:
                print(f"  {dep[0]} - {dep[1]}")

            # Seleccionar ID
            while True:
                id_dep = pedir_input("Ingrese el ID del departamento a eliminar (0 para cancelar): ", cnx)
                if id_dep is None:
                    return
                if not id_dep.isdigit():
                    print("Debe ingresar un número válido.")
                    continue
                id_dep = int(id_dep)

                if not any(dep[0] == id_dep for dep in departamentos):
                    print("ID no válido, intente de nuevo.")
                    continue
                break

            # Verificar dependencias (EmpleadoDepartamento)
            cursor.execute("""
                SELECT COUNT(*)
                FROM EmpleadoDepartamento
                WHERE Departamento_idDepartamento = %s
            """, (id_dep,))
            count = cursor.fetchone()[0]

            if count > 0:
                print(f"No se puede eliminar el departamento. Hay {count} empleados asignados actualmente.")
                return

            # Confirmación final
            confirmar = pedir_input("¿Está seguro de eliminar este departamento? (s/n, 0 para cancelar): ", cnx, opcional=True)
            if confirmar is None:
                return
            if confirmar.lower() != "s":
                print("Operación cancelada.")
                return

            # Eliminar
            cursor.execute("DELETE FROM Departamento WHERE id_Departamento = %s", (id_dep,))
            cnx.commit()
            print("Departamento eliminado correctamente.")

        except Exception as e:
            try:
                cnx.rollback()
            except Exception:
                pass
            print(f"Ocurrió un error al eliminar el departamento: {e}")

    # --- PROYECTOS: Listo ---
        
    def crear_proyecto(self, cnx, cursor):
        try:
            print("\n--- CREAR PROYECTO ---")

            nombre = pedir_input("Nombre del proyecto (0 para cancelar): ", cnx)
            if nombre is None:
                return

            descripcion = pedir_input("Descripción del proyecto (opcional, 0 para cancelar): ", cnx, opcional=True)
            if descripcion is None:
                return

            fecha_inicio = pedir_input(
                "Fecha de inicio del proyecto (YYYY-MM-DD, dejar vacío si no aplica, 0 para cancelar): ",
                cnx, opcional=True
            )
            if fecha_inicio is None:
                return

            # Validar fecha si se ingresó
            if fecha_inicio:
                try:
                    datetime.strptime(fecha_inicio, "%Y-%m-%d")
                except ValueError:
                    print("Fecha inválida. Se dejará sin fecha de inicio.")
                    fecha_inicio = None
            else:
                fecha_inicio = None

            cursor.execute("""
                INSERT INTO Proyecto (NombreProyecto, DescripcionProyecto, FechaInicio)
                VALUES (%s, %s, %s)
            """, (nombre, descripcion, fecha_inicio))

            cnx.commit()
            print(f"Proyecto '{nombre}' creado correctamente.")

        except Exception as e:
            cnx.rollback()
            print(f"Error al crear el proyecto: {e}")

    def listar_proyectos(self, cursor):
        try:
            print("\n--- LISTADO DE PROYECTOS ---")

            cursor.execute("""
                SELECT id_Proyecto, NombreProyecto, FechaInicioProyecto, DescripcionProyecto
                FROM Proyecto
                ORDER BY id_Proyecto
            """)
            proyectos = cursor.fetchall()

            if not proyectos:
                print("No hay proyectos registrados.")
                return

            cantidad_por_pagina = 5
            total = len(proyectos)
            pagina = 0

            while True:
                inicio = pagina * cantidad_por_pagina
                fin = inicio + cantidad_por_pagina
                for p in proyectos[inicio:fin]:
                    print(f"""
                            ID: {p[0]}
                            Nombre: {p[1]}
                            Fecha inicio: {p[2]}
                            Descripción: {p[3] if p[3] else '(Sin descripción)'}
                            ------------------------------
                    """)

                if fin >= total:
                    print("No hay más proyectos.")
                    break

                opcion = pedir_input("Presione ENTER para ver los siguientes, 'q' para salir, o 0 para cancelar: ", opcional=True)
                if opcion is None or opcion.lower() == 'q':
                    print("Operación cancelada o fin del listado.")
                    break

                pagina += 1

        except Exception as e:
            print(f"Ocurrió un error al listar proyectos: {e}")

    def editar_proyecto(self, cnx, cursor):
        try:
            print("\n--- EDITAR PROYECTO ---")

            cursor.execute("SELECT id_Proyecto, NombreProyecto, DescripcionProyecto, FechaInicioProyecto FROM Proyecto")
            proyectos = cursor.fetchall()

            if not proyectos:
                print("No hay proyectos registrados.")
                return

            print("Proyectos existentes:")
            for p in proyectos:
                print(f"{p[0]} - {p[1]} | Fecha inicio: {p[3]}")

            while True:
                id_pro = pedir_input("Ingrese el ID del proyecto a editar (0 para cancelar): ", cnx)
                if id_pro is None:
                    return
                if id_pro.isdigit():
                    id_pro = int(id_pro)
                    cursor.execute("SELECT * FROM Proyecto WHERE id_Proyecto = %s", (id_pro,))
                    proyecto = cursor.fetchone()
                    if proyecto:
                        break
                    print("ID de proyecto no existe. Intente nuevamente.")
                else:
                    print("Debe ingresar un número válido.")

            nuevo_nombre = pedir_input(f"Nuevo nombre (actual: {proyecto[3]}) (0 para cancelar): ", cnx, opcional=True)
            if nuevo_nombre is None: return
            nuevo_nombre = nuevo_nombre or proyecto[3]

            nueva_descripcion = pedir_input(f"Nueva descripción (actual: {proyecto[2]}) (0 para cancelar): ", cnx, opcional=True)
            if nueva_descripcion is None: return
            nueva_descripcion = nueva_descripcion or proyecto[2]

            nueva_fecha = pedir_input(
                f"Nueva fecha de inicio (actual: {proyecto[1]}) "
                "(YYYY-MM-DD, dejar vacío para mantener, 0 para cancelar): ",
                cnx, opcional=True
            )
            if nueva_fecha is None: return

            # Validar fecha si se ingresó algo
            if nueva_fecha:
                try:
                    datetime.strptime(nueva_fecha, "%Y-%m-%d")
                except ValueError:
                    print("Fecha inválida. Se mantendrá la anterior.")
                    nueva_fecha = proyecto[1]
            else:
                nueva_fecha = proyecto[1]  # si dejó vacío, mantener la original

            cursor.execute("""
                UPDATE Proyecto
                SET NombreProyecto = %s,
                    DescripcionProyecto = %s,
                    FechaInicioProyecto = %s
                WHERE id_Proyecto = %s
            """, (nuevo_nombre, nueva_descripcion, nueva_fecha, id_pro))

            cnx.commit()
            print(f"Proyecto ID {id_pro} actualizado correctamente.")

        except Exception as e:
            cnx.rollback()
            print(f"Ocurrió un error al editar el proyecto: {e}")

    def eliminar_proyecto(self, cnx, cursor):
        try:
            print("\n--- ELIMINAR PROYECTO ---")

            cursor.execute("SELECT id_Proyecto, NombreProyecto FROM Proyecto ORDER BY id_Proyecto")
            proyectos = cursor.fetchall()

            if not proyectos:
                print("No hay proyectos para eliminar.")
                return

            for p in proyectos:
                print(f"{p[0]} - {p[1]}")

            while True:
                id_pro = pedir_input("Ingrese el ID del proyecto a eliminar (0 para cancelar): ", cnx)
                if id_pro is None:
                    return
                if id_pro.isdigit():
                    id_pro = int(id_pro)
                    if any(p[0] == id_pro for p in proyectos):
                        break
                    print("ID no válido, intente de nuevo.")
                else:
                    print("Debe ingresar un número válido.")

            # Verificar si hay empleados asignados
            cursor.execute("""
                SELECT COUNT(*) 
                FROM EmpleadoProyecto 
                WHERE Proyecto_idProyecto = %s AND Activo = TRUE
            """, (id_pro,))
            count = cursor.fetchone()[0]

            if count > 0:
                print(f"No se puede eliminar el proyecto. Tiene {count} empleados asignados actualmente.")
                return

            confirm = pedir_input("¿Está seguro de eliminar este proyecto? (s/n, 0 para cancelar): ", cnx)
            if confirm is None or confirm.lower() != 's':
                print("Eliminación cancelada.")
                return

            cursor.execute("DELETE FROM Proyecto WHERE id_Proyecto = %s", (id_pro,))
            cnx.commit()
            print("Proyecto eliminado correctamente.")

        except Exception as e:
            cnx.rollback()
            print(f"Ocurrió un error al eliminar el proyecto: {e}")

    # Asignaciones:

    # --- EmpleadoDepartamento ---

    def asignar_empleado_a_departamento(self, cnx, cursor):
        try:
            print("\n--- ASIGNAR EMPLEADO A DEPARTAMENTO ---")

            # Listar usuarios
            cursor.execute("""
                SELECT id_UsuarioSistema, Nombre, Apellido 
                FROM UsuarioSistema
                ORDER BY id_UsuarioSistema
            """)
            usuarios = cursor.fetchall()
            if not usuarios:
                print("No hay usuarios registrados.")
                return

            print("\nUsuarios disponibles:")
            for u in usuarios:
                print(f"  {u[0]} - {u[1]} {u[2]}")

            # Seleccionar usuario
            while True:
                id_usuario = pedir_input("Ingrese el ID del usuario a asignar (0 para cancelar): ", cnx)
                if id_usuario is None:
                    return
                if not id_usuario.isdigit():
                    print("Debe ingresar un número válido.")
                    continue
                id_usuario = int(id_usuario)
                if not any(u[0] == id_usuario for u in usuarios):
                    print("No existe un usuario con ese ID.")
                    continue
                break

            # Listar departamentos
            cursor.execute("""
                SELECT id_Departamento, NombreDepartamento 
                FROM Departamento
                ORDER BY id_Departamento
            """)
            departamentos = cursor.fetchall()
            if not departamentos:
                print("No hay departamentos registrados.")
                return

            print("\nDepartamentos disponibles:")
            for d in departamentos:
                print(f"  {d[0]} - {d[1]}")

            # Seleccionar departamento
            while True:
                id_departamento = pedir_input("Ingrese el ID del departamento (0 para cancelar): ", cnx)
                if id_departamento is None:
                    return
                if not id_departamento.isdigit():
                    print("Debe ingresar un número válido.")
                    continue
                id_departamento = int(id_departamento)
                if not any(d[0] == id_departamento for d in departamentos):
                    print("No existe un departamento con ese ID.")
                    continue
                break

            # Verificar si ya existe asignación activa
            cursor.execute("""
                SELECT id_EmpleadoDepartamento, Activo 
                FROM EmpleadoDepartamento
                WHERE UsuarioSistema_idUsuarioSistema = %s AND Departamento_idDepartamento = %s
            """, (id_usuario, id_departamento))
            asignacion = cursor.fetchone()

            if asignacion:
                if asignacion[1]:  # activo
                    print("El usuario ya está asignado a este departamento.")
                    return
                else:
                    # Reactivar asignación
                    cursor.execute("""
                        UPDATE EmpleadoDepartamento 
                        SET Activo = TRUE, FechaAsignacion = CURRENT_TIMESTAMP
                        WHERE id_EmpleadoDepartamento = %s
                    """, (asignacion[0],))
                    cnx.commit()
                    print("Empleado reactivado en el departamento correctamente.")
                    return

            # Nueva asignación
            cursor.execute("""
                INSERT INTO EmpleadoDepartamento (Departamento_idDepartamento, UsuarioSistema_idUsuarioSistema)
                VALUES (%s, %s)
            """, (id_departamento, id_usuario))
            cnx.commit()

            print(f"\nEmpleado asignado correctamente al departamento ID {id_departamento}.")

        except Exception as e:
            try:
                cnx.rollback()
            except Exception:
                pass
            print(f"Ocurrió un error al asignar el empleado: {e}")

    def listar_empleados_en_departamento(self, cursor):
        try:
            print("\n--- LISTADO DE EMPLEADOS EN DEPARTAMENTOS ---")

            # Obtener todas las asignaciones activas e inactivas
            cursor.execute("""
                SELECT 
                    ED.id_EmpleadoDepartamento,
                    U.id_UsuarioSistema, U.Nombre, U.Apellido, U.NombreUsuario,
                    D.id_Departamento, D.NombreDepartamento, 
                    R.tipo_Rol,
                    ED.Activo, ED.FechaAsignacion
                FROM EmpleadoDepartamento ED
                JOIN UsuarioSistema U ON ED.UsuarioSistema_idUsuarioSistema = U.id_UsuarioSistema
                JOIN Departamento D ON ED.Departamento_idDepartamento = D.id_Departamento
                JOIN Rol R ON U.Rol_idRol = R.id_Rol
                ORDER BY D.NombreDepartamento, U.Nombre
            """)
            asignaciones = cursor.fetchall()

            if not asignaciones:
                print("No hay empleados asignados a ningún departamento.")
                return

            # Paginación
            por_pagina = 5
            total = len(asignaciones)
            pagina = 0

            while True:
                inicio = pagina * por_pagina
                fin = inicio + por_pagina
                grupo = asignaciones[inicio:fin]

                if not grupo:
                    print("No hay más resultados para mostrar.")
                    break

                print(f"\n--- PÁGINA {pagina + 1} / {((total - 1) // por_pagina) + 1} ---")

                for a in grupo:
                    estado = "Activo" if a[8] else "Inactivo"
                    print(f"""
                        ID Asignación: {a[0]} | Fecha: {a[9]}
                        Empleado: {a[2]} {a[3]} ({a[4]})
                        Departamento: {a[6]} (ID {a[5]})
                        Rol: {a[7]}
                        Estado: {estado}
                        ----------------------------------------
                        """)

                if fin >= total:
                    print("Fin del listado.")
                    break

                continuar = input("¿Ver siguiente página? (s/n): ").strip().lower()
                if continuar != 's':
                    print("Operación finalizada.")
                    break
                pagina += 1

        except Exception as e:
            print(f"Ocurrió un error al listar los empleados: {e}")

    def editar_asignacion_empleado_departamento(self, cnx, cursor):
        try:
            print("\n--- EDITAR ASIGNACIÓN DE EMPLEADO A DEPARTAMENTO ---")

            # Listar asignaciones existentes
            cursor.execute("""
                SELECT 
                    ED.id_EmpleadoDepartamento, ED.Activo, ED.FechaAsignacion,
                    U.id_UsuarioSistema, U.Nombre, U.Apellido, U.NombreUsuario,
                    D.id_Departamento, D.NombreDepartamento
                FROM EmpleadoDepartamento ED
                JOIN UsuarioSistema U ON ED.UsuarioSistema_idUsuarioSistema = U.id_UsuarioSistema
                JOIN Departamento D ON ED.Departamento_idDepartamento = D.id_Departamento
                ORDER BY ED.id_EmpleadoDepartamento
            """)
            asignaciones = cursor.fetchall()

            if not asignaciones:
                print("No hay asignaciones registradas.")
                return

            print("\nAsignaciones disponibles:")
            for a in asignaciones:
                estado = "Activo" if a[1] else "Inactivo"
                print(f"{a[0]} - {a[4]} {a[5]} ({a[6]}) | Departamento: {a[8]} | {estado}")

            # Seleccionar asignación a editar
            id_asignacion = pedir_input("Ingrese el ID de la asignación a editar (0 para cancelar): ", cnx)
            if id_asignacion is None:
                return
            if not id_asignacion.isdigit():
                print("Debe ingresar un número válido.")
                return
            id_asignacion = int(id_asignacion)

            asignacion = next((a for a in asignaciones if a[0] == id_asignacion), None)
            if not asignacion:
                print("No existe una asignación con ese ID.")
                return

            id_usuario = asignacion[3]
            id_departamento_actual = asignacion[7]
            estado_actual = asignacion[1]

            print(f"\nEmpleado: {asignacion[4]} {asignacion[5]} ({asignacion[6]})")
            print(f"Departamento actual: {asignacion[8]}")
            print(f"Estado actual: {'Activo' if estado_actual else 'Inactivo'}")

            # Mostrar opciones
            print("""
    --- OPCIONES DE EDICIÓN ---
    1. Cambiar departamento
    2. Activar / Desactivar asignación
    0. Cancelar
    """)
            opcion = input("Seleccione una opción: ").strip()

            if opcion == "0":
                print("Operación cancelada.")
                return

            # Opción 1: Cambiar departamento
            if opcion == "1":
                cursor.execute("SELECT id_Departamento, NombreDepartamento FROM Departamento ORDER BY id_Departamento")
                departamentos = cursor.fetchall()
                if not departamentos:
                    print("No hay departamentos registrados.")
                    return

                print("\nDepartamentos disponibles:")
                for d in departamentos:
                    print(f"{d[0]} - {d[1]}")

                nuevo_id = pedir_input("Ingrese el ID del nuevo departamento (0 para cancelar): ", cnx)
                if nuevo_id is None:
                    return
                if not nuevo_id.isdigit():
                    print("Debe ingresar un número válido.")
                    return
                nuevo_id = int(nuevo_id)

                if nuevo_id == id_departamento_actual:
                    print("El empleado ya pertenece a ese departamento.")
                    return

                # Verificar si ya existe una asignación (activa o no)
                cursor.execute("""
                    SELECT id_EmpleadoDepartamento, Activo 
                    FROM EmpleadoDepartamento
                    WHERE UsuarioSistema_idUsuarioSistema = %s AND Departamento_idDepartamento = %s
                """, (id_usuario, nuevo_id))
                existente = cursor.fetchone()

                if existente:
                    if existente[1]:
                        print("El empleado ya está activo en ese departamento. No se realizará ningún cambio.")
                        return
                    else:
                        # Reactivar en el nuevo departamento
                        cursor.execute("""
                            UPDATE EmpleadoDepartamento 
                            SET Activo = TRUE, FechaAsignacion = CURRENT_TIMESTAMP
                            WHERE id_EmpleadoDepartamento = %s
                        """, (existente[0],))
                        cnx.commit()
                        print("Empleado reactivado en el nuevo departamento.")
                        return

                # Si no existe, actualizar el registro actual con el nuevo departamento
                cursor.execute("""
                    UPDATE EmpleadoDepartamento
                    SET Departamento_idDepartamento = %s, FechaAsignacion = CURRENT_TIMESTAMP
                    WHERE id_EmpleadoDepartamento = %s
                """, (nuevo_id, id_asignacion))
                cnx.commit()
                print("Departamento actualizado correctamente.")

            # Opción 2: Activar / Desactivar asignación
            elif opcion == "2":
                nuevo_estado = not estado_actual
                cursor.execute("""
                    UPDATE EmpleadoDepartamento
                    SET Activo = %s, FechaAsignacion = CURRENT_TIMESTAMP
                    WHERE id_EmpleadoDepartamento = %s
                """, (nuevo_estado, id_asignacion))
                cnx.commit()
                print(f"Asignación {'activada' if nuevo_estado else 'desactivada'} correctamente.")

            else:
                print("Opción no válida.")

        except Exception as e:
            try:
                cnx.rollback()
            except Exception:
                pass
            print(f"Ocurrió un error al editar la asignación: {e}")

    def eliminar_asignacion_empleado_departamento(self, cnx, cursor):
        try:
            print("\n--- DESASIGNAR EMPLEADO DE DEPARTAMENTO ---")

            # Listar todas las asignaciones
            cursor.execute("""
                SELECT 
                    ED.id_EmpleadoDepartamento, ED.Activo, ED.FechaAsignacion,
                    U.Nombre, U.Apellido, U.NombreUsuario,
                    D.NombreDepartamento
                FROM EmpleadoDepartamento ED
                JOIN UsuarioSistema U ON ED.UsuarioSistema_idUsuarioSistema = U.id_UsuarioSistema
                JOIN Departamento D ON ED.Departamento_idDepartamento = D.id_Departamento
                ORDER BY ED.id_EmpleadoDepartamento
            """)
            asignaciones = cursor.fetchall()

            if not asignaciones:
                print("No hay asignaciones registradas.")
                return

            print("\nAsignaciones disponibles:")
            for a in asignaciones:
                estado = "Activo" if a[1] else "Inactivo"
                print(f"{a[0]} - {a[3]} {a[4]} ({a[5]}) | Departamento: {a[6]} | {estado}")

            # Pedir ID
            id_asignacion = pedir_input("Ingrese el ID de la asignación a eliminar (0 para cancelar): ", cnx)
            if id_asignacion is None:
                return
            if not id_asignacion.isdigit():
                print("Debe ingresar un número válido.")
                return
            id_asignacion = int(id_asignacion)

            asignacion = next((a for a in asignaciones if a[0] == id_asignacion), None)
            if not asignacion:
                print("No existe una asignación con ese ID.")
                return

            # Verificar si hay proyectos vinculados a esa asignación
            cursor.execute("""
                SELECT COUNT(*) 
                FROM EmpleadoProyecto 
                WHERE EmpleadoDepartamento_idEmpleadoDepartamento = %s
            """, (id_asignacion,))
            proyectos_asociados = cursor.fetchone()[0]

            if proyectos_asociados > 0:
                print(f"No se puede eliminar la asignación. El empleado participa en {proyectos_asociados} proyecto(s).")
                print("Debe desasignarlo de esos proyectos antes de eliminar esta relación.")
                return

            # Confirmación
            confirm = pedir_input(
                f"¿Está seguro de eliminar la asignación del empleado {asignacion[3]} {asignacion[4]} en el departamento '{asignacion[6]}'?\nEscriba DELETE para confirmar o 0 para cancelar: ",
                cnx
            )
            if confirm is None or confirm != "DELETE":
                print("Operación cancelada.")
                cnx.rollback()
                return

            # Eliminar asignación
            cursor.execute("DELETE FROM EmpleadoDepartamento WHERE id_EmpleadoDepartamento = %s", (id_asignacion,))
            cnx.commit()
            print("Asignación eliminada correctamente.")

        except Exception as e:
            try:
                cnx.rollback()
            except Exception:
                pass
            print(f"Ocurrió un error al eliminar la asignación: {e}")

    # --- EmpleadoProyecto ---

    def asignar_empleado_a_proyecto(self, cnx, cursor):
        try:
            print("\n--- ASIGNAR EMPLEADO A PROYECTO ---")

            # Obtener empleados activos en departamentos
            cursor.execute("""
                SELECT 
                    ED.id_EmpleadoDepartamento,
                    U.id_UsuarioSistema, U.Nombre, U.Apellido, U.NombreUsuario,
                    D.NombreDepartamento
                FROM EmpleadoDepartamento ED
                JOIN UsuarioSistema U ON ED.UsuarioSistema_idUsuarioSistema = U.id_UsuarioSistema
                JOIN Departamento D ON ED.Departamento_idDepartamento = D.id_Departamento
                WHERE ED.Activo = TRUE
                ORDER BY U.Nombre
            """)
            empleados = cursor.fetchall()

            if not empleados:
                print("No hay empleados activos en ningún departamento.")
                return

            print("Empleados disponibles para asignar:")
            for e in empleados:
                print(f"{e[0]} - {e[2]} {e[3]} ({e[4]}) | Departamento: {e[5]}")

            # Seleccionar empleado
            id_empleado_dep = pedir_input("Ingrese el ID del empleado a asignar (0 para cancelar): ", cnx)
            if id_empleado_dep is None:
                return
            if not id_empleado_dep.isdigit():
                print("Debe ingresar un número válido.")
                return
            id_empleado_dep = int(id_empleado_dep)

            empleado = next((e for e in empleados if e[0] == id_empleado_dep), None)
            if not empleado:
                print("No existe un empleado con ese ID.")
                return

            # Listar proyectos
            cursor.execute("SELECT id_Proyecto, NombreProyecto FROM Proyecto ORDER BY id_Proyecto")
            proyectos = cursor.fetchall()
            if not proyectos:
                print("No hay proyectos registrados.")
                return

            print("\nProyectos disponibles:")
            for p in proyectos:
                print(f"{p[0]} - {p[1]}")

            # Seleccionar proyecto
            id_proyecto = pedir_input("Ingrese el ID del proyecto (0 para cancelar): ", cnx)
            if id_proyecto is None:
                return
            if not id_proyecto.isdigit():
                print("Debe ingresar un número válido.")
                return
            id_proyecto = int(id_proyecto)

            proyecto = next((p for p in proyectos if p[0] == id_proyecto), None)
            if not proyecto:
                print("No existe un proyecto con ese ID.")
                return

            # Verificar si ya existe relación
            cursor.execute("""
                SELECT id_DetalleProyecto, Activo
                FROM EmpleadoProyecto
                WHERE EmpleadoDepartamento_idEmpleadoDepartamento = %s AND Proyecto_idProyecto = %s
            """, (id_empleado_dep, id_proyecto))
            existente = cursor.fetchone()

            # Si ya existe activa → no duplicar
            if existente and existente[1]:
                print("El empleado ya está asignado a este proyecto.")
                return

            # Si existe pero inactiva → reactivar
            if existente and not existente[1]:
                cursor.execute("""
                    UPDATE EmpleadoProyecto
                    SET Activo = TRUE, FechaProyectoInscrito = CURRENT_TIMESTAMP
                    WHERE id_DetalleProyecto = %s
                """, (existente[0],))
                cnx.commit()
                print("Asignación reactivada correctamente.")
                return

            # Si no existe, crear una nueva
            while True:
                horas = input("Ingrese cantidad de horas asignadas: ").strip()
                if horas == "0":
                    print("Operación cancelada.")
                    return
                if not horas.isdigit() or int(horas) <= 0:
                    print("Debe ingresar un número mayor a 0.")
                    continue
                horas = int(horas)
                break

            descripcion = input("Descripción de la tarea (opcional, 0 para cancelar): ").strip()
            if descripcion == "0":
                print("Operación cancelada.")
                return

            # Insertar nuevo registro
            cursor.execute("""
                INSERT INTO EmpleadoProyecto 
                (EmpleadoDepartamento_idEmpleadoDepartamento, Proyecto_idProyecto, CantidadHorasEmpleadoProyecto, DescripcionTareaProyecto)
                VALUES (%s, %s, %s, %s)
            """, (id_empleado_dep, id_proyecto, horas, descripcion))
            cnx.commit()

            print(f"Empleado '{empleado[2]} {empleado[3]}' asignado correctamente al proyecto '{proyecto[1]}'.")
            
        except Exception as e:
            try:
                cnx.rollback()
            except Exception:
                pass
            print(f"Ocurrió un error al asignar el empleado al proyecto: {e}")

    def editar_empleado_proyecto(self, cnx, cursor):
        try:
            print("\n--- EDITAR ASIGNACIÓN DE EMPLEADO A PROYECTO ---")

            # Listar asignaciones activas
            cursor.execute("""
                SELECT 
                    EP.id_DetalleProyecto,
                    U.Nombre, U.Apellido,
                    P.NombreProyecto,
                    EP.CantidadHorasEmpleadoProyecto,
                    EP.DescripcionTareaProyecto
                FROM EmpleadoProyecto EP
                JOIN EmpleadoDepartamento ED ON EP.EmpleadoDepartamento_idEmpleadoDepartamento = ED.id_EmpleadoDepartamento
                JOIN UsuarioSistema U ON ED.UsuarioSistema_idUsuarioSistema = U.id_UsuarioSistema
                JOIN Proyecto P ON EP.Proyecto_idProyecto = P.id_Proyecto
                WHERE EP.Activo = TRUE
                ORDER BY EP.id_DetalleProyecto
            """)
            asignaciones = cursor.fetchall()

            if not asignaciones:
                print("No hay asignaciones activas para editar.")
                return

            # Mostrar lista de asignaciones activas
            print("Asignaciones activas:")
            for a in asignaciones:
                print(f"{a[0]} - {a[1]} {a[2]} | Proyecto: {a[3]} | Horas: {a[4]} | Tarea: {a[5]}")

            # Seleccionar ID de asignación
            id_detalle = input("\nIngrese el ID del detalle a editar (0 para cancelar): ").strip()
            if id_detalle == "0":
                print("Operación cancelada.")
                return
            if not id_detalle.isdigit():
                print("Debe ingresar un número válido.")
                return
            id_detalle = int(id_detalle)

            detalle = next((a for a in asignaciones if a[0] == id_detalle), None)
            if not detalle:
                print("No existe una asignación activa con ese ID.")
                return

            # Mostrar datos actuales
            print(f"\nEmpleado: {detalle[1]} {detalle[2]}")
            print(f"Proyecto: {detalle[3]}")
            print(f"Horas actuales: {detalle[4]}")
            print(f"Tarea actual: {detalle[5]}")

            # Pedir nuevos valores
            horas = input("Nueva cantidad de horas (ENTER para mantener, 0 para cancelar): ").strip()
            if horas == "0":
                print("Operación cancelada.")
                return
            if horas == "":
                horas = detalle[4]
            elif not horas.isdigit() or int(horas) <= 0:
                print("Debe ingresar un número válido mayor a 0.")
                return
            else:
                horas = int(horas)

            descripcion = input("Nueva descripción de tarea (ENTER para mantener, 0 para cancelar): ").strip()
            if descripcion == "0":
                print("Operación cancelada.")
                return
            if descripcion == "":
                descripcion = detalle[5]

            # Confirmación
            confirmar = input(f"¿Desea actualizar esta asignación? (s/n): ").strip().lower()
            if confirmar != "s":
                print("Operación cancelada.")
                return

            # Actualizar datos
            cursor.execute("""
                UPDATE EmpleadoProyecto
                SET CantidadHorasEmpleadoProyecto = %s, DescripcionTareaProyecto = %s
                WHERE id_DetalleProyecto = %s
            """, (horas, descripcion, id_detalle))
            cnx.commit()

            print("Asignación actualizada correctamente.")

        except Exception as e:
            try:
                cnx.rollback()
            except Exception:
                pass
            print(f"Ocurrió un error al editar la asignación: {e}")

    def desasignar_empleado_a_proyecto(self, cnx, cursor):
        try:
            print("\n--- DESASIGNAR EMPLEADO DE PROYECTO ---")

            # Listar asignaciones activas
            cursor.execute("""
                SELECT 
                    EP.id_DetalleProyecto,
                    U.Nombre, U.Apellido,
                    P.NombreProyecto,
                    EP.CantidadHorasEmpleadoProyecto,
                    EP.DescripcionTareaProyecto
                FROM EmpleadoProyecto EP
                JOIN EmpleadoDepartamento ED ON EP.EmpleadoDepartamento_idEmpleadoDepartamento = ED.id_EmpleadoDepartamento
                JOIN UsuarioSistema U ON ED.UsuarioSistema_idUsuarioSistema = U.id_UsuarioSistema
                JOIN Proyecto P ON EP.Proyecto_idProyecto = P.id_Proyecto
                WHERE EP.Activo = TRUE
                ORDER BY EP.id_DetalleProyecto
            """)
            asignaciones = cursor.fetchall()

            if not asignaciones:
                print("No hay asignaciones activas de empleados a proyectos.")
                return

            print("Asignaciones activas:")
            for a in asignaciones:
                print(f"{a[0]} - {a[1]} {a[2]} | Proyecto: {a[3]} | Horas: {a[4]} | Tarea: {a[5]}")

            # Pedir ID de la asignación
            id_asignacion = input("\nIngrese el ID de la asignación a desasignar (0 para cancelar): ").strip()
            if id_asignacion == "0":
                print("Operación cancelada.")
                return
            if not id_asignacion.isdigit():
                print("Debe ingresar un número válido.")
                return
            id_asignacion = int(id_asignacion)

            # Buscar la asignación seleccionada
            asignacion = next((a for a in asignaciones if a[0] == id_asignacion), None)
            if not asignacion:
                print("No existe una asignación activa con ese ID.")
                return

            # Confirmar desasignación
            confirmar = input(f"¿Está seguro de desasignar al empleado {asignacion[1]} {asignacion[2]} del proyecto '{asignacion[3]}'? (s/n): ").strip().lower()
            if confirmar != 's':
                print("Operación cancelada.")
                return

            # Marcar como inactiva la relación
            cursor.execute("""
                UPDATE EmpleadoProyecto
                SET Activo = FALSE
                WHERE id_DetalleProyecto = %s
            """, (id_asignacion,))
            cnx.commit()

            print(f"Empleado {asignacion[1]} {asignacion[2]} desasignado correctamente del proyecto '{asignacion[3]}'.")
            
        except Exception as e:
            try:
                cnx.rollback()
            except Exception:
                pass
            print(f"Ocurrió un error al desasignar al empleado del proyecto: {e}")

    def ver_detalle_empleado_proyecto(self, cursor):
        try:
            print("\n--- VER DETALLES DE ASIGNACIÓN DE EMPLEADOS A PROYECTOS ---")

            # Preguntar si se quiere ver solo activos o también inactivos
            print("¿Qué desea ver?")
            print("1. Solo asignaciones activas")
            print("2. Ver historial completo (activas + inactivas)")
            opcion = input("Seleccione una opción (0 para cancelar): ").strip()

            if opcion == "0":
                print("Operación cancelada.")
                return
            elif opcion not in ["1", "2"]:
                print("Opción inválida.")
                return

            filtro_activo = "EP.Activo = TRUE" if opcion == "1" else "1=1"

            # Traer asignaciones según filtro (incluyendo Departamento)
            cursor.execute(f"""
                SELECT 
                    EP.id_DetalleProyecto,
                    U.Nombre, U.Apellido, U.NombreUsuario,
                    P.NombreProyecto,
                    EP.FechaProyectoInscrito,
                    EP.CantidadHorasEmpleadoProyecto,
                    EP.DescripcionTareaProyecto,
                    CASE WHEN EP.Activo = TRUE THEN 'Activo' ELSE 'Inactivo' END AS Estado,
                    Dpto.NombreDepartamento
                FROM EmpleadoProyecto EP
                JOIN EmpleadoDepartamento ED
                    ON EP.EmpleadoDepartamento_idEmpleadoDepartamento = ED.id_EmpleadoDepartamento
                JOIN UsuarioSistema U
                    ON ED.UsuarioSistema_idUsuarioSistema = U.id_UsuarioSistema
                JOIN Proyecto P
                    ON EP.Proyecto_idProyecto = P.id_Proyecto
                JOIN Departamento Dpto
                    ON ED.Departamento_idDepartamento = Dpto.id_Departamento
                WHERE {filtro_activo}
                ORDER BY EP.id_DetalleProyecto
            """)
            asignaciones = cursor.fetchall()

            if not asignaciones:
                print("No se encontraron asignaciones con el criterio seleccionado.")
                return

            # Mostrar todas las asignaciones (ahora con Departamento)
            print("\n--- LISTADO DE ASIGNACIONES ---")
            for a in asignaciones:
                # a[9] = NombreDepartamento
                print(f"""
                        ID Detalle Proyecto:   {a[0]}
                        Empleado:              {a[1]} {a[2]} ({a[3]})
                        Departamento:          {a[9]}
                        Proyecto:              {a[4]}
                        Fecha Inscripción:     {a[5]}
                        Horas Asignadas:       {a[6]}
                        Descripción Tarea:     {a[7] if a[7] else '(Sin descripción)'}
                        Estado:                {a[8]}
                        ----------------------------------------
                """)

            # Consultar un detalle específico
            ver_detalle = input("¿Desea ver un detalle específico? (s/n): ").strip().lower()
            if ver_detalle != "s":
                print("Operación finalizada.")
                return

            id_detalle = input("Ingrese el ID del detalle a consultar (0 para cancelar): ").strip()
            if id_detalle == "0":
                print("Operación cancelada.")
                return
            if not id_detalle.isdigit():
                print("Debe ingresar un número válido.")
                return
            id_detalle = int(id_detalle)

            # Buscar detalle (incluyendo Departamento)
            cursor.execute("""
                SELECT 
                    EP.id_DetalleProyecto,
                    U.Nombre, U.Apellido, U.NombreUsuario,
                    P.NombreProyecto,
                    EP.FechaProyectoInscrito,
                    EP.CantidadHorasEmpleadoProyecto,
                    EP.DescripcionTareaProyecto,
                    CASE WHEN EP.Activo = TRUE THEN 'Activo' ELSE 'Inactivo' END AS Estado,
                    Dpto.NombreDepartamento
                FROM EmpleadoProyecto EP
                JOIN EmpleadoDepartamento ED
                    ON EP.EmpleadoDepartamento_idEmpleadoDepartamento = ED.id_EmpleadoDepartamento
                JOIN UsuarioSistema U
                    ON ED.UsuarioSistema_idUsuarioSistema = U.id_UsuarioSistema
                JOIN Proyecto P
                    ON EP.Proyecto_idProyecto = P.id_Proyecto
                JOIN Departamento Dpto
                    ON ED.Departamento_idDepartamento = Dpto.id_Departamento
                WHERE EP.id_DetalleProyecto = %s
            """, (id_detalle,))
            detalle = cursor.fetchone()

            if not detalle:
                print("No existe una asignación con ese ID.")
                return

            # Mostrar detalle completo (con Departamento)
            print("\n" + "="*50)
            print("       DETALLE DE EMPLEADO EN PROYECTO")
            print("="*50)
            print(f"ID Detalle Proyecto: {detalle[0]}")
            print(f"Empleado:            {detalle[1]} {detalle[2]} ({detalle[3]})")
            print(f"Departamento:        {detalle[9]}")
            print(f"Proyecto:            {detalle[4]}")
            print(f"Fecha Inscripción:   {detalle[5]}")
            print(f"Horas Asignadas:     {detalle[6]}")
            print(f"Descripción Tarea:   {detalle[7] if detalle[7] else '(Sin descripción)'}")
            print(f"Estado:              {detalle[8]}")
            print("="*50 + "\n")

        except Exception as e:
            print(f"Ocurrió un error al visualizar los detalles: {e}")

    # --- Informes ---

    # Exportar a Excel
    
    def generarInforme():
        pass
from clases.UsuarioSistema import UsuarioSistema
from utils import pedir_input, validar_email, validar_contrasena, validar_telefono, pedir_contrasena
import hashlib


class Empleado(UsuarioSistema):
    def __init__(self, Nombre, Apellido, RUT, Email, Telefono, NombreUsuario, Contraseña, id_Direccion, id_Rol, id_UsuarioSistema=None):
        super().__init__(id_UsuarioSistema, Nombre, Apellido, RUT, Email, Telefono, NombreUsuario, Contraseña, id_Direccion, id_Rol)

    def ver_datos_personales(self, cursor):
        """
        Muestra datos personales y dirección. No rompe tu flujo de impresión.
        Maneja valores None de dirección para evitar 'None' en pantalla.
        """
        try:
            cursor.execute("""
                SELECT 
                    U.Nombre, U.Apellido, U.RUT, U.Email, U.Telefono, U.NombreUsuario,
                    D.Calle, D.Numero, D.Ciudad, D.Region, D.Pais, D.CodigoPostal
                FROM UsuarioSistema U
                LEFT JOIN Direccion D ON U.Direccion_idDireccion = D.id_Direccion
                WHERE U.id_UsuarioSistema = %s
            """, (self.id_UsuarioSistema,))
            u = cursor.fetchone()

            if not u:
                print("Error: No se encontraron datos del usuario actual.")
                return

            # Desempaquetado con defaults seguros para dirección
            (nombre, apellido, rut, email, telefono, nombre_usuario,
             calle, numero, ciudad, region, pais, cp) = u

            calle  = calle  if calle  is not None else "(sin calle)"
            numero = numero if numero is not None else "-"
            ciudad = ciudad if ciudad is not None else "(sin ciudad)"
            region = region if region is not None else "(sin región)"
            pais   = pais   if pais   is not None else "(sin país)"
            cp     = cp     if cp     is not None else "(sin CP)"
            tel_mostrar = telefono if telefono else "(No registrado)"

            print("\n========== DATOS PERSONALES ==========")
            print(f"Nombre completo:    {nombre} {apellido}")
            print(f"RUT:                {rut}")
            print(f"Email:              {email}")
            print(f"Teléfono:           {tel_mostrar}")
            print(f"Nombre de usuario:  {nombre_usuario}")
            print("\n--- Dirección ---")
            print(f"Calle:              {calle} {numero}")
            print(f"Ciudad/Región:      {ciudad}, {region}")
            print(f"País:               {pais}")
            print(f"Código Postal:      {cp}")
            print("======================================\n")

        except Exception as e:
            print(f"Ocurrió un error al obtener los datos personales: {e}")

    def ver_detalle_laboral(self, cursor):
        """
        Muestra el último estado laboral (según FechaAsignacion más reciente).
        Mantiene tu formato, pero evita crashear si algo viene None.
        """
        try:
            cursor.execute("""
                SELECT 
                    D.FechaContrato,
                    D.Salario,
                    D.TipoEmpleado,
                    Dep.NombreDepartamento,
                    CASE WHEN ED.Activo = TRUE THEN 'En servicio' ELSE 'Desvinculado' END AS Estado
                FROM DetalleEmpleado D
                JOIN EmpleadoDepartamento ED ON D.UsuarioSistema_idUsuarioSistema = ED.UsuarioSistema_idUsuarioSistema
                JOIN Departamento Dep ON ED.Departamento_idDepartamento = Dep.id_Departamento
                WHERE D.UsuarioSistema_idUsuarioSistema = %s
                ORDER BY ED.FechaAsignacion DESC
                LIMIT 1
            """, (self.id_UsuarioSistema,))
            detalle = cursor.fetchone()

            if not detalle:
                print("\nNo tienes historial laboral registrado.\n")
                return

            fecha_contrato = detalle[0] if detalle[0] is not None else "(sin fecha)"
            salario_val = detalle[1] if detalle[1] is not None else 0
            tipo_emp = detalle[2] if detalle[2] else "No especificado"
            depto = detalle[3] if detalle[3] else "(sin departamento)"
            estado = detalle[4] if detalle[4] else "(desconocido)"

            salario_fmt = f"{salario_val:,}".replace(",", ".")
            print("\n===== DETALLE LABORAL =====")
            print(f"Estado:              {estado}")
            print(f"Departamento actual: {depto}")
            print(f"Cargo / Tipo:        {tipo_emp}")
            print(f"Salario:             ${salario_fmt}")
            print(f"Fecha de Contrato:   {fecha_contrato}")
            print("============================\n")

        except Exception as e:
            print(f"Ocurrió un error al obtener detalle laboral: {e}")

    def ver_proyectos(self, cursor):
        try:
            cursor.execute("""
                SELECT 
                    P.NombreProyecto,
                    EP.FechaProyectoInscrito,
                    EP.CantidadHorasEmpleadoProyecto,
                    EP.DescripcionTareaProyecto
                FROM EmpleadoProyecto EP
                JOIN EmpleadoDepartamento ED ON EP.EmpleadoDepartamento_idEmpleadoDepartamento = ED.id_EmpleadoDepartamento
                JOIN Proyecto P ON EP.Proyecto_idProyecto = P.id_Proyecto
                WHERE ED.UsuarioSistema_idUsuarioSistema = %s
                  AND EP.Activo = TRUE
                ORDER BY EP.FechaProyectoInscrito DESC
            """, (self.id_UsuarioSistema,))
            proyectos = cursor.fetchall()

            if not proyectos:
                print("\nActualmente no estás asignado a ningún proyecto activo.")
                return

            print("\n========== PROYECTOS ACTIVOS ==========")
            for p in proyectos:
                nombre = p[0] if p[0] else "(Sin nombre)"
                fecha = p[1] if p[1] else "(Sin fecha)"
                horas = p[2] if p[2] is not None else 0
                tarea = p[3] if p[3] else "(Sin descripción)"
                print(f"""
        Proyecto:          {nombre}
        Fecha Inscripción: {fecha}
        Horas asignadas:   {horas}
        Tarea:             {tarea}
        ----------------------------------""")
            print("======================================\n")

        except Exception as e:
            print(f"Ocurrió un error al consultar tus proyectos: {e}")

    def ver_historial_proyectos(self, cursor):
        try:
            cursor.execute("""
                SELECT 
                    P.NombreProyecto,
                    EP.FechaProyectoInscrito,
                    EP.CantidadHorasEmpleadoProyecto,
                    EP.DescripcionTareaProyecto,
                    CASE WHEN EP.Activo = TRUE THEN 'Activo' ELSE 'Inactivo' END AS Estado
                FROM EmpleadoProyecto EP
                JOIN EmpleadoDepartamento ED ON EP.EmpleadoDepartamento_idEmpleadoDepartamento = ED.id_EmpleadoDepartamento
                JOIN Proyecto P ON EP.Proyecto_idProyecto = P.id_Proyecto
                WHERE ED.UsuarioSistema_idUsuarioSistema = %s
                ORDER BY EP.FechaProyectoInscrito DESC
            """, (self.id_UsuarioSistema,))
            proyectos = cursor.fetchall()

            if not proyectos:
                print("\nNo existe ningún historial de proyectos para tu usuario.")
                return

            print("\n========== HISTORIAL DE PROYECTOS ==========")
            for p in proyectos:
                nombre = p[0] if p[0] else "(Sin nombre)"
                fecha = p[1] if p[1] else "(Sin fecha)"
                horas = p[2] if p[2] is not None else 0
                tarea = p[3] if p[3] else "(Sin descripción)"
                estado = p[4] if p[4] else "(Desconocido)"
                print(f"""
        Proyecto:          {nombre}
        Fecha Inscripción: {fecha}
        Horas asignadas:   {horas}
        Tarea:             {tarea}
        Estado:            {estado}
        ----------------------------------""")
            print("===========================================\n")

        except Exception as e:
            print(f"Ocurrió un error al consultar tu historial de proyectos: {e}")

    def editar_datos_personales(self, cnx, cursor):
        try:
            print("\n--- EDITAR DATOS PERSONALES ---")
            print("Presione ENTER para mantener el valor actual o 0 para cancelar.\n")

            cursor.execute("""
                SELECT 
                    U.Nombre, U.Apellido, U.Email, U.Telefono,
                    D.id_Direccion, D.Calle, D.Numero, D.Ciudad, D.Region, D.Pais, D.CodigoPostal
                FROM UsuarioSistema U
                LEFT JOIN Direccion D ON U.Direccion_idDireccion = D.id_Direccion
                WHERE U.id_UsuarioSistema = %s
            """, (self.id_UsuarioSistema,))
            usuario = cursor.fetchone()

            if not usuario:
                print("Error: No se pudo cargar la información actual.")
                return

            # --- DATOS PERSONALES ---
            nombre = pedir_input(f"Nombre [{usuario[0]}]: ", cnx, opcional=True)
            if nombre is None: return
            nombre = nombre or usuario[0]

            apellido = pedir_input(f"Apellido [{usuario[1]}]: ", cnx, opcional=True)
            if apellido is None: return
            apellido = apellido or usuario[1]

            while True:
                email = pedir_input(f"Email [{usuario[2]}]: ", cnx, opcional=True)
                if email is None: 
                    return
                if not email:
                    email = usuario[2]
                    break
                if validar_email(email):
                    break
                print("Email inválido. Reintente.")

            while True:
                telefono = pedir_input(f"Teléfono [{usuario[3] if usuario[3] else '(vacío)'}]: ", cnx, opcional=True)
                if telefono is None: 
                    return
                if not telefono:
                    telefono = usuario[3]
                    break
                if validar_telefono(telefono):
                    break
                print("Teléfono inválido. Reintente.")

            # --- DIRECCIÓN ---
            print("\n--- EDITAR DIRECCIÓN ---")

            calle = pedir_input(f"Calle [{usuario[5] if usuario[5] else '(vacía)'}]: ", cnx, opcional=True)
            if calle is None: return
            calle = calle or usuario[5]

            while True:
                numero = pedir_input(f"Número [{usuario[6] if usuario[6] else '(sin número)'}]: ", cnx, opcional=True)
                if numero is None: return
                if not numero:
                    numero = usuario[6]
                    break
                try:
                    numero = int(numero)
                    break
                except ValueError:
                    print("Número inválido. Debe ser un número entero.")

            ciudad = pedir_input(f"Ciudad [{usuario[7] if usuario[7] else '(vacía)'}]: ", cnx, opcional=True)
            if ciudad is None: return
            ciudad = ciudad or usuario[7]

            region = pedir_input(f"Región [{usuario[8] if usuario[8] else '(vacía)'}]: ", cnx, opcional=True)
            if region is None: return
            region = region or usuario[8]

            pais = pedir_input(f"País [{usuario[9] if usuario[9] else '(vacío)'}]: ", cnx, opcional=True)
            if pais is None: return
            pais = pais or usuario[9]

            while True:
                codigo_postal = pedir_input(f"Código Postal [{usuario[10] if usuario[10] else '(vacío)'}]: ", cnx, opcional=True)
                if codigo_postal is None: return
                if not codigo_postal:
                    codigo_postal = usuario[10]
                    break
                try:
                    codigo_postal = int(codigo_postal)
                    if codigo_postal < 0 or codigo_postal > 99999999:
                        print("Código postal fuera de rango válido.")
                        continue
                    break
                except ValueError:
                    print("Código postal inválido. Debe ser un número entero.")

            confirmar = pedir_input("¿Desea guardar los cambios? (s/n): ", cnx, opcional=True)
            if confirmar is None or confirmar.lower() not in  ("s", "si"):
                print("Cambios cancelados.")
                return

            # --- ACTUALIZACIÓN ---
            cursor.execute("""
                UPDATE UsuarioSistema
                SET Nombre = %s, Apellido = %s, Email = %s, Telefono = %s
                WHERE id_UsuarioSistema = %s
            """, (nombre, apellido, email, telefono, self.id_UsuarioSistema))

            cursor.execute("""
                UPDATE Direccion
                SET Calle = %s, Numero = %s, Ciudad = %s, Region = %s, Pais = %s, CodigoPostal = %s
                WHERE id_Direccion = %s
            """, (calle, numero, ciudad, region, pais, codigo_postal, usuario[4]))

            cnx.commit()
            print("\nTus datos han sido actualizados correctamente.\n")

        except Exception as e:
            try:
                cnx.rollback()
            except Exception:
                pass
            print(f"Ocurrió un error al editar tus datos: {e}")

    def cambiar_nombre_usuario(self, cnx, cursor):
        try:
            print("\n--- CAMBIAR NOMBRE DE USUARIO ---")
            nuevo_usuario = pedir_input("Nuevo nombre de usuario [0 para cancelar]: ", cnx)
            if nuevo_usuario is None:
                return

            if len(nuevo_usuario.strip()) == 0:
                print("El nombre de usuario no puede estar vacío.")
                return
            if len(nuevo_usuario) > 20:
                print("El nombre de usuario no puede superar los 20 caracteres.")
                return

            # Verificar que no exista otro usuario con el mismo nombre
            cursor.execute("SELECT COUNT(*) FROM UsuarioSistema WHERE NombreUsuario = %s", (nuevo_usuario,))
            if cursor.fetchone()[0] > 0:
                print("Ese nombre de usuario ya está en uso. Elija otro.")
                return

            confirmar = pedir_input(f"¿Confirma cambiar su nombre de usuario a '{nuevo_usuario}'? (s/n): ", cnx, opcional=True)
            if confirmar is None or confirmar.lower() not in ("s", "si"):
                print("Operación cancelada.")
                return

            cursor.execute("""
                UPDATE UsuarioSistema
                SET NombreUsuario = %s
                WHERE id_UsuarioSistema = %s
            """, (nuevo_usuario, self.id_UsuarioSistema))
            cnx.commit()
            print(f"\nNombre de usuario actualizado correctamente a '{nuevo_usuario}'.\n")

        except Exception as e:
            try:
                cnx.rollback()
            except Exception:
                pass
            print(f"Ocurrió un error al cambiar el nombre de usuario: {e}")

    def cambiar_contrasena(self, cnx, cursor):
        try:
            print("\n--- CAMBIAR CONTRASEÑA ---")
            print("Debe ingresar su contraseña actual para continuar.\n")

            contrasena_actual = pedir_contrasena("Contraseña actual [0 para cancelar]: ", cnx)
            if contrasena_actual is None:
                return

            # Verificar la contraseña actual (ya hasheada en BD)
            cursor.execute("""
                SELECT Contraseña FROM UsuarioSistema WHERE id_UsuarioSistema = %s
            """, (self.id_UsuarioSistema,))
            registro = cursor.fetchone()
            if not registro:
                print("Error al obtener la contraseña actual.")
                return

            hash_actual = hashlib.sha256(contrasena_actual.encode()).hexdigest()
            if hash_actual != registro[0]:
                print("Contraseña actual incorrecta.")
                return

            # Nueva contraseña
            while True:
                nueva = pedir_contrasena("Nueva contraseña [0 para cancelar]: ", cnx)
                if nueva is None:
                    return
                if not validar_contrasena(nueva):
                    print("La contraseña debe tener mínimo 8 caracteres, una mayúscula, un número y un símbolo.")
                    continue

                repetir = pedir_contrasena("Repita la nueva contraseña: ", cnx)
                if repetir is None:
                    return
                if nueva != repetir:
                    print("Las contraseñas no coinciden. Intente de nuevo.")
                    continue
                break

            nueva_hash = hashlib.sha256(nueva.encode()).hexdigest()

            cursor.execute("""
                UPDATE UsuarioSistema
                SET Contraseña = %s
                WHERE id_UsuarioSistema = %s
            """, (nueva_hash, self.id_UsuarioSistema))
            cnx.commit()
            print("\nContraseña actualizada correctamente.\n")

        except Exception as e:
            try:
                cnx.rollback()
            except Exception:
                pass
            print(f"Ocurrió un error al cambiar la contraseña: {e}")


    def ver_compañeros(self, cursor):
        """
        Muestra los compañeros de departamento (excepto el propio empleado).
        Si no pertenece a ningún departamento, informa adecuadamente.
        """
        try:
            # Primero obtenemos su departamento activo
            cursor.execute("""
                SELECT Departamento_idDepartamento
                FROM EmpleadoDepartamento
                WHERE UsuarioSistema_idUsuarioSistema = %s
                  AND Activo = TRUE
                LIMIT 1
            """, (self.id_UsuarioSistema,))
            dep = cursor.fetchone()

            if not dep:
                print("\nNo estás asignado actualmente a ningún departamento.")
                return

            id_dep = dep[0]

            # Luego listamos compañeros del mismo departamento
            cursor.execute("""
                SELECT 
                    U.Nombre, U.Apellido, U.Email, U.Telefono, DE.TipoEmpleado
                FROM EmpleadoDepartamento ED
                JOIN UsuarioSistema U ON ED.UsuarioSistema_idUsuarioSistema = U.id_UsuarioSistema
                JOIN DetalleEmpleado DE ON U.id_UsuarioSistema = DE.UsuarioSistema_idUsuarioSistema
                WHERE ED.Departamento_idDepartamento = %s
                  AND ED.Activo = TRUE
                  AND U.id_UsuarioSistema <> %s
                ORDER BY U.Apellido, U.Nombre
            """, (id_dep, self.id_UsuarioSistema))
            compañeros = cursor.fetchall()

            if not compañeros:
                print("\nNo tienes compañeros actualmente en tu departamento.\n")
                return

            print("\n===== COMPAÑEROS DE DEPARTAMENTO =====")
            for c in compañeros:
                nombre = c[0] if c[0] else "(sin nombre)"
                apellido = c[1] if c[1] else ""
                email = c[2] if c[2] else "(sin email)"
                telefono = c[3] if c[3] else "(sin teléfono)"
                tipo = c[4] if c[4] else "(sin cargo)"
                print(f"""
        {nombre} {apellido}
        Cargo: {tipo}
        Email: {email}
        Teléfono: {telefono}
        ----------------------------------""")
            print("=======================================\n")

        except Exception as e:
            print(f"Ocurrió un error al listar tus compañeros: {e}")


    # Nueva función/método

    def ver_datos_personales_gui(self, cursor):
        # Igual que ver_datos_personales() pero retornando texto en lugar de imprimir
        try:
            cursor.execute("""
                SELECT 
                    U.Nombre, U.Apellido, U.RUT, U.Email, U.Telefono, U.NombreUsuario,
                    D.Calle, D.Numero, D.Ciudad, D.Region, D.Pais, D.CodigoPostal
                FROM UsuarioSistema U
                LEFT JOIN Direccion D ON U.Direccion_idDireccion = D.id_Direccion
                WHERE U.id_UsuarioSistema = %s
            """, (self.id_UsuarioSistema,))
            u = cursor.fetchone()

            if not u:
                return "⚠ No se encontraron datos personales."

            (nombre, apellido, rut, email, telefono, nombre_usuario,
            calle, numero, ciudad, region, pais, cp) = u

            texto = f"""
    ======== DATOS PERSONALES ========

    Nombre: {nombre} {apellido}
    RUT: {rut}
    Email: {email}
    Teléfono: {telefono}

    Usuario: {nombre_usuario}

    --- Dirección ---
    Calle: {calle} {numero}
    Ciudad: {ciudad}
    Región: {region}
    País: {pais}
    Código Postal: {cp}

    ================================
    """
            return texto

        except Exception as e:
            return f"Error: {e}"




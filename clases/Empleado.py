from clases.UsuarioSistema import UsuarioSistema


class Empleado(UsuarioSistema):
    def __init__(self, Nombre, Apellido, RUT, Email, Telefono, NombreUsuario, Contraseña, id_Direccion, id_Rol, id_UsuarioSistema=None):
        super().__init__(Nombre, Apellido, RUT, Email, Telefono, NombreUsuario, Contraseña, id_Direccion, id_Rol, id_UsuarioSistema)

    def ver_datos_personales(self, cursor):
        try:
            cursor.execute("""
                SELECT 
                    U.Nombre, U.Apellido, U.RUT, U.Email, U.Telefono, U.NombreUsuario,
                    D.Calle, D.Numero, D.Ciudad, D.Region, D.Pais, D.CodigoPostal
                FROM UsuarioSistema U
                LEFT JOIN Direccion D ON U.Direccion_idDireccion = D.id_Direccion
                WHERE U.id_UsuarioSistema = %s
            """, (self.id_UsuarioSistema,))
            usuario = cursor.fetchone()

            if not usuario:
                print("Error: No se encontraron datos del usuario actual.")
                return

            print("\n========== DATOS PERSONALES ==========")
            print(f"Nombre completo:    {usuario[0]} {usuario[1]}")
            print(f"RUT:                {usuario[2]}")
            print(f"Email:              {usuario[3]}")
            print(f"Teléfono:           {usuario[4] if usuario[4] else '(No registrado)'}")
            print(f"Nombre de usuario:  {usuario[5]}")
            print("\n--- Dirección ---")
            print(f"Calle:              {usuario[6]} {usuario[7]}")
            print(f"Ciudad/Región:      {usuario[8]}, {usuario[9]}")
            print(f"País:               {usuario[10]}")
            print(f"Código Postal:      {usuario[11]}")
            print("======================================\n")

        except Exception as e:
            print(f"Ocurrió un error al obtener los datos personales: {e}")

    def ver_detalle_laboral(self, cursor):
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

            salario_fmt = f"{detalle[1]:,}".replace(",", ".")
            print("\n===== DETALLE LABORAL =====")
            print(f"Estado:              {detalle[4]}")
            print(f"Departamento actual: {detalle[3]}")
            print(f"Cargo / Tipo:        {detalle[2]}")
            print(f"Salario:             ${salario_fmt}")
            print(f"Fecha de Contrato:   {detalle[0]}")
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
                print(f"""
        Proyecto:          {p[0]}
        Fecha Inscripción: {p[1]}
        Horas asignadas:   {p[2]}
        Tarea:             {p[3] if p[3] else '(Sin descripción)'}
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
                print(f"""
        Proyecto:          {p[0]}
        Fecha Inscripción: {p[1]}
        Horas asignadas:   {p[2]}
        Tarea:             {p[3] if p[3] else '(Sin descripción)'}
        Estado:            {p[4]}
        ----------------------------------""")
            print("===========================================\n")

        except Exception as e:
            print(f"Ocurrió un error al consultar tu historial de proyectos: {e}")

    def editar_datos_personales(self, cnx, cursor):
        try:
            print("\n--- EDITAR DATOS PERSONALES ---")
            print("Ingrese los nuevos datos o presione ENTER para mantener el valor actual.")
            print("Ingrese 0 en cualquier momento para cancelar la operación.\n")

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

            nombre = input(f"Nombre [{usuario[0]}]: ").strip()
            if nombre == "0": return
            nombre = nombre or usuario[0]

            apellido = input(f"Apellido [{usuario[1]}]: ").strip()
            if apellido == "0": return
            apellido = apellido or usuario[1]

            email = input(f"Email [{usuario[2]}]: ").strip()
            if email == "0": return
            email = email or usuario[2]

            telefono = input(f"Teléfono [{usuario[3] if usuario[3] else '(vacío)'}]: ").strip()
            if telefono == "0": return
            telefono = telefono or usuario[3]

            print("\n--- EDITAR DIRECCIÓN ---")
            calle = input(f"Calle [{usuario[5]}]: ").strip()
            if calle == "0": return
            calle = calle or usuario[5]

            numero = input(f"Número [{usuario[6]}]: ").strip()
            if numero == "0": return
            numero = int(numero) if numero else usuario[6]

            ciudad = input(f"Ciudad [{usuario[7]}]: ").strip()
            if ciudad == "0": return
            ciudad = ciudad or usuario[7]

            region = input(f"Región [{usuario[8]}]: ").strip()
            if region == "0": return
            region = region or usuario[8]

            pais = input(f"País [{usuario[9]}]: ").strip()
            if pais == "0": return
            pais = pais or usuario[9]

            codigo_postal = input(f"Código Postal [{usuario[10]}]: ").strip()
            if codigo_postal == "0": return
            codigo_postal = int(codigo_postal) if codigo_postal else usuario[10]

            confirmar = input("\n¿Desea guardar los cambios? (s/n): ").strip().lower()
            if confirmar != "s":
                print("Cambios cancelados.")
                return

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

    def ver_compañeros(self, cursor):
        try:
            cursor.execute("""
                SELECT D.id_Departamento, D.NombreDepartamento
                FROM EmpleadoDepartamento ED
                JOIN Departamento D ON ED.Departamento_idDepartamento = D.id_Departamento
                WHERE ED.UsuarioSistema_idUsuarioSistema = %s
                  AND ED.Activo = TRUE
                ORDER BY D.NombreDepartamento
            """, (self.id_UsuarioSistema,))
            departamentos = cursor.fetchall()

            if not departamentos:
                print("\nNo estás actualmente asignado a ningún departamento activo.\n")
                return

            for dep_id, dep_nombre in departamentos:
                cursor.execute("""
                    SELECT U.Nombre, U.Apellido, U.NombreUsuario, DE.TipoEmpleado
                    FROM EmpleadoDepartamento ED
                    JOIN UsuarioSistema U ON ED.UsuarioSistema_idUsuarioSistema = U.id_UsuarioSistema
                    LEFT JOIN DetalleEmpleado DE ON U.id_UsuarioSistema = DE.UsuarioSistema_idUsuarioSistema
                    WHERE ED.Departamento_idDepartamento = %s
                      AND ED.Activo = TRUE
                      AND U.id_UsuarioSistema <> %s
                    ORDER BY U.Nombre, U.Apellido
                """, (dep_id, self.id_UsuarioSistema))
                companeros = cursor.fetchall()

                print(f"\n=== Compañeros en {dep_nombre} ===")
                if not companeros:
                    print("No hay otros compañeros activos en este departamento.")
                else:
                    for c in companeros:
                        tipo = c[3] if c[3] else "No especificado"
                        print(f"- {c[0]} {c[1]}  |  usuario: {c[2]}  |  tipo: {tipo}")
            print()

        except Exception as e:
            print(f"Ocurrió un error al consultar tus compañeros: {e}")


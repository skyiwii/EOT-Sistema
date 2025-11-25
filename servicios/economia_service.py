import os
import requests
from datetime import datetime
from openpyxl import Workbook
from openpyxl.chart import LineChart, Reference
from openpyxl.chart.axis import DateAxis


class EconomiaService:
    """
    Se encarga de:
    - Consultar la API pública de indicadores económicos (findic.cl).
    - Guardar cada consulta en ConsultaEconomica.
    - Leer últimos valores para mostrarlos en el panel de la derecha.
    """

    # Usamos findic.cl
    BASE_URL = "https://findic.cl/api"

    # Mapeo entre el "CodigoIndicador" de tu tabla y la clave del JSON de findic
    #
    # OJO: estos códigos deben existir en la tabla IndicadorEconomico.CodigoIndicador
    # (los sembramos en crear_datos_ejemplo).

    INDICADORES_API = {
        "UF_CLP":              "uf",
        "IVP":                 "ivp",
        "IPC":                 "ipc",
        "UTM_CLP":             "utm",
        "USD_CLP":             "dolar",
        "EUR_CLP":             "euro",
        # opcionales extra
        "USD_INTERCAMBIO_CLP": "dolar_intercambio",
        "IPSA":                "ipsa",
    }

    def __init__(self, cnx, cursor, usuario):
        self.cnx = cnx
        self.cursor = cursor
        self.usuario = usuario  # para guardar quién hizo la consulta

    # -----------------------------------------------
    # 1) Consultar API y registrar en ConsultaEconomica
    # -----------------------------------------------
    def actualizar_desde_api(self):
        """
        Llama a la API de findic.cl una sola vez (resumen diario),
        guarda los valores en ConsultaEconomica
        y devuelve un dict con los últimos valores para cada indicador.
        """
        resultados = {}

        try:
            # 1 llamada para traer TODO el resumen del día
            resp = requests.get(self.BASE_URL, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"[EconomiaService] Error consultando findic.cl: {e}")
            return resultados  # dict vacío

        # Recorremos los indicadores que nos interesan
        for codigo_indicador, json_key in self.INDICADORES_API.items():
            try:
                indicador_data = data.get(json_key)
                if not indicador_data:
                    # Si findic no trajo ese indicador, lo saltamos
                    continue

                # Ejemplo de bloque en JSON:
                # "uf": {
                #   "codigo": "uf",
                #   "nombre": "Unidad de fomento (UF)",
                #   "unidad_medida": "Pesos",
                #   "fecha": "2025-11-24",
                #   "valor": 39643.59
                # }
                valor = float(indicador_data.get("valor", 0))
                fecha_str = indicador_data.get("fecha")

                # Normalizamos fecha: "YYYY-MM-DD" → datetime
                try:
                    fecha_dt = datetime.strptime(fecha_str, "%Y-%m-%d")
                except Exception:
                    # Si por algo falla el parseo, usamos ahora
                    fecha_dt = datetime.now()

                # Buscamos el id del indicador en tu tabla IndicadorEconomico
                self.cursor.execute(
                    """
                    SELECT id_IndicadorEconomico
                    FROM IndicadorEconomico
                    WHERE CodigoIndicador = %s
                    """,
                    (codigo_indicador,),
                )
                row = self.cursor.fetchone()
                if not row:
                    # Si por alguna razón no existe ese Código en la BD, lo saltamos
                    print(f"[EconomiaService] CodigoIndicador '{codigo_indicador}' no existe en BD.")
                    continue

                id_ind = row[0]

                # Insertamos la consulta en ConsultaEconomica
                self.cursor.execute(
                    """
                    INSERT INTO ConsultaEconomica
                        (UsuarioSistema_idUsuarioSistema,
                         IndicadorEconomico_idIndicadorEconomico,
                         FechaConsulta,
                         ParametrosConsulta,
                         ValorPrincipal,
                         Exito,
                         MensajeError,
                         Fuente)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        self.usuario.id_UsuarioSistema,
                        id_ind,
                        fecha_dt,
                        "resumen_diario",
                        valor,
                        True,
                        None,
                        "findic.cl",
                    ),
                )

                resultados[codigo_indicador] = {
                    "valor": valor,
                    "fecha": fecha_dt,
                }

            except Exception as e:
                # Si algo explota con un indicador, no mata a los demás
                print(f"[EconomiaService] Error con {codigo_indicador}: {e}")

        # Intentamos guardar todo
        try:
            self.cnx.commit()
        except Exception:
            self.cnx.rollback()

        return resultados
    

    # -----------------------------------------------
    # 1.b) Consultar HISTÓRICO en la API por periodo
    # -----------------------------------------------
    def consultar_indicador_periodo_api(
        self,
        codigo_indicador: str,
        fecha_desde: str | None = None,
        fecha_hasta: str | None = None,
        registrar_en_bd: bool = False,
    ):
        """
        Consulta la API de findic.cl para UN indicador concreto
        (UF_CLP, IPC, USD_CLP, etc.) usando el endpoint histórico,
        por ejemplo: https://findic.cl/api/uf

        Devuelve una lista de tuplas:
            [(datetime(fecha), valor_float), ...]

        - fecha_desde / fecha_hasta se esperan como 'YYYY-MM-DD' (strings) o None.
        - Si registrar_en_bd=True, cada punto de la serie se guarda en ConsultaEconomica.
        """

        from datetime import datetime

        # 1) Resolver endpoint de la API (uf, ipc, dolar, etc.)
        endpoint = self.INDICADORES_API.get(codigo_indicador)
        if not endpoint:
            raise ValueError(f"Indicador '{codigo_indicador}' no está configurado en INDICADORES_API")

        url = f"{self.BASE_URL}/{endpoint}"

        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            raise RuntimeError(f"Error consultando {url}: {e}")

        # 2) La mayoría de APIs tipo findic/mindicador devuelven una clave 'serie'
        serie_json = data.get("serie")
        if not serie_json:
            # Si no hay 'serie', intentamos ver si viene un solo valor (como en /api)
            # para no rompernos; devolvemos al menos un punto.
            fecha_str = data.get("fecha")
            valor = data.get("valor")
            if fecha_str is None or valor is None:
                return []

            try:
                fecha_dt = datetime.strptime(fecha_str[:10], "%Y-%m-%d")
            except Exception:
                return []

            valor_f = float(valor)
            serie = [(fecha_dt, valor_f)]
        else:
            # 3) Filtramos la serie por el rango de fechas
            serie = []
            # Normalizamos rangos a datetime (solo fecha)
            fecha_desde_dt = None
            fecha_hasta_dt = None
            if fecha_desde:
                fecha_desde_dt = datetime.strptime(fecha_desde, "%Y-%m-%d")
            if fecha_hasta:
                fecha_hasta_dt = datetime.strptime(fecha_hasta, "%Y-%m-%d")

            for punto in serie_json:
                # Cada punto suele ser {"fecha": "2025-11-24", "valor": 39643.59}
                f_str = str(punto.get("fecha", ""))[:10]
                v = punto.get("valor", None)
                if v is None or not f_str:
                    continue

                try:
                    f_dt = datetime.strptime(f_str, "%Y-%m-%d")
                except Exception:
                    continue

                # Aplicar filtros de rango
                if fecha_desde_dt and f_dt < fecha_desde_dt:
                    continue
                if fecha_hasta_dt and f_dt > fecha_hasta_dt:
                    continue

                try:
                    valor_f = float(v)
                except Exception:
                    continue

                serie.append((f_dt, valor_f))

            # Ordenamos por fecha ascendente
            serie.sort(key=lambda x: x[0])

        # 4) Registrar en BD si así se pide
        if registrar_en_bd and serie:
            try:
                # Buscar id del indicador UNA sola vez
                self.cursor.execute(
                    """
                    SELECT id_IndicadorEconomico
                    FROM IndicadorEconomico
                    WHERE CodigoIndicador = %s
                    """,
                    (codigo_indicador,),
                )
                row = self.cursor.fetchone()
                if not row:
                    print(f"[EconomiaService] CodigoIndicador '{codigo_indicador}' no existe en BD.")
                else:
                    id_ind = row[0]
                    # Insertar cada punto de la serie
                    for fecha_dt, valor_f in serie:
                        self.cursor.execute(
                            """
                            INSERT INTO ConsultaEconomica
                                (UsuarioSistema_idUsuarioSistema,
                                 IndicadorEconomico_idIndicadorEconomico,
                                 FechaConsulta,
                                 ParametrosConsulta,
                                 ValorPrincipal,
                                 Exito,
                                 MensajeError,
                                 Fuente)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            """,
                            (
                                self.usuario.id_UsuarioSistema,
                                id_ind,
                                fecha_dt,  # usamos la fecha del indicador como FechaConsulta
                                f"hist_api;{endpoint};{fecha_desde or ''};{fecha_hasta or ''}",
                                valor_f,
                                True,
                                None,
                                "findic.cl",
                            ),
                        )
                    self.cnx.commit()
            except Exception as e:
                print(f"[EconomiaService] Error registrando serie histórica: {e}")
                try:
                    self.cnx.rollback()
                except:
                    pass

        return serie


    # -----------------------------------------------
    # 2) Leer últimos valores guardados en la BD
    # -----------------------------------------------
    def obtener_ultimos_valores(self):
        """
        Devuelve un dict con los últimos valores registrados
        para cada indicador activo.
        {
          "USD_CLP": {"nombre": "...", "valor": 950.0, "fecha": datetime(...)},
          "UF_CLP": {...},
          ...
        }
        """
        self.cursor.execute(
            """
            SELECT 
                i.id_IndicadorEconomico,
                i.CodigoIndicador,
                i.NombreIndicador
            FROM IndicadorEconomico i
            WHERE i.Activo = TRUE
            ORDER BY i.CodigoIndicador
            """
        )

        indicadores = self.cursor.fetchall()

        resultado = {}

        for id_ind, codigo, nombre in indicadores:
            # Subconsulta: último registro en ConsultaEconomica para ese indicador
            self.cursor.execute(
                """
                SELECT ValorPrincipal, FechaConsulta
                FROM ConsultaEconomica
                WHERE IndicadorEconomico_idIndicadorEconomico = %s
                ORDER BY FechaConsulta DESC
                LIMIT 1
                """,
                (id_ind,),
            )

            row = self.cursor.fetchone()
            if not row:
                continue

            valor, fecha = row
            resultado[codigo] = {
                "nombre": nombre,
                "valor": float(valor),
                "fecha": fecha,
            }

        return resultado

    # -----------------------------------------------
    # 3) Exportar historial a Excel
    # -----------------------------------------------
    def exportar_historial_excel(
        self,
        fecha_desde=None,
        fecha_hasta=None,
        codigo_indicador=None,
        incluir_grafico: bool = False,
        solo_usuario_id=None
    ):
        """
        Exporta el historial de consultas económicas a un archivo Excel (.xlsx)
        con filtros opcionales por fecha, indicador y usuario.

        Si incluir_grafico=True y se filtra por UN solo indicador (codigo_indicador != None),
        se inserta un gráfico de línea en la hoja usando la columna de fechas y de valores.
        """

        where_clauses = []
        params = []

        if fecha_desde:
            where_clauses.append("c.FechaConsulta >= %s")
            params.append(f"{fecha_desde} 00:00:00")

        if fecha_hasta:
            where_clauses.append("c.FechaConsulta <= %s")
            params.append(f"{fecha_hasta} 23:59:59")

        if codigo_indicador:
            where_clauses.append("i.CodigoIndicador = %s")
            params.append(codigo_indicador)

        if solo_usuario_id is not None:
            where_clauses.append("c.UsuarioSistema_idUsuarioSistema = %s")
            params.append(solo_usuario_id)

        where_sql = ""
        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses)

        self.cursor.execute(
            f"""
            SELECT 
                c.FechaConsulta,
                i.CodigoIndicador,
                i.NombreIndicador,
                c.ValorPrincipal,
                c.Exito,
                c.MensajeError,
                c.Fuente,
                u.NombreUsuario
            FROM ConsultaEconomica c
            JOIN IndicadorEconomico i
                ON c.IndicadorEconomico_idIndicadorEconomico = i.id_IndicadorEconomico
            JOIN UsuarioSistema u
                ON c.UsuarioSistema_idUsuarioSistema = u.id_UsuarioSistema
            {where_sql}
            ORDER BY c.FechaConsulta ASC
            """,
            tuple(params)
        )
        filas = self.cursor.fetchall()

        if not filas:
            return None

        carpeta = "./informes"
        os.makedirs(carpeta, exist_ok=True)

        wb = Workbook()
        ws = wb.active
        ws.title = "HistorialEconomico"

        encabezados = [
            "Fecha consulta",
            "Código indicador",
            "Nombre indicador",
            "Valor",
            "Éxito",
            "Mensaje error",
            "Fuente",
            "Usuario"
        ]
        ws.append(encabezados)

        for fila in filas:
            fecha, codigo, nombre, valor, exito, msg_err, fuente, usuario = fila
            ws.append([
                fecha.strftime("%Y-%m-%d %H:%M:%S") if fecha else "",
                codigo,
                nombre,
                float(valor) if valor is not None else None,
                bool(exito),
                msg_err,
                fuente,
                usuario
            ])

        # Creamos nombre del archivo
        nombre_archivo = f"hist_economico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        ruta = os.path.join(carpeta, nombre_archivo)

        # Opcional: insertar gráfico sólo si hay un indicador y se pidió
        if incluir_grafico and codigo_indicador and len(filas) > 1:
            chart = LineChart()
            chart.title = f"Serie {codigo_indicador}"
            chart.y_axis.title = "Valor"
            chart.x_axis.title = "Fecha"

            max_row = len(filas) + 1  # +1 por encabezados
            # Columna 4: "Valor" (D)
            data_ref = Reference(ws, min_col=4, min_row=1, max_row=max_row)
            # Columna 1: "Fecha consulta" (A) como categorías
            cats_ref = Reference(ws, min_col=1, min_row=2, max_row=max_row)

            chart.add_data(data_ref, titles_from_data=True)
            chart.set_categories(cats_ref)

            ws.add_chart(chart, "J2")

        wb.save(ruta)
        return ruta


    
    # -----------------------------------------------
    # 4) Obtener serie temporal para un indicador
    # -----------------------------------------------
    def obtener_serie(self, codigo_indicador, fecha_desde=None, fecha_hasta=None,
                      solo_usuario_id=None):
        """
        Devuelve una serie ordenada por fecha para un indicador:

        [
          (datetime(fecha), valor_float),
          ...
        ]

        Los parámetros fecha_desde / fecha_hasta se esperan en formato 'YYYY-MM-DD'
        (como strings). Si son None, no se filtra por ese extremo.

        Si solo_usuario_id no es None, filtra solo las consultas hechas por ese usuario.
        """

        where = ["i.CodigoIndicador = %s"]
        params = [codigo_indicador]

        if fecha_desde:
            where.append("c.FechaConsulta >= %s")
            params.append(f"{fecha_desde} 00:00:00")

        if fecha_hasta:
            where.append("c.FechaConsulta <= %s")
            params.append(f"{fecha_hasta} 23:59:59")

        if solo_usuario_id is not None:
            where.append("c.UsuarioSistema_idUsuarioSistema = %s")
            params.append(solo_usuario_id)

        where_sql = "WHERE " + " AND ".join(where)

        # Agrupamos por día para que el gráfico sea legible
        self.cursor.execute(
            f"""
            SELECT
                DATE(c.FechaConsulta) AS dia,
                AVG(c.ValorPrincipal) AS valor
            FROM ConsultaEconomica c
            JOIN IndicadorEconomico i
                ON c.IndicadorEconomico_idIndicadorEconomico = i.id_IndicadorEconomico
            {where_sql}
            GROUP BY dia
            ORDER BY dia ASC
            """,
            tuple(params)
        )

        filas = self.cursor.fetchall()
        serie = []

        for dia, valor in filas:
            if dia is None or valor is None:
                continue
            # dia ya viene como date/datetime desde MySQL
            if isinstance(dia, str):
                try:
                    dia = datetime.strptime(dia, "%Y-%m-%d")
                except Exception:
                    continue
            serie.append((dia, float(valor)))

        return serie
    

    # -----------------------------------------------
    # 5) Consultar histórico desde la API por período
    # -----------------------------------------------
    def consultar_indicador_periodo_api(
        self,
        codigo_indicador: str,
        fecha_desde: str | None = None,
        fecha_hasta: str | None = None,
        registrar_en_bd: bool = False
    ):
        """
        Consulta la API de findic.cl para UN indicador específico
        (UF_CLP, IVP, IPC, UTM_CLP, USD_CLP, EUR_CLP, etc.)
        usando el endpoint:
            BASE_URL / <clave_json>

        Ejemplo:
            codigo_indicador = "UF_CLP"  ->  GET https://findic.cl/api/uf

        Parámetros:
          - codigo_indicador: debe existir en INDICADORES_API.
          - fecha_desde / fecha_hasta: strings 'YYYY-MM-DD' o None.
          - registrar_en_bd: si True, inserta en ConsultaEconomica
            cada punto del período filtrado.

        Devuelve una lista de tuplas (fecha_datetime, valor_float)
        ORDENADA por fecha ascendente.
        """

        # 1) Resolver clave JSON de la API
        json_key = self.INDICADORES_API.get(codigo_indicador)
        if not json_key:
            raise ValueError(f"Código de indicador no soportado: {codigo_indicador}")

        # 2) Llamar al endpoint histórico, por ejemplo:
        #    https://findic.cl/api/uf
        url = f"{self.BASE_URL}/{json_key}"

        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            raise RuntimeError(f"Error consultando {url}: {e}")

        # 3) Deserializar usando la clase IndicadorSerieFindic
        deserializado = IndicadorSerieFindic(data)

        # 4) Filtrar por rango de fechas en Python
        def parse_fecha_lim(s):
            if not s:
                return None
            return datetime.strptime(s, "%Y-%m-%d").date()

        desde_date = parse_fecha_lim(fecha_desde)
        hasta_date = parse_fecha_lim(fecha_hasta)

        serie_filtrada = []
        for punto in deserializado.serie:
            f = punto["fecha"].date()
            v = punto["valor"]

            if desde_date and f < desde_date:
                continue
            if hasta_date and f > hasta_date:
                continue

            serie_filtrada.append((punto["fecha"], v))

        # 5) Opcional: registrar en la base de datos cada punto
        #    (siempre que haya encontrado el indicador en la tabla).
        if registrar_en_bd and serie_filtrada:
            # buscar id_IndicadorEconomico
            self.cursor.execute(
                """
                SELECT id_IndicadorEconomico
                FROM IndicadorEconomico
                WHERE CodigoIndicador = %s
                """,
                (codigo_indicador,),
            )
            fila = self.cursor.fetchone()
            if fila:
                id_ind = fila[0]
                # Insertar cada registro
                for fecha_valor, valor in serie_filtrada:
                    try:
                        self.cursor.execute(
                            """
                            INSERT INTO ConsultaEconomica
                                (UsuarioSistema_idUsuarioSistema,
                                 IndicadorEconomico_idIndicadorEconomico,
                                 FechaConsulta,
                                 ParametrosConsulta,
                                 ValorPrincipal,
                                 Exito,
                                 MensajeError,
                                 Fuente)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            """,
                            (
                                self.usuario.id_UsuarioSistema,
                                id_ind,
                                fecha_valor,  # aquí guardamos la fecha del valor
                                f"rango={fecha_desde or '-inf'}..{fecha_hasta or '+inf'}",
                                valor,
                                True,
                                None,
                                "findic.cl/api",
                            ),
                        )
                    except Exception as e:
                        print(f"[EconomiaService] Error insertando en BD: {e}")

                try:
                    self.cnx.commit()
                except Exception:
                    self.cnx.rollback()

        # 6) Devolver serie ordenada
        serie_filtrada.sort(key=lambda x: x[0])
        return serie_filtrada



# ----------------------------------------------------------------------
# Clase de deserialización para series de findic.cl
# ----------------------------------------------------------------------
class IndicadorSerieFindic:
    """
    Deserializa la respuesta JSON de endpoints como:
      https://findic.cl/api/uf
      https://findic.cl/api/dolar
      https://findic.cl/api/euro
      https://findic.cl/api/utm
      https://findic.cl/api/ipsa
      etc.

    Se asume el formato descrito en la documentación:
      - clave 'serie': lista de objetos con 'fecha' y 'valor'
      - nombres en español tal como vienen de la API.
    """

    def __init__(self, json_data: dict):
        self.version = json_data.get("version")
        self.autor = json_data.get("autor")
        self.fecha_consulta_api = json_data.get("fecha")  # suele ser fecha "actual" del resumen

        # Algunas respuestas vienen como:
        # { "uf": {...}, "ivp": {...}, ... }
        # y otras como:
        # { "version":..., "autor":..., "serie":[{fecha,valor},...] }
        # Para historical endpoints (uf, dolar, utm, etc.) la doc indica
        # que la key importante es 'serie'.
        self.serie = self._parse_serie(json_data)

    def _parse_serie(self, data):
        """
        Devuelve una lista de dicts homogéneos:
        [{ "fecha": datetime, "valor": float }, ...]
        """
        cruda = data.get("serie")

        # Por seguridad: si no hay 'serie' pero sí hay una lista en otra clave,
        # intentamos detectarla (fallback).
        if cruda is None:
            # buscar la primera lista que parezca serie
            for v in data.values():
                if isinstance(v, list) and v and isinstance(v[0], dict) and "fecha" in v[0]:
                    cruda = v
                    break

        if not cruda:
            return []

        resultado = []
        for punto in cruda:
            fecha_str = punto.get("fecha")
            valor = punto.get("valor")
            if fecha_str is None or valor is None:
                continue
            try:
                fecha_dt = datetime.strptime(fecha_str, "%Y-%m-%d")
                valor_f = float(valor)
            except Exception:
                continue
            resultado.append({"fecha": fecha_dt, "valor": valor_f})

        return resultado



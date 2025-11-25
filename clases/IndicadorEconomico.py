#Table: IndicadorEconomico

#Columns:
#   id_IndicadorEconomico          int AI PK
#   CodigoIndicador                varchar(30) UNIQUE
#   NombreIndicador                varchar(80)
#   MonedaBase                     varchar(10)   -- ej: USD, UF
#   MonedaCotizada                 varchar(10)   -- ej: CLP
#   DescripcionIndicador           varchar(200) NULL
#   Activo                         boolean

class IndicadorEconomico:
    columnas = {
        "id_IndicadorEconomico": "INT NOT NULL AUTO_INCREMENT PRIMARY KEY",
        "CodigoIndicador": "VARCHAR(30) NOT NULL UNIQUE",  # ej: 'USD_CLP', 'UF_CLP'
        "NombreIndicador": "VARCHAR(80) NOT NULL",         # ej: 'Dólar observado', 'UF'
        "MonedaBase": "VARCHAR(10) NOT NULL",              # ej: 'USD', 'UF', 'EUR'
        "MonedaCotizada": "VARCHAR(10) NOT NULL",          # ej: 'CLP'
        "DescripcionIndicador": "VARCHAR(200) NULL",
        "Activo": "BOOLEAN NOT NULL DEFAULT TRUE"
    }

    constraints = [
        # Por ahora sin FKs, solo configuración propia
    ]

    def __init__(self,
                 CodigoIndicador,
                 NombreIndicador,
                 MonedaBase,
                 MonedaCotizada,
                 DescripcionIndicador=None,
                 Activo=True,
                 id_IndicadorEconomico=None):
        self.id_IndicadorEconomico = id_IndicadorEconomico
        self.CodigoIndicador = CodigoIndicador
        self.NombreIndicador = NombreIndicador
        self.MonedaBase = MonedaBase
        self.MonedaCotizada = MonedaCotizada
        self.DescripcionIndicador = DescripcionIndicador
        self.Activo = Activo

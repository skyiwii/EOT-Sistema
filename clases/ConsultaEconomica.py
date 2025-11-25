#Table: ConsultaEconomica

#Columns:
#   id_ConsultaEconomica               int AI PK
#   UsuarioSistema_idUsuarioSistema    int FK -> UsuarioSistema(id_UsuarioSistema)
#   IndicadorEconomico_idIndicadorEconomico int FK -> IndicadorEconomico(id_IndicadorEconomico)
#   FechaConsulta                      datetime
#   ParametrosConsulta                 varchar(255) NULL
#   ValorPrincipal                     decimal(18,6) NULL
#   Exito                              boolean
#   MensajeError                       varchar(255) NULL
#   Fuente                             varchar(80) NULL   -- nombre API, por ejemplo

class ConsultaEconomica:
    columnas = {
        "id_ConsultaEconomica": "INT NOT NULL AUTO_INCREMENT PRIMARY KEY",
        "UsuarioSistema_idUsuarioSistema": "INT NOT NULL",
        "IndicadorEconomico_idIndicadorEconomico": "INT NOT NULL",
        "FechaConsulta": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
        "ParametrosConsulta": "VARCHAR(255) NULL",         # ej: 'rango: último día'
        "ValorPrincipal": "DECIMAL(18,6) NULL",            # valor numérico consultado
        "Exito": "BOOLEAN NOT NULL DEFAULT TRUE",
        "MensajeError": "VARCHAR(255) NULL",
        "Fuente": "VARCHAR(80) NULL"                       # ej: 'mindicador.cl', 'mi_api_banco'
    }

    constraints = [
        "FOREIGN KEY (UsuarioSistema_idUsuarioSistema) "
        "REFERENCES UsuarioSistema(id_UsuarioSistema) ON DELETE CASCADE",

        "FOREIGN KEY (IndicadorEconomico_idIndicadorEconomico) "
        "REFERENCES IndicadorEconomico(id_IndicadorEconomico) ON DELETE RESTRICT"
    ]

    def __init__(self,
                 UsuarioSistema_idUsuarioSistema,
                 IndicadorEconomico_idIndicadorEconomico,
                 ParametrosConsulta=None,
                 ValorPrincipal=None,
                 Exito=True,
                 MensajeError=None,
                 Fuente=None,
                 FechaConsulta=None,
                 id_ConsultaEconomica=None):
        self.id_ConsultaEconomica = id_ConsultaEconomica
        self.UsuarioSistema_idUsuarioSistema = UsuarioSistema_idUsuarioSistema
        self.IndicadorEconomico_idIndicadorEconomico = IndicadorEconomico_idIndicadorEconomico
        self.FechaConsulta = FechaConsulta
        self.ParametrosConsulta = ParametrosConsulta
        self.ValorPrincipal = ValorPrincipal
        self.Exito = Exito
        self.MensajeError = MensajeError
        self.Fuente = Fuente

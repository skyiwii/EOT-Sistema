#Table: DetalleEmpleado

#Columns:
#	id_DetalleEmpleado	int AI PK
#	FechaContrato	datetime
#	Salario	int
#	TipoEmpleado	varchar(45)
#	UsuarioSistema_idUsuarioSistema	int

# -------------------------------------------------------------
# | columnas es para crear estructura si no exiten las tablas |
# -------------------------------------------------------------


class DetalleEmpleado: 
    columnas = {
        "id_DetalleEmpleado": "INT NOT NULL AUTO_INCREMENT PRIMARY KEY",
        "FechaContrato": "datetime NOT NULL DEFAULT CURRENT_TIMESTAMP",
        "Salario": "INT NOT NULL",
        "TipoEmpleado": "VARCHAR(30) DEFAULT 'No especificado'",
        "UsuarioSistema_idUsuarioSistema": "INT NOT NULL"
    }

    constraints = [
         "FOREIGN KEY (UsuarioSistema_idUsuarioSistema) REFERENCES UsuarioSistema(id_UsuarioSistema) ON DELETE CASCADE"
    ]
    
    def __init__(self, FechaContrato, Salario, TipoEmpleado, id_Departamento, id_UsuarioSistema):
        self.FechaContrato = FechaContrato
        self.Salario = Salario
        self.TipoEmpleado = TipoEmpleado
        self.UsuarioSistema_idUsuarioSistema = id_UsuarioSistema

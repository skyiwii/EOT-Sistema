#Table: EmpleadoDepartamento

#Columns:
#	id_EmpleadoDepartamento	int AI PK
#	Departamento_idDepartamento	int
#	UsuarioSistema_idUsuarioSistema	int

class EmpleadoDepartamento:
    columnas = {
        "id_EmpleadoDepartamento": "INT NOT NULL AUTO_INCREMENT PRIMARY KEY",
        "Departamento_idDepartamento": "INT NOT NULL",
        "UsuarioSistema_idUsuarioSistema": "INT NOT NULL",
        "Activo": "BOOLEAN DEFAULT TRUE",
        "FechaAsignacion": "DATETIME DEFAULT CURRENT_TIMESTAMP"
    }

    constraints = [
        "FOREIGN KEY (Departamento_idDepartamento) REFERENCES Departamento(id_Departamento) ON DELETE CASCADE",
        "FOREIGN KEY (UsuarioSistema_idUsuarioSistema) REFERENCES UsuarioSistema(id_UsuarioSistema) ON DELETE CASCADE"
    ]

    def __init__(self, id_Departamento, id_UsuarioSistema, Activo=True, FechaAsignacion=None):
        self.Departamento_idDepartamento = id_Departamento
        self.UsuarioSistema_idUsuarioSistema = id_UsuarioSistema
        self.Activo = Activo
        self.FechaAsignacion = FechaAsignacion

#Table: Informe

#Columns:
#	id_Informe	int AI PK
#	NombreInforme	varchar(35)
#	FechaConsulta	datetime
#	DescripcionInforme	longtext
#	TipoInforme	varchar(45)
#	EmpleadoProyecto_idDetalleProyecto	int

# -------------------------------------------------------------
# | columnas es para crear estructura si no exiten las tablas |
# -------------------------------------------------------------


class Informe: 
    columnas = {
        "id_Informe": "INT NOT NULL AUTO_INCREMENT PRIMARY KEY",
        "NombreInforme": "VARCHAR(100) NOT NULL",
        "FechaConsulta": "datetime NOT NULL DEFAULT CURRENT_TIMESTAMP",
        "DescripcionInforme":"LONGTEXT NULL",
        "TipoInforme": "VARCHAR(45) DEFAULT 'No especificado'",
        "EmpleadoProyecto_idDetalleProyecto": "INT NOT NULL"
    }

    constraints = [
        "FOREIGN KEY (EmpleadoProyecto_idDetalleProyecto) REFERENCES EmpleadoProyecto(id_DetalleProyecto) ON DELETE CASCADE"
    ]
    
    def __init__(self, NombreInforme, FechaConsulta, DescripcionInforme, TipoInforme, id_DetalleProyecto):
        self.NombreInforme = NombreInforme
        self.FechaConsulta = FechaConsulta
        self.DescripcionInforme = DescripcionInforme
        self.TipoInforme = TipoInforme
        self.EmpleadoProyecto_idDetalleProyecto = id_DetalleProyecto
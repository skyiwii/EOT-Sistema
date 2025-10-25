#Table: EmpleadoProyecto

#Columns:
#	id_DetalleProyecto	int AI PK
#	DetalleEmpleado_idDetalleEmpleado	int
#	Proyecto_idProyecto	int
#	FechaProyectoInscrito	datetime
#	CantidadHorasEmpleadoProyecto	int
#	DescripcionTareaProyecto	varchar(45)

# -------------------------------------------------------------
# | columnas es para crear estructura si no exiten las tablas |
# -------------------------------------------------------------

class EmpleadoProyecto: 
    columnas = {
        "id_DetalleProyecto": "INT NOT NULL AUTO_INCREMENT PRIMARY KEY",
        "FechaProyectoInscrito": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
        "CantidadHorasEmpleadoProyecto": "INT NOT NULL",
        "DescripcionTareaProyecto": "TEXT NULL",
        "Activo": "BOOLEAN DEFAULT TRUE",
        "EmpleadoDepartamento_idEmpleadoDepartamento": "INT NOT NULL",
        "Proyecto_idProyecto": "INT NOT NULL"
    }

    constraints = [
        "FOREIGN KEY (EmpleadoDepartamento_idEmpleadoDepartamento) REFERENCES EmpleadoDepartamento(id_EmpleadoDepartamento) ON DELETE CASCADE",
        "FOREIGN KEY (Proyecto_idProyecto) REFERENCES Proyecto(id_Proyecto) ON DELETE CASCADE"
    ]

    def __init__(self, id_EmpleadoDepartamento, id_Proyecto, CantidadHorasEmpleadoProyecto, DescripcionTareaProyecto, FechaProyectoInscrito, Activo=True):
        self.EmpleadoDepartamento_idEmpleadoDepartamento = id_EmpleadoDepartamento
        self.Proyecto_idProyecto = id_Proyecto
        self.CantidadHorasEmpleadoProyecto = CantidadHorasEmpleadoProyecto
        self.DescripcionTareaProyecto = DescripcionTareaProyecto
        self.FechaProyectoInscrito = FechaProyectoInscrito
        self.Activo = Activo

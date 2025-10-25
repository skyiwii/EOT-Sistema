#Table: Proyecto

#Columns:
#	id_Proyecto	int AI PK
#	FechaInicioProyecto	datetime DEFAULT CURRENT_TIMESTAMP
#	DescripcionProyecto	text 
#	NombreProyecto	varchar(20)

# -------------------------------------------------------------
# | columnas es para crear estructura si no exiten las tablas |
# -------------------------------------------------------------

class Proyecto: 


    # para crear las tablas luego

    columnas = {
        "id_Proyecto": "INT NOT NULL AUTO_INCREMENT PRIMARY KEY",
        "FechaInicioProyecto": "DATETIME DEFAULT CURRENT_TIMESTAMP",
        "DescripcionProyecto": "TEXT NULL",
        "NombreProyecto": "VARCHAR(20) NOT NULL"
    }
    
    # constructor para insertar datos en las tablas

    def __init__(self, FechaInicioProyecto, DescripcionProyecto, NombreProyecto):
        self.FechaInicioProyecto = FechaInicioProyecto
        self.DescripcionProyecto = DescripcionProyecto
        self.NombreProyecto = NombreProyecto


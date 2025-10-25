#Table: Departamento

#Columns:
#	id_Departamento	int AI PK
#	NombreDepartamento	varchar(25)
#	TipoDepartamento	varchar(30)
#	DescripcionDepartamento	TEXT
#	Direccion_idDireccion INT Foreign Key REFERENCES id_Direccion DELETE ON CASCADE


# -------------------------------------------------------------
# | columnas es para crear estructura si no exiten las tablas |
# -------------------------------------------------------------

class Departamento: 
    columnas = {
        "id_Departamento": "INT NOT NULL AUTO_INCREMENT PRIMARY KEY",
        "NombreDepartamento": "VARCHAR(25) NOT NULL",
        "TipoDepartamento": "VARCHAR(30) NOT NULL",
        "DescripcionDepartamento": "TEXT NULL",
        "Direccion_idDireccion": "INT NOT NULL"
    }

    constraints = [
        "FOREIGN KEY (Direccion_idDireccion) REFERENCES Direccion(id_Direccion) ON DELETE CASCADE"
    ]
    
    def __init__(self, NombreDepartamento, TipoDepartamento, DescripcionDepartamento, id_Direccion):
        self.NombreDepartamento = NombreDepartamento
        self.TipoDepartamento = TipoDepartamento
        self.DescripcionDepartamento = DescripcionDepartamento
        self.Direccion_idDireccion = id_Direccion
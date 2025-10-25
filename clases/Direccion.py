#Table: Direccion

#Columns:
#	id_Direccion	int AI PK
#	Calle	varchar(45) NOT NULL
#	Numero	INT NOT NULL
#	Ciudad	varchar(45) NOT NULL
#	Region	varchar(45) NOT NULL 
#	Pais	varchar(45) NOT NULL 
#	CodigoPostal INT NOT NULL


# -------------------------------------------------------------
# | columnas es para crear estructura si no exiten las tablas |
# -------------------------------------------------------------

class Direccion: 


    # para crear las tablas luego

    columnas = {
        "id_Direccion": "INT NOT NULL AUTO_INCREMENT PRIMARY KEY",
        "Calle": "VARCHAR(45) NOT NULL",
        "Numero": "INT NOT NULL",
        "Ciudad": "VARCHAR(45) NOT NULL",
        "Region": "VARCHAR(45) NOT NULL",
        "Pais": "VARCHAR(45) NOT NULL",
        "CodigoPostal": "INT NOT NULL"
    }
    
    # constructor para insertar datos en las tablas

    def __init__(self, Calle, Numero, Ciudad, Region, Pais, CodigoPostal):
        self.Calle = Calle
        self.Numero = Numero
        self.Ciudad = Ciudad
        self.Region = Region
        self.Pais = Pais
        self.CodigoPostal = CodigoPostal
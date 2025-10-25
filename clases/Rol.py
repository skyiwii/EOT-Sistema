#Table: Rol

#Columns:
#	id_Rol	int AI PK
#	tipo_Rol ENUM('admin', 'empleado')

# -------------------------------------------------------------
# | columnas es para crear estructura si no exiten las tablas |
# -------------------------------------------------------------

class Rol: 


    # para crear las tablas luego

    columnas = {
        "id_Rol": "INT NOT NULL AUTO_INCREMENT PRIMARY KEY",
        "tipo_Rol": "ENUM('admin','empleado') NOT NULL DEFAULT 'empleado'"
    }
    
    # constructor para insertar datos en las tablas

    def __init__(self, tipo_Rol):
        self.tipo_Rol = tipo_Rol
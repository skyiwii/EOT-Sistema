#Table: UsuarioSistema

#Columns:
#	id_UsuarioSistema	int AI PK
#	Nombre	varchar(50)
#	Apellido	varchar(50)
#	RUT	varchar(12)
#	Email	varchar(100)
#	Telefono	varchar(25)
#	NombreUsuario	varchar(15)
#	Contraseña	varchar(255)
#	Direccion_idDireccion	int
#	Rol_idRol	int




# -------------------------------------------------------------
# | columnas es para crear estructura si no exiten las tablas |
# -------------------------------------------------------------

class UsuarioSistema: 
    columnas = {
        "id_UsuarioSistema": "INT NOT NULL AUTO_INCREMENT PRIMARY KEY",
        "Nombre": "VARCHAR(50) NOT NULL",
        "Apellido": "VARCHAR(50) NOT NULL",
        "RUT": "VARCHAR(12) UNIQUE NOT NULL",
        "Email": "VARCHAR(100) UNIQUE NOT NULL",
        "Telefono": "VARCHAR(25) UNIQUE DEFAULT 'Sin teléfono especificado'",
        "NombreUsuario": "VARCHAR(20) UNIQUE NOT NULL",
        "Contraseña": "VARCHAR(255) NOT NULL",
        "Direccion_idDireccion": "INT NOT NULL",
        "Rol_idRol": "INT NOT NULL"
    }

    constraints = [
        "FOREIGN KEY (Direccion_idDireccion) REFERENCES Direccion(id_Direccion) ON DELETE CASCADE",
        "FOREIGN KEY (Rol_idRol) REFERENCES Rol(id_Rol) ON DELETE CASCADE"
    ]
    
    def __init__(self, id_UsuarioSistema, Nombre, Apellido, RUT, Email, Telefono, NombreUsuario, Contraseña, id_Direccion, id_Rol):
        self.id_UsuarioSistema = id_UsuarioSistema 
        self.Nombre = Nombre
        self.Apellido = Apellido
        self.RUT = RUT
        self.Email = Email
        self.Telefono = Telefono
        self.NombreUsuario = NombreUsuario
        self.Contraseña = Contraseña
        self.Direccion_idDireccion = id_Direccion
        self.Rol_idRol = id_Rol


# Subclases: Admin vs Empleado



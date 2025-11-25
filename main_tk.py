import tkinter as tk
from database.database import (
    conectarBaseDeDatos,
    crearTablas,
    crear_admin,
    crear_datos_ejemplo,
)

from interfaces.login_view import LoginView
from interfaces.dashboard_view import DashboardView

def main():
    cnx, cursor, db_name = conectarBaseDeDatos()
    if not cnx or not cursor:
        print("No se pudo conectar a la BD.")
        return
    
    # 🔹 NUEVO: asegurar estructura y datos base
    crearTablas(cursor)          # crea tablas si no existen
    cnx.commit()
    crear_admin(cnx, cursor)     # crea admin si no existe
    crear_datos_ejemplo(cnx, cursor)  # crea empleado1, deptos, etc.

    root = tk.Tk()
    root.title("Sistema EoTech")
    root.geometry("900x600")

    def on_login_success(usuario_obj, rol):
        login.destroy()  # eliminar pantalla login
        dashboard = DashboardView(root, cnx, cursor, usuario_obj, rol)
        dashboard.pack(fill="both", expand=True)

    login = LoginView(root, cnx, cursor, on_login_success)
    login.pack(fill="both", expand=True)

    root.mainloop()

if __name__ == "__main__":
    main()

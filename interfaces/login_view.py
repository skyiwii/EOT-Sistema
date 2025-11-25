import tkinter as tk
from tkinter import messagebox
from database.database import autenticar_usuario

class LoginView(tk.Frame):
    def __init__(self, master, cnx, cursor, on_login_success, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.cnx = cnx
        self.cursor = cursor
        self.on_login_success = on_login_success  # callback

        self._build_ui()

    def _build_ui(self):
        # ------------------------
        # HEADER: Logo + Empresa
        # ------------------------
        header = tk.Frame(self)
        header.pack(fill="x", pady=10)

        lbl_empresa = tk.Label(header, text="LOGO | Sistema EoTech", font=("Arial", 16, "bold"))
        lbl_empresa.pack()

        # ------------------------
        # CUADRO DEL LOGIN
        # ------------------------
        cont = tk.Frame(self)
        cont.pack(pady=40)

        lbl_login = tk.Label(cont, text="INICIAR SESIÓN", font=("Arial", 14, "bold"))
        lbl_login.pack(pady=(0, 10))

        # Usuario
        tk.Label(cont, text="Usuario").pack(anchor="w")
        self.entry_user = tk.Entry(cont, width=30)
        self.entry_user.pack(pady=5)

        # Contraseña
        tk.Label(cont, text="Contraseña").pack(anchor="w")
        self.entry_pass = tk.Entry(cont, show="*", width=30)
        self.entry_pass.pack(pady=5)

        # Botón login
        btn_login = tk.Button(cont, text="Iniciar sesión", command=self._intentar_login)
        btn_login.pack(pady=15)

        # Que Enter también haga login
        self.entry_pass.bind("<Return>", lambda e: self._intentar_login())

    # ------------------------
    # LÓGICA DE AUTENTICACIÓN
    # ------------------------
    def _intentar_login(self):
        usuario = self.entry_user.get().strip()
        contrasena = self.entry_pass.get().strip()

        if not usuario or not contrasena:
            messagebox.showwarning("Campos vacíos", "Ingrese usuario y contraseña.")
            return

        usuario_obj, rol = autenticar_usuario(usuario, contrasena, self.cursor)

        if usuario_obj is None:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")
            return

        # NO destruir aquí el frame, lo hace el callback:
        self.on_login_success(usuario_obj, rol)


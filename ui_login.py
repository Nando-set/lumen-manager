import flet as ft
from base_datos import GestorNube

class LoginScreen(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.nube = GestorNube()
        self.expand = True
        self.bgcolor = "#F4F6F7"
        self.padding = 40

        # --- CAMPOS DE LOGIN ---
        self.in_user = ft.TextField(label="Usuario", border_radius=15, prefix_icon="person")
        self.in_pin = ft.TextField(label="PIN de acceso", password=True, can_reveal_password=True, border_radius=15, prefix_icon="lock", keyboard_type="number")
        self.chk_recordar = ft.Checkbox(label="Recuérdame en este equipo", value=True)

       # --- CAMPOS DE REGISTRO ---
        self.reg_nombre = ft.TextField(label="Nombre Real (Ej: Carlos)", border_radius=10)
        self.reg_user = ft.TextField(label="Usuario corto (Ej: carlos123)", border_radius=10)
        
        self.reg_pin = ft.TextField(
            label="Crea un PIN de 4 dígitos", border_radius=10, 
            keyboard_type="number", password=True, can_reveal_password=True
        )
        self.reg_codigo = ft.TextField(
            label="Código de Autorización", border_radius=10, 
            password=True, prefix_icon="vpn_key", can_reveal_password=True
        )

        # --- CONTENEDORES ---
        self.panel_login = self.crear_panel_login()
        self.panel_registro = self.crear_panel_registro()
        
        self.content = ft.AnimatedSwitcher(
            self.panel_login,
            transition=ft.AnimatedSwitcherTransition.FADE,
            duration=500
        )

    def crear_panel_login(self):
        return ft.Column([
            # 🔥 AQUÍ INYECTAMOS TU LOGO REAL EN LUGAR DEL ÍCONO
            ft.Image(
                src="logo.png", # Asegúrate de que tu archivo en la carpeta assets se llame así (o cámbialo aquí a .ico si es necesario)
                width=150,      # Tamaño ajustado, puedes subirlo a 200 si lo ves muy pequeño
                height=150,
                fit=ft.ImageFit.CONTAIN,
            ),
            ft.Text("MODA SPACIO", size=30, weight="bold", color="#212F3D"),
            ft.Text("System 2.0", size=16, color="grey"),
            ft.Divider(height=30, color="transparent"),
            self.in_user, self.in_pin, self.chk_recordar,
            ft.Divider(height=10, color="transparent"),
            ft.ElevatedButton("INICIAR SESIÓN", width=300, height=50, style=ft.ButtonStyle(bgcolor="#212F3D", color="white"), on_click=self.iniciar_sesion),
            ft.TextButton("¿Eres nuevo? Regístrate aquí", on_click=lambda _: self.cambiar_vista(self.panel_registro))
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    def crear_panel_registro(self):
        return ft.Column([
            ft.Text("Registro de Personal", size=24, weight="bold", color="#212F3D"),
            ft.Text("Pide el código de autorización a tu gerente.", color="grey", size=12),
            ft.Divider(height=20, color="transparent"),
            self.reg_nombre, self.reg_user, self.reg_pin, self.reg_codigo,
            ft.Divider(height=10, color="transparent"),
            ft.ElevatedButton("CREAR CUENTA", width=300, height=50, style=ft.ButtonStyle(bgcolor="#28B463", color="white"), on_click=self.procesar_registro),
            ft.TextButton("Volver al Login", on_click=lambda _: self.cambiar_vista(self.panel_login))
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    def cambiar_vista(self, vista):
        self.content = vista
        self.update()

    def iniciar_sesion(self, e):
        exito, datos_user = self.nube.verificar_login(self.in_user.value, self.in_pin.value)
        if exito:
            # 1. Guardar en memoria de sesión
            self.page.session.set("usuario_actual", datos_user['nombre_real'])
            self.page.session.set("rol_actual", datos_user['rol'])
            
            # 2. Persistencia si marcó "Recuérdame"
            if self.chk_recordar.value:
                self.page.client_storage.set("sesion_modaspacio", datos_user)
            else:
                self.page.client_storage.remove("sesion_modaspacio") # Limpia por si acaso
                
            self.page.go('/home')
        else:
            self.page.snack_bar = ft.SnackBar(ft.Text("❌ Usuario o PIN incorrecto"), bgcolor="red")
            self.page.snack_bar.open = True
            self.page.update()

    def procesar_registro(self, e):
        exito, msj = self.nube.registrar_usuario(self.reg_nombre.value, self.reg_user.value, self.reg_pin.value, self.reg_codigo.value)
        color_snack = "green" if exito else "red"
        self.page.snack_bar = ft.SnackBar(ft.Text(msj), bgcolor=color_snack)
        self.page.snack_bar.open = True
        if exito: self.cambiar_vista(self.panel_login)
        self.page.update()
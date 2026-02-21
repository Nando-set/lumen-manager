import flet as ft

class Home(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.padding = 20

        # Botón para ir al cotizador
        self.btn_cotizar = ft.ElevatedButton(
            content=ft.Row([ft.Icon(ft.icons.CALCULATE), ft.Text("NUEVA COTIZACIÓN", weight="bold")], alignment=ft.MainAxisAlignment.CENTER),
            bgcolor="#2E86C1", color="white", height=60, width=400,
            on_click=lambda _: self.page.go('/cotizador')
        )
        
        # Botón para ir al inventario
        self.btn_inventario = ft.ElevatedButton(
            content=ft.Row([ft.Icon(ft.icons.INVENTORY), ft.Text("INVENTARIO Y PRECIOS", weight="bold")], alignment=ft.MainAxisAlignment.CENTER),
            bgcolor="#8E44AD", color="white", height=60, width=400,
            on_click=lambda _: self.page.go('/inventario')
        )

        # 🔥 NUEVO BOTÓN: AGENDA DE INSTALACIONES
        self.btn_agenda = ft.ElevatedButton(
            content=ft.Row([ft.Icon(ft.icons.CALENDAR_MONTH), ft.Text("AGENDA DE INSTALACIONES", weight="bold")], alignment=ft.MainAxisAlignment.CENTER),
            bgcolor="#E67E22", color="white", height=60, width=400,
            on_click=lambda _: self.page.go('/agenda')
        )

        self.content = ft.Column([
            ft.Text("LUMEN MANAGER", size=24, weight="bold", color="#212F3D"),
            ft.Text("Menú Principal", color="grey", size=14),
            ft.Divider(height=30, color="transparent"),
            
            self.btn_cotizar,
            ft.Divider(height=10, color="transparent"),
            self.btn_inventario,
            ft.Divider(height=10, color="transparent"),
            self.btn_agenda # <- Lo inyectamos aquí en la pantalla
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
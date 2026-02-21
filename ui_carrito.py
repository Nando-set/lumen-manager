import flet as ft
from base_datos import GestorNube

class CarritoCompras(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.nube = GestorNube()
        self.expand = True
        self.padding = 10

        # --- LISTA DONDE CAERÁN LOS PRODUCTOS AGREGADOS ---
        self.lista_carrito = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
        
        # --- TOTALES ---
        self.lbl_total = ft.Text("$0.00", size=24, weight="bold", color="#28B463")

        # ==========================================
        # 1. CONTROLES PESTAÑA AUTOMÁTICOS (PERSIANAS)
        # ==========================================
        self.drop_auto = ft.Dropdown(label="Seleccionar Persiana", expand=True)
        self.in_ancho = ft.TextField(label="Ancho (m)", width=100, keyboard_type="number")
        self.in_alto = ft.TextField(label="Alto (m)", width=100, keyboard_type="number")
        self.in_cant_auto = ft.TextField(label="Cant.", value="1", width=70, keyboard_type="number")
        
        panel_auto = ft.Column([
            self.drop_auto,
            ft.Row([self.in_ancho, self.in_alto, self.in_cant_auto], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.ElevatedButton("AGREGAR AL CARRITO", bgcolor="#2E86C1", color="white", icon=ft.icons.ADD_SHOPPING_CART, width=float('inf'))
        ])

        # ==========================================
        # 2. CONTROLES PESTAÑA MANUALES
        # ==========================================
        self.drop_manual = ft.Dropdown(label="Seleccionar Producto Manual", expand=True)
        self.in_precio_manual = ft.TextField(label="Precio a cobrar ($)", width=150, prefix_text="$", keyboard_type="number")
        self.in_cant_manual = ft.TextField(label="Cant.", value="1", width=100, keyboard_type="number")
        
        panel_manual = ft.Column([
            self.drop_manual,
            ft.Row([self.in_precio_manual, self.in_cant_manual], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.ElevatedButton("AGREGAR AL CARRITO", bgcolor="#28B463", color="white", icon=ft.icons.ADD_SHOPPING_CART, width=float('inf'))
        ])

        # ==========================================
        # 3. CONTROLES PESTAÑA TOLDOS RETRÁCTILES
        # ==========================================
        self.drop_toldos = ft.Dropdown(
            label="Medida del Toldo", 
            options=[
                ft.dropdown.Option("Toldo 3.95 x 3.00"),
                ft.dropdown.Option("Toldo 5.95 x 3.50")
            ], expand=True
        )
        self.switch_motor = ft.Switch(label="Incluir Motor (+ Costo Extra)", value=False)
        self.in_cant_toldo = ft.TextField(label="Cant.", value="1", width=100, keyboard_type="number")
        
        panel_toldos = ft.Column([
            self.drop_toldos,
            ft.Row([self.switch_motor, self.in_cant_toldo], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.ElevatedButton("AGREGAR AL CARRITO", bgcolor="#D35400", color="white", icon=ft.icons.ADD_SHOPPING_CART, width=float('inf'))
        ])

        # --- PESTAÑAS DEL SELECTOR ---
        self.tabs_agregar = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(text="🤖 A Medida", content=ft.Container(padding=10, content=panel_auto)),
                ft.Tab(text="✍️ Manual", content=ft.Container(padding=10, content=panel_manual)),
                ft.Tab(text="🏕️ Toldos", content=ft.Container(padding=10, content=panel_toldos)),
            ]
        )

        # --- ARMADO FINAL DE LA PANTALLA ---
        self.content = ft.Column([
            ft.Row([
                ft.Icon(ft.icons.SHOPPING_BASKET, size=30, color="#212F3D"),
                ft.Text("NUEVA VENTA", size=22, weight="bold", color="#212F3D")
            ]),
            ft.Divider(height=10, color="transparent"),
            
            # El cuadro para agregar cosas
            ft.Container(
                bgcolor="white", border_radius=10, padding=5,
                shadow=ft.BoxShadow(blur_radius=5, color=ft.colors.with_opacity(0.1, "black")),
                content=self.tabs_agregar
            ),
            
            ft.Divider(height=15, color="grey"),
            ft.Text("🛒 TUS PRODUCTOS:", weight="bold"),
            
            # Aquí van los items agregados
            self.lista_carrito,
            
            ft.Divider(height=10, color="grey"),
            
            # Footer del total
            ft.Container(
                padding=15, bgcolor="#212F3D", border_radius=10,
                content=ft.Row([
                    ft.Text("TOTAL NETO:", size=18, weight="bold", color="white"),
                    self.lbl_total
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ),
            
            ft.ElevatedButton("PROCEDER AL COBRO", bgcolor="#8E44AD", color="white", height=50, width=float('inf'))

        ], expand=True)

        # Cargar los nombres en los dropdowns al abrir
        self.cargar_listas_desplegables()

    def cargar_listas_desplegables(self):
        # Esta función alimentará los Dropdowns desde la nube
        # Por ahora ponemos unos de prueba para que veas el diseño
        self.drop_auto.options = [ft.dropdown.Option("Persiana Sheer"), ft.dropdown.Option("Toldo Vertical")]
        self.drop_manual.options = [ft.dropdown.Option("Motor Tubo 45mm"), ft.dropdown.Option("Pasto Sintético")]
        self.page.update()
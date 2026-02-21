import flet as ft
from motor_calculo import MotorCalculo
from base_datos import GestorNube
import math 

class Cotizador(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.motor = MotorCalculo()
        
        # --- CURA PARA LA AMNESIA: Cargar de la sesión ---
        self.carrito = self.page.session.get("carrito") or []
        self.total_venta = self.page.session.get("total_venta") or 0.0
        # 🤫 NUEVA VARIABLE SECRETA: El costo de fábrica total
        self.costo_fabrica_total = self.page.session.get("costo_fabrica_total") or 0.0
        
        self.expand = True
        self.padding = 10

        self.nube = GestorNube()
        productos_nube = self.nube.obtener_productos()
        
        if productos_nube:
            self.productos_auto = productos_nube
        else:
            self.productos_auto = {"Sin conexión a Nube": {"precio": 0.0, "limite_ancho": 2.5, "costo_instalacion": 0.0, "precio_fabrica": 0.0}}

        # ==========================================
        # 1. CONTROLES PESTAÑA AUTOMÁTICO (OPTIMIZADOS PARA MÓVIL 📱)
        # ==========================================
        self.dd_producto = ft.Dropdown(label="Seleccionar Persiana", options=[ft.dropdown.Option(k) for k in self.productos_auto.keys()], expand=True, on_change=self.al_cambiar_producto, label_style=ft.TextStyle(weight="bold"))
        
        # 🔥 EL SECRETO: Quitamos los 'width' fijos y usamos 'expand=True' para que se adapten como líquido
        self.in_precio_base = ft.TextField(label="Precio m2", read_only=True, prefix_text="$", text_style=ft.TextStyle(color="#C0392B", weight="bold", size=13), label_style=ft.TextStyle(weight="bold", size=12), expand=True)
        self.in_ancho = ft.TextField(label="Ancho (m)", keyboard_type="number", on_change=self.calcular_piezas_auto, text_style=ft.TextStyle(weight="bold", size=14), label_style=ft.TextStyle(weight="bold", color="#2980B9", size=12), expand=True)
        self.in_alto = ft.TextField(label="Alto (m)", keyboard_type="number", text_style=ft.TextStyle(weight="bold", size=14), label_style=ft.TextStyle(weight="bold", color="#2980B9", size=12), expand=True)
        
        self.in_espacios = ft.TextField(label="Espacios", value="1", keyboard_type="number", on_change=self.calcular_piezas_auto, text_style=ft.TextStyle(weight="bold", size=14), expand=True)
        self.in_pzas_inst = ft.TextField(label="Pzas (Inst)", value="1", keyboard_type="number", text_style=ft.TextStyle(color="red", weight="bold", size=14), expand=True)

        panel_auto = ft.Column([
            self.dd_producto,
            ft.Row([self.in_precio_base, self.in_ancho, self.in_alto], spacing=10),
            ft.Row([self.in_espacios, self.in_pzas_inst], spacing=10),
            ft.ElevatedButton("AGREGAR AL CARRITO", bgcolor="#2E86C1", color="white", on_click=self.agregar_auto, width=float('inf'))
        ], spacing=15)

        # ==========================================
        # 2. CONTROLES PESTAÑA TOLDOS
        # ==========================================
        self.drop_toldos = ft.Dropdown(label="Medida del Toldo", options=[ft.dropdown.Option("Toldo 3.95 x 3.00"), ft.dropdown.Option("Toldo 5.95 x 3.50")], expand=True)
        self.switch_motor = ft.Switch(label="Incluir Motor", value=False, expand=True)
        self.in_cant_toldo = ft.TextField(label="Cant.", value="1", keyboard_type="number", expand=True)

        panel_toldos = ft.Column([
            self.drop_toldos,
            ft.Row([self.switch_motor, self.in_cant_toldo], spacing=10),
            ft.ElevatedButton("AGREGAR TOLDO", bgcolor="#D35400", color="white", on_click=self.agregar_toldo, width=float('inf'))
        ], spacing=15)

        # 🚀 TABS LIMPIOS (Altura aumentada a 320 para que quepa todo en el celular sin cortarse)
        self.tabs = ft.Tabs(
            selected_index=0, animation_duration=300, height=320,
            tabs=[
                ft.Tab(text="🤖 Automático", content=ft.Container(padding=10, content=panel_auto)),
                ft.Tab(text="🏕️ Toldos", content=ft.Container(padding=10, content=panel_toldos))
            ]
        )

        self.lista_ui = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
        self.lbl_total = ft.Text(f"${self.total_venta:,.2f}", size=24, weight="bold", color="white")
        
        # --- EL BOTÓN DE LIMPIAR ---
        self.btn_limpiar = ft.IconButton(icon=ft.icons.DELETE_SWEEP, icon_color="red", tooltip="Vaciar todo el carrito", on_click=self.limpiar_carrito)

        # 🔥 Agregamos ScrollMode.AUTO a la columna principal para pantallas pequeñas
        self.content = ft.Column([
            ft.Row([ft.Icon(ft.icons.SHOPPING_BASKET, size=30, color="#212F3D"), ft.Text("NUEVA VENTA", size=22, weight="bold", color="#212F3D")]),
            ft.Container(bgcolor="white", border_radius=10, padding=5, shadow=ft.BoxShadow(blur_radius=5, color=ft.colors.with_opacity(0.1, "black")), content=self.tabs),
            ft.Text("🛒 TUS PRODUCTOS:", weight="bold"),
            ft.Container(content=self.lista_ui, border=ft.border.all(1, "#E5E7E9"), border_radius=10, padding=10, expand=True),
            
            # FOOTER CON EL BOTÓN INCLUIDO
            ft.Container(bgcolor="#212F3D", padding=15, border_radius=10, content=ft.Row([
                ft.Text("TOTAL NETO:", size=16, weight="bold", color="white"), 
                ft.Row([self.lbl_total, self.btn_limpiar])
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)),
            
            ft.ElevatedButton("PROCEDER AL COBRO", bgcolor="#8E44AD", color="white", height=50, width=float('inf'), on_click=self.ir_a_checkout)
        ], expand=True, scroll=ft.ScrollMode.AUTO)

        self.reconstruir_carrito_visual()

    # --- LÓGICA DE MEMORIA (SESIÓN) ---
    def guardar_en_memoria(self):
        self.page.session.set("carrito", self.carrito)
        self.page.session.set("total_venta", self.total_venta)
        self.page.session.set("costo_fabrica_total", self.costo_fabrica_total) 

    def limpiar_carrito(self, e):
        self.carrito.clear()
        self.total_venta = 0.0
        self.costo_fabrica_total = 0.0 
        self.lbl_total.value = "$0.00"
        self.lista_ui.controls.clear()
        self.guardar_en_memoria()
        self.page.update()

    def reconstruir_carrito_visual(self):
        self.lista_ui.controls.clear()
        for item in self.carrito:
            self._dibujar_fila(item)

    # --- LÓGICA DE CÁLCULOS ---
    def al_cambiar_producto(self, e):
        nombre = self.dd_producto.value
        if nombre and nombre in self.productos_auto:
            precio = self.productos_auto[nombre].get("precio", 0.0) 
            self.in_precio_base.value = f"{precio}"
            self.calcular_piezas_auto(e)
        self.page.update()

    def calcular_piezas_auto(self, e):
        nombre = self.dd_producto.value
        if not nombre or nombre == "Sin conexión a Nube": return
        try:
            ancho = float(self.in_ancho.value) if self.in_ancho.value else 0.0
            espacios = int(self.in_espacios.value) if self.in_espacios.value else 1
        except ValueError: return

        if "cortin" in nombre.lower():
            divisiones_base = 1
        else:
            datos = self.productos_auto.get(nombre, {})
            limite = float(datos.get("limite_ancho", 2.5))
            if limite <= 0: limite = 2.5 
            divisiones_base = math.ceil(ancho / limite) if ancho > 0 else 1
                
        self.in_pzas_inst.value = str(divisiones_base * espacios)
        self.page.update()

    # --- AGREGAR PRODUCTOS ---
    def agregar_auto(self, e):
        nombre = self.dd_producto.value
        if not nombre or nombre == "Sin conexión a Nube": return
        try:
            ancho = float(self.in_ancho.value)
            alto = float(self.in_alto.value)
            espacios = int(self.in_espacios.value)
            pzas_fisicas = int(self.in_pzas_inst.value) 
            datos_producto = self.productos_auto[nombre]
            precio_base = float(datos_producto.get("precio", 0.0))
            costo_inst = float(datos_producto.get("costo_instalacion", 0.0))
            
            precio_fabrica_m2 = float(datos_producto.get("precio_fabrica", 0.0))
            
        except Exception as err: 
            self.page.snack_bar = ft.SnackBar(ft.Text("Revisa los campos numéricos"), bgcolor="red")
            self.page.snack_bar.open = True
            self.page.update()
            return
            
        area = ancho * alto
        total_linea = (area * precio_base * espacios) + (costo_inst * pzas_fisicas)
        
        costo_fabrica_linea = (area * precio_fabrica_m2 * espacios)
        
        desc = f"{nombre} ({ancho}x{alto}m)"
        if espacios > 1: desc += f" x{espacios} esp"
        desc += f" | Inst: {pzas_fisicas} pzas"
        
        self._registrar_item(desc, total_linea, costo_fabrica_linea)
        
        self.in_ancho.value = ""
        self.in_alto.value = ""
        self.in_espacios.value = "1"
        self.in_pzas_inst.value = "1"
        self.page.update()

    # 🔥 FUNCIÓN DE TOLDOS RESTAURADA
    def agregar_toldo(self, e):
        modelo = self.drop_toldos.value
        if not modelo: return
        try: cant = int(self.in_cant_toldo.value)
        except: return
        precio_unitario = 13500.0 if "3.95" in modelo else 16500.0
        if self.switch_motor.value:
            precio_unitario += 3500.0
            modelo += " (+ Motor)"
        
        # Ojo: Toldos los pasamos con costo de fábrica 0 por ahora (lo puedes cambiar después)
        self._registrar_item(f"[Toldo] {modelo} (x{cant})", precio_unitario * cant, 0.0)
        
        self.in_cant_toldo.value = "1"
        self.switch_motor.value = False
        self.page.update()

    def ir_a_checkout(self, e):
        if not self.carrito:
            self.page.snack_bar = ft.SnackBar(ft.Text("El carrito está vacío"), bgcolor="red")
            self.page.snack_bar.open = True
            self.page.update()
            return
        self.guardar_en_memoria()
        self.page.go('/checkout')

    # --- DIBUJO Y REGISTRO ---
    def _registrar_item(self, descripcion, subtotal, costo_fabrica_item=0.0):
        item_data = {"desc": descripcion, "subtotal": subtotal, "costo_fabrica": costo_fabrica_item}
        self.carrito.append(item_data)
        
        self.total_venta += subtotal
        self.costo_fabrica_total += costo_fabrica_item 
        
        self.lbl_total.value = f"${self.total_venta:,.2f}"
        self.guardar_en_memoria() 
        self._dibujar_fila(item_data)
        self.page.update()

    def _dibujar_fila(self, item_data):
        item_row = ft.Container(padding=10, border_radius=8, bgcolor="white", shadow=ft.BoxShadow(blur_radius=2, color=ft.colors.with_opacity(0.1, "black")))
        
        def borrar_este_item(e):
            self.carrito.remove(item_data)
            self.lista_ui.controls.remove(item_row)
            self.total_venta -= item_data["subtotal"]
            self.costo_fabrica_total -= item_data.get("costo_fabrica", 0.0)
            self.lbl_total.value = f"${self.total_venta:,.2f}"
            self.guardar_en_memoria()
            self.page.update()

        item_row.content = ft.Row([
            ft.Text(item_data["desc"], size=13, expand=True, weight="bold"), 
            ft.Text(f"${item_data['subtotal']:,.2f}", weight="bold", color="#2E86C1"), 
            ft.IconButton(icon="delete", icon_color="red", on_click=borrar_este_item)
        ])
        self.lista_ui.controls.append(item_row)
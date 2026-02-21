import flet as ft
from base_datos import GestorNube

class Inventario(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.nube = GestorNube()
        self.expand = True
        self.padding = 20

        # --- PESTAÑAS DE NAVEGACIÓN (AHORA SOLO 2) ---
        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(text="Persianas", icon=ft.icons.BLINDS),
                ft.Tab(text="Toldos y Motores", icon=ft.icons.STOREFRONT),
            ],
            on_change=lambda _: self.cargar_datos() 
        )

        # --- CAMPOS DEL FORMULARIO ---
        self.id_actual = None
        self.in_nombre = ft.TextField(label="Nombre del Producto", border_radius=10)
        
        self.in_categoria = ft.Dropdown(
            label="Categoría Exacta", border_radius=10,
            options=[
                ft.dropdown.Option("Persiana"),
                ft.dropdown.Option("Toldo"),
                ft.dropdown.Option("Motor")
            ]
        )
        
        self.in_precio = ft.TextField(label="Precio Público ($)", keyboard_type="number", border_radius=10, prefix_icon="attach_money", border_color="#28B463")
        self.in_precio_fabrica = ft.TextField(label="Costo Fábrica ($) [Oculto]", keyboard_type="number", border_radius=10, prefix_icon="factory", border_color="#D35400", color="#D35400")
        
        self.in_costo_instalacion = ft.TextField(label="Costo Instalación ($)", keyboard_type="number", border_radius=10, prefix_icon="build")
        self.in_limite_ancho = ft.TextField(label="Límite de ancho (m)", keyboard_type="number", border_radius=10, prefix_icon="straighten")
        self.in_precio_2 = ft.TextField(label="Precio 2 (Excedentes) ($)", keyboard_type="number", border_radius=10)
        self.in_limite_precio_2 = ft.TextField(label="Límite Precio 2 (m)", keyboard_type="number", border_radius=10)

        self.lista_productos = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

        self.modal = ft.AlertDialog(
            title=ft.Text("Datos del Producto", weight="bold"),
            content=ft.Container(
                width=320, height=450, 
                content=ft.Column([
                    self.in_nombre, self.in_categoria,
                    ft.Divider(height=10, color="transparent"),
                    ft.Text("PRECIOS PRINCIPALES", weight="bold", size=12, color="grey"),
                    self.in_precio, self.in_precio_fabrica,
                    ft.Divider(height=10, color="transparent"),
                    ft.Text("REGLAS DE CÁLCULO (Opcionales)", weight="bold", size=12, color="grey"),
                    self.in_costo_instalacion, self.in_limite_ancho, self.in_precio_2, self.in_limite_precio_2
                ], scroll=ft.ScrollMode.AUTO, tight=True, spacing=10)
            ),
            actions=[
                ft.IconButton(icon="delete", icon_color="red", on_click=self.eliminar_desde_modal, tooltip="Eliminar Producto"),
                ft.Row([
                    ft.TextButton("Cancelar", on_click=self.cerrar_modal),
                    ft.ElevatedButton("Guardar", on_click=self.guardar_producto, bgcolor="#212F3D", color="white")
                ])
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        self.content = ft.Column([
            ft.Row([
                ft.Text("INVENTARIO", size=22, weight="bold", color="#212F3D"),
                ft.ElevatedButton("Nuevo", icon="add", on_click=self.abrir_modal_nuevo, bgcolor="#212F3D", color="white")
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Text("🔒 Toca un producto para editarlo. Costos ocultos a vendedores.", color="grey", size=12),
            self.tabs,
            ft.Divider(height=10, color="transparent"),
            self.lista_productos
        ], expand=True)

        self.cargar_datos()

    def cargar_datos(self):
        self.lista_productos.controls.clear()
        try:
            res = self.nube.supabase.table("productos").select("*").order("nombre").execute()
            datos = res.data
        except Exception as e:
            print(f"Error cargando datos: {e}")
            datos = []

        indice_pestana = self.tabs.selected_index
        datos_filtrados = []
        
        for prod in datos:
            tipo = prod.get('tipo', 'Persiana')
            # Pestaña 0: Persianas. Pestaña 1: Toldos y Motores
            if indice_pestana == 0 and tipo == 'Persiana':
                datos_filtrados.append(prod)
            elif indice_pestana == 1 and tipo in ['Toldo', 'Motor']:
                datos_filtrados.append(prod)

        for prod in datos_filtrados:
            val_pub = prod.get('precio_base')
            val_fab = prod.get('precio_fabrica')
            
            precio_pub = float(val_pub) if val_pub is not None else 0.0
            precio_fab = float(val_fab) if val_fab is not None else 0.0
            
            tipo = prod.get('tipo', 'Persiana')
            icono_cat = ft.icons.BLINDS if tipo == 'Persiana' else ft.icons.STOREFRONT if tipo == 'Toldo' else ft.icons.SETTINGS_INPUT_COMPONENT
            color_cat = "#3498DB" if tipo == 'Persiana' else "#E67E22" if tipo == 'Toldo' else "#9B59B6"
            
            tarjeta = ft.Container(
                padding=15, bgcolor="white", border_radius=10,
                border=ft.border.all(1, "#E5E7E9"),
                shadow=ft.BoxShadow(blur_radius=4, color=ft.colors.with_opacity(0.1, "black")),
                on_click=lambda _, p=prod: self.abrir_modal_editar(p), 
                content=ft.Row([
                    ft.Container(
                        width=40, height=40, bgcolor=ft.colors.with_opacity(0.1, color_cat), border_radius=20,
                        alignment=ft.alignment.center, content=ft.Icon(icono_cat, color=color_cat, size=20)
                    ),
                    ft.Column([
                        ft.Text(prod.get('nombre', 'Sin Nombre'), weight="bold", size=15),
                        ft.Text(tipo, size=11, color="grey"),
                    ], expand=True, spacing=2),
                    
                    ft.Column([
                        ft.Text(f"Pub: ${precio_pub:,.2f}", weight="bold", color="#28B463", size=12),
                        ft.Text(f"Fab: ${precio_fab:,.2f}", weight="bold", color="#D35400", size=11),
                    ], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=2),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            )
            self.lista_productos.controls.append(tarjeta)
        
        if not self.lista_productos.controls:
            self.lista_productos.controls.append(ft.Text("No hay productos en esta categoría.", color="grey", italic=True))
            
        self.page.update()

    def abrir_modal_nuevo(self, e):
        self.id_actual = None
        self.in_nombre.value = ""
        indice = self.tabs.selected_index
        self.in_categoria.value = "Persiana" if indice == 0 else "Toldo"
        self.in_precio.value = ""
        self.in_precio_fabrica.value = ""
        self.in_costo_instalacion.value = "0"
        self.in_limite_ancho.value = "0"
        self.in_precio_2.value = "0"
        self.in_limite_precio_2.value = "0"
        
        self.page.dialog = self.modal
        self.modal.open = True
        self.page.update()

    def abrir_modal_editar(self, prod):
        self.id_actual = prod.get('id')
        self.in_nombre.value = prod.get('nombre', '')
        self.in_categoria.value = prod.get('tipo', 'Persiana')
        self.in_precio.value = str(prod.get('precio_base') or "0")
        self.in_precio_fabrica.value = str(prod.get('precio_fabrica') or "0")
        self.in_costo_instalacion.value = str(prod.get('costo_instalacion') or "0")
        self.in_limite_ancho.value = str(prod.get('limite_ancho') or "0")
        self.in_precio_2.value = str(prod.get('precio_2') or "0")
        self.in_limite_precio_2.value = str(prod.get('limite_precio_2') or "0")
        
        self.page.dialog = self.modal
        self.modal.open = True
        self.page.update()

    def cerrar_modal(self, e):
        self.modal.open = False
        self.page.update()

    def guardar_producto(self, e):
        try:
            def seguro_float(valor):
                try: return float(valor) if valor else 0.0
                except: return 0.0

            datos = {
                "nombre": self.in_nombre.value,
                "tipo": self.in_categoria.value, 
                "precio_base": seguro_float(self.in_precio.value),
                "precio_fabrica": seguro_float(self.in_precio_fabrica.value),
                "costo_instalacion": seguro_float(self.in_costo_instalacion.value),
                "limite_ancho": seguro_float(self.in_limite_ancho.value),
                "precio_2": seguro_float(self.in_precio_2.value),
                "limite_precio_2": seguro_float(self.in_limite_precio_2.value)
            }

            if self.id_actual:
                self.nube.supabase.table("productos").update(datos).eq("id", self.id_actual).execute()
            else:
                self.nube.supabase.table("productos").insert(datos).execute()
            
            self.cerrar_modal(None)
            self.cargar_datos()
            
            self.page.snack_bar = ft.SnackBar(ft.Text("✅ Producto guardado con éxito"), bgcolor="green")
            self.page.snack_bar.open = True
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"❌ Error al guardar: {ex}"), bgcolor="red")
            self.page.snack_bar.open = True
        self.page.update()

    def eliminar_desde_modal(self, e):
        if self.id_actual:
            try:
                self.nube.supabase.table("productos").delete().eq("id", self.id_actual).execute()
                self.cerrar_modal(None)
                self.cargar_datos()
                self.page.snack_bar = ft.SnackBar(ft.Text("🗑️ Producto eliminado"), bgcolor="red")
                self.page.snack_bar.open = True
            except Exception as ex:
                pass
        self.page.update()
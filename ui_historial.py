import flet as ft
from base_datos import GestorNube
from reporte import generar_pdf
import os
import urllib.parse
import base64 

class HistorialVentas(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.nube = GestorNube()
        self.expand = True
        self.padding = 10
        
        self.usuario_actual = self.page.session.get("usuario_actual") or "Desconocido"
        self.rol_actual = self.page.session.get("rol_actual") or "vendedor"

        self.lista_clientes = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

        self.filtro = ft.SegmentedButton(
            selected={"TODOS"},
            on_change=self.cambiar_filtro,
            segments=[
                ft.Segment(value="TODOS", label=ft.Text("Todos", size=12), icon=ft.Icon(ft.icons.LIST)),
                ft.Segment(value="VENTA", label=ft.Text("Ventas", size=12), icon=ft.Icon(ft.icons.CHECK_CIRCLE, color="green")),
                ft.Segment(value="PENDIENTES", label=ft.Text("Pendientes", size=12), icon=ft.Icon(ft.icons.PAUSE_CIRCLE, color="orange")),
            ],
        )

        self.content = ft.Column([
            ft.Row([
                ft.Icon(ft.icons.PEOPLE_ALT, size=30, color="#212F3D"),
                ft.Text("CARTERA DE CLIENTES", size=22, weight="bold")
            ]),
            self.filtro,
            ft.Text("Toca un cliente para ver su historial, o el lápiz para editar.", color="grey", size=12),
            ft.Divider(height=10, color="transparent"),
            self.lista_clientes
        ], expand=True)
        
        self.cargar_datos()

    def cambiar_filtro(self, e):
        self.cargar_datos()

    def cargar_datos(self):
        self.lista_clientes.controls.clear()
        datos_completos = self.nube.obtener_historial_ventas()
        filtro_actual = list(self.filtro.selected)[0]

        if self.rol_actual != "admin":
            datos = [nota for nota in datos_completos if nota.get('vendedor') == self.usuario_actual]
        else:
            datos = datos_completos

        if filtro_actual != "TODOS":
            datos = [nota for nota in datos if nota.get('estado') == filtro_actual]

        vendedores_agrupados = {}
        for nota in datos:
            vendedor = nota.get('vendedor', 'Sin Vendedor')
            cliente = nota.get('cliente', 'Sin Nombre')
            
            if vendedor not in vendedores_agrupados:
                vendedores_agrupados[vendedor] = {}
                
            if cliente not in vendedores_agrupados[vendedor]:
                vendedores_agrupados[vendedor][cliente] = []
                
            vendedores_agrupados[vendedor][cliente].append(nota)

        for vendedor, clientes in vendedores_agrupados.items():
            
            if self.rol_actual == "admin":
                self.lista_clientes.controls.append(
                    ft.Container(
                        bgcolor="#212F3D", padding=10, border_radius=8, margin=ft.margin.only(top=10, bottom=5),
                        content=ft.Row([
                            ft.Icon(ft.icons.BADGE, color="white", size=20),
                            ft.Text(f"Vendedor: {vendedor}", weight="bold", color="white", size=14)
                        ])
                    )
                )

            for cliente, notas in clientes.items():
                total_gastado = sum(n.get('total', 0) for n in notas)
                cantidad_notas = len(notas)
                
                color_monto = "orange" if filtro_actual == "PENDIENTES" else "#28B463"
                
                # Extraemos los datos actuales para poder editarlos
                tel_actual = notas[0].get('telefono', '')
                dom_actual = notas[0].get('domicilio', '')
                
                tarjeta = ft.Container(
                    padding=15, bgcolor="white", border_radius=10,
                    border=ft.border.all(1, "#E5E7E9"),
                    shadow=ft.BoxShadow(blur_radius=4, color=ft.colors.with_opacity(0.1, "black")),
                    on_click=lambda _, c=cliente, n=notas: self.abrir_historial_personal(c, n), 
                    content=ft.Row([
                        ft.Container(
                            width=50, height=50, bgcolor="#EAF2F8", border_radius=25,
                            alignment=ft.alignment.center,
                            content=ft.Text(cliente[:2].upper(), size=18, weight="bold", color="#2E86C1")
                        ),
                        ft.Column([
                            ft.Text(cliente, weight="bold", size=16),
                            ft.Text(f"{cantidad_notas} notas mostradas", size=12, color="grey"),
                        ], expand=True, spacing=2),
                        
                        # 🔥 AQUÍ ESTÁ EL NUEVO BOTÓN DE EDITAR
                        ft.IconButton(icon=ft.icons.EDIT, icon_color="#3498DB", tooltip="Editar Datos", 
                                      on_click=lambda e, c=cliente, t=tel_actual, d=dom_actual: self.abrir_edicion_cliente(e, c, t, d)),
                        
                        ft.Column([
                            ft.Text("Total en Lista", size=10, color="grey"),
                            ft.Text(f"${total_gastado:,.2f}", weight="bold", color=color_monto),
                        ], horizontal_alignment=ft.CrossAxisAlignment.END)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                )
                self.lista_clientes.controls.append(tarjeta)
        
        if not self.lista_clientes.controls:
            self.lista_clientes.controls.append(ft.Text(f"No hay registros en la categoría: {filtro_actual}.", color="grey", italic=True))
        
        self.page.update()

    # 🔥 NUEVA FUNCIÓN PARA EDITAR CLIENTE (CRUD)
    def abrir_edicion_cliente(self, e, cliente, tel_actual, dom_actual):
        # Evitamos que el toque se pase a la tarjeta y abra el historial por error
        e.control.page = self.page 
        
        in_tel = ft.TextField(label="Teléfono", value=tel_actual, prefix_icon="phone")
        in_dom = ft.TextField(label="Domicilio", value=dom_actual, prefix_icon="home", multiline=True)

        def guardar_cambios(e_btn):
            exito = self.nube.actualizar_datos_cliente(cliente, in_tel.value, in_dom.value)
            if exito:
                self.page.snack_bar = ft.SnackBar(ft.Text("✅ Datos actualizados con éxito"), bgcolor="green")
            else:
                self.page.snack_bar = ft.SnackBar(ft.Text("❌ Error al actualizar en la nube"), bgcolor="red")
            
            self.page.snack_bar.open = True
            self.cerrar_dialogo(dialogo)
            self.cargar_datos() # Recarga la lista para asegurar que todo está al día

        dialogo = ft.AlertDialog(
            title=ft.Text(f"Editar Datos: {cliente}", size=18, weight="bold"),
            content=ft.Column([in_tel, in_dom], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self.cerrar_dialogo(dialogo)),
                ft.ElevatedButton("Guardar", bgcolor="#2E86C1", color="white", on_click=guardar_cambios)
            ]
        )
        self.page.dialog = dialogo
        dialogo.open = True
        self.page.update()

    # --- RESTO DE TUS FUNCIONES EXACTAMENTE IGUALES ---

    def enviar_whatsapp(self, e, nota):
        telefono = nota.get('telefono', '').strip()
        cliente = nota.get('cliente', 'Cliente').strip()
        
        telefono_limpio = ''.join(c for c in telefono if c.isdigit())
        
        if not telefono_limpio:
            self.page.snack_bar = ft.SnackBar(ft.Text("❌ El cliente no tiene un teléfono válido registrado."), bgcolor="red")
            self.page.snack_bar.open = True
            self.page.update()
            return
            
        if len(telefono_limpio) == 10: 
            telefono_limpio = "52" + telefono_limpio
            
        mensaje = f"Hola {cliente}, le comparto los detalles de su nota de Moda Spacio."
        mensaje_codificado = urllib.parse.quote_plus(mensaje)
        
        url_whatsapp = f"https://wa.me/{telefono_limpio}?text={mensaje_codificado}"
        self.page.launch_url(url_whatsapp)
        
        self.page.snack_bar = ft.SnackBar(ft.Text("✅ WhatsApp abierto. Recuerda arrastrar el PDF al chat."), bgcolor="green")
        self.page.snack_bar.open = True
        self.page.update()

    def abrir_historial_personal(self, nombre_cliente, notas):
        lista_notas_ui = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=10)
        
        for i, nota in enumerate(notas):
            color_estado = "green" if nota.get('estado') == "VENTA" else "orange"
            
            costo_fab = float(nota.get('costo_fabrica') or 0.0)
            total_nota = float(nota.get('total') or 0.0)
            ganancia = total_nota - costo_fab
            
            contenido_tarjeta = [
                ft.Row([
                    ft.Text(f"Nota #{i+1}", weight="bold", size=14),
                    ft.Container(content=ft.Text(nota.get('estado', 'PEND.'), size=10, color="white", weight="bold"), bgcolor=color_estado, padding=5, border_radius=5)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=5),
                ft.Row([
                    ft.Text(f"Total: ${total_nota:,.2f}", weight="bold", size=12),
                    ft.Text(f"Saldo: ${float(nota.get('saldo') or 0.0):,.2f}", color="red", size=12),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ]
            
            if self.rol_actual.lower() == "admin":
                contenido_tarjeta.append(
                    ft.Container(
                        bgcolor="#FDEDEC", padding=8, border_radius=5, margin=ft.margin.only(top=5, bottom=5),
                        content=ft.Column([
                            ft.Text(f"🏭 Costo Fábrica: ${costo_fab:,.2f}", size=12, color="#D35400", weight="bold"),
                            ft.Text(f"📈 Ganancia Neta: ${ganancia:,.2f}", size=12, color="blue", weight="bold"),
                        ], spacing=2)
                    )
                )
            
            contenido_tarjeta.append(
                ft.Row([
                    ft.ElevatedButton("Ver PDF", icon=ft.icons.PICTURE_AS_PDF, height=35, expand=True, on_click=lambda _, n=nota: self.reimprimir_pdf(n)),
                    ft.IconButton(
                        icon=ft.icons.MESSAGE, 
                        icon_color="white", 
                        bgcolor="#25D366",
                        tooltip="Enviar por WhatsApp",
                        on_click=lambda e, n=nota: self.enviar_whatsapp(e, n)
                    )
                ], spacing=10)
            )

            tarjeta_nota = ft.Container(
                padding=10, bgcolor="#F8F9F9", border_radius=8,
                border=ft.border.all(1, "#D5D8DC"),
                content=ft.Column(contenido_tarjeta)
            )
            lista_notas_ui.controls.append(tarjeta_nota)

        dialogo = ft.AlertDialog(
            title=ft.Text(f"Historial: {nombre_cliente}", weight="bold"),
            content=ft.Container(width=300, height=400, content=lista_notas_ui),
            actions=[ft.TextButton("Cerrar", on_click=lambda _: self.cerrar_dialogo(dialogo))]
        )
        
        self.page.dialog = dialogo
        dialogo.open = True
        self.page.update()

    def cerrar_dialogo(self, dialogo):
        dialogo.open = False
        self.page.update()

    def reimprimir_pdf(self, nota):
        datos_pdf = {"cliente": nota.get('cliente',''), "telefono": nota.get('telefono',''), "domicilio": nota.get('domicilio',''), "notas": nota.get('notas',''), "vendedor": nota.get('vendedor','')}
        totales = {"total": nota.get('total',0), "anticipo": nota.get('anticipo',0), "saldo": nota.get('saldo',0)}
        carrito = nota.get('productos', [])
        nombre_archivo = f"Reimpresion_{datos_pdf['cliente'].replace(' ', '_')}.pdf"
        
        try:
            generar_pdf(datos_pdf, carrito, totales, nombre_archivo)
            with open(nombre_archivo, "rb") as archivo_pdf:
                pdf_base64 = base64.b64encode(archivo_pdf.read()).decode('utf-8')
            
            self.page.launch_url(f"data:application/pdf;base64,{pdf_base64}", web_window_name="_blank")
            
        except Exception as e:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"❌ Error al abrir PDF: {e}"), bgcolor="red")
            self.page.snack_bar.open = True
            self.page.update()
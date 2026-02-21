import flet as ft
from base_datos import GestorNube
from datetime import datetime, timedelta
import os
from reporte import generar_pdf

# 📅 Diccionarios para fechas en español
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

class ReporteFabrica(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.nube = GestorNube()
        self.expand = True
        self.padding = 20

        self.lista_reportes = ft.Column(spacing=20, scroll=ft.ScrollMode.AUTO, expand=True)
        self.lbl_total_general = ft.Text("$0.00", size=28, weight="bold", color="#D35400")

        # 🎛️ NUEVO: Dropdown para filtrar el tiempo
        self.filtro_tiempo = ft.Dropdown(
            options=[
                ft.dropdown.Option("Esta Semana"),
                ft.dropdown.Option("Semana Pasada"),
                ft.dropdown.Option("Últimos 15 Días"),
                ft.dropdown.Option("Historial Completo")
            ],
            value="Esta Semana",
            on_change=lambda e: self.cargar_datos(),
            height=45, text_size=13, expand=True,
            border_radius=10, filled=True, bgcolor="#FDFEFE"
        )

        self.content = ft.Column([
            ft.Row([ft.Icon(ft.icons.FACTORY, size=30, color="#212F3D"), ft.Text("CORTES DE FÁBRICA", size=22, weight="bold", color="#212F3D")]),
            
            ft.Row([ft.Text("📅 Ver:", weight="bold", color="grey"), self.filtro_tiempo], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            ft.Container(
                bgcolor="#FDEDEC", padding=20, border_radius=10,
                content=ft.Column([
                    ft.Text("💰 TOTAL DEL PERIODO:", weight="bold", color="#C0392B"),
                    self.lbl_total_general
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            ),
            ft.Divider(),
            self.lista_reportes
        ], expand=True)

        self.cargar_datos()

    def cargar_datos(self):
        self.lista_reportes.controls.clear()
        datos = self.nube.obtener_historial_ventas()
        
        ventas_por_dia = {}
        total_global = 0.0
        
        hoy = datetime.now()
        filtro = self.filtro_tiempo.value

        # 🕒 MATEMÁTICA DE FECHAS (Calculando el Lunes actual y pasado)
        lunes_esta_semana = hoy - timedelta(days=hoy.weekday())
        lunes_esta_semana = lunes_esta_semana.replace(hour=0, minute=0, second=0, microsecond=0)
        
        lunes_semana_pasada = lunes_esta_semana - timedelta(days=7)
        domingo_semana_pasada = lunes_esta_semana - timedelta(seconds=1)
        
        limite_15_dias = hoy - timedelta(days=15)

        def seguro_float(valor):
            try: return float(valor) if valor is not None else 0.0
            except: return 0.0

        for nota in datos:
            costo_fab = seguro_float(nota.get('costo_fabrica'))
            if costo_fab <= 0: continue 
            
            fecha_cruda = nota.get('created_at') or nota.get('fecha') or ''
            fecha_obj = None
            
            if fecha_cruda:
                try:
                    fecha_str = str(fecha_cruda).strip()[:10]
                    fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d")
                    
                    nombre_dia = DIAS[fecha_obj.weekday()]
                    nombre_mes = MESES[fecha_obj.month - 1]
                    fecha_bonita = f"{nombre_dia} {fecha_obj.day} de {nombre_mes}"
                except Exception as e:
                    fecha_bonita = "Fecha Desconocida"
                    fecha_str = "0000-00-00"
            else:
                fecha_bonita = "Fecha Desconocida"
                fecha_str = "0000-00-00"

            # 🛑 EL GRAN FILTRO (Decide qué notas entran a la suma global)
            if fecha_obj:
                if filtro == "Esta Semana":
                    if fecha_obj < lunes_esta_semana: continue
                elif filtro == "Semana Pasada":
                    if not (lunes_semana_pasada <= fecha_obj <= domingo_semana_pasada): continue
                elif filtro == "Últimos 15 Días":
                    if fecha_obj < limite_15_dias: continue
            else:
                # Si no tiene fecha, solo la mostramos en "Historial Completo"
                if filtro != "Historial Completo": continue

            if fecha_str not in ventas_por_dia:
                ventas_por_dia[fecha_str] = {"etiqueta": fecha_bonita, "notas": []}
            
            ventas_por_dia[fecha_str]["notas"].append(nota)
            total_global += costo_fab

        self.lbl_total_general.value = f"${total_global:,.2f}"

        for clave_fecha in sorted(ventas_por_dia.keys(), reverse=True):
            datos_dia = ventas_por_dia[clave_fecha]
            etiqueta = datos_dia["etiqueta"]
            notas_dia = datos_dia["notas"]
            
            total_dia = sum(seguro_float(n.get('costo_fabrica')) for n in notas_dia)

            filas_ui = []
            for n in notas_dia:
                vendedor = n.get('vendedor', 'S/N')
                cliente = n.get('cliente', 'S/N')
                costo = seguro_float(n.get('costo_fabrica'))
                
                fila_clickeable = ft.Container(
                    content=ft.Row([
                        ft.Text(f"👤 {vendedor[:4]}. (Cl: {cliente})", size=13, expand=True),
                        ft.Text(f"${costo:,.2f}", size=13, color="#D35400", weight="bold")
                    ]),
                    padding=5, border_radius=5, ink=True, 
                    on_click=lambda _, nota_seleccionada=n, f=etiqueta: self.abrir_detalles(nota_seleccionada, f)
                )
                filas_ui.append(fila_clickeable)

            tarjeta_dia = ft.Container(
                bgcolor="white", padding=15, border_radius=10,
                border=ft.border.all(1, "#E5E7E9"),
                shadow=ft.BoxShadow(blur_radius=4, color=ft.colors.with_opacity(0.1, "black")),
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.icons.CALENDAR_TODAY, size=16, color="#2E86C1"),
                        ft.Text(f"{etiqueta}", weight="bold", size=16, color="#2E86C1")
                    ]),
                    ft.Divider(height=10),
                    ft.Column(filas_ui, spacing=0),
                    ft.Divider(height=10),
                    ft.Row([
                        ft.Text("Total del Día:", weight="bold"),
                        ft.Text(f"${total_dia:,.2f}", weight="bold", color="red", size=16)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ])
            )
            self.lista_reportes.controls.append(tarjeta_dia)

        if not self.lista_reportes.controls:
            self.lista_reportes.controls.append(ft.Text(f"No hay ventas registradas en: {filtro}.", color="grey", italic=True))

        self.page.update()

    # 🔥 VISOR DE DETALLES
    def abrir_detalles(self, nota, fecha):
        cliente = nota.get('cliente', 'Sin Nombre')
        total = float(nota.get('total', 0))
        anticipo = float(nota.get('anticipo', 0))
        productos = nota.get('productos', [])
        
        lista_prod_ui = ft.Column(spacing=5, scroll=ft.ScrollMode.AUTO, height=120)
        for p in productos:
            desc = p.get('desc', 'Producto')
            subt = p.get('subtotal', 0)
            lista_prod_ui.controls.append(
                ft.Text(f"• {desc} - ${subt:,.2f}", size=11)
            )
        
        if not lista_prod_ui.controls:
            lista_prod_ui.controls.append(ft.Text("Sin detalles de productos.", size=11, color="grey"))

        contenido = ft.Column([
            ft.Text(f"📅 Fecha: {fecha}", size=12, color="grey"),
            ft.Divider(height=5),
            ft.Text("🛍️ Productos de la Nota:", weight="bold", size=12),
            ft.Container(content=lista_prod_ui, bgcolor="#F8F9F9", padding=5, border_radius=5, border=ft.border.all(1, "#E5E7E9")),
            ft.Divider(height=5),
            ft.Row([ft.Text("Anticipo del Cliente:", size=12), ft.Text(f"${anticipo:,.2f}", size=12, weight="bold", color="green")], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([ft.Text("Total Venta:", size=12), ft.Text(f"${total:,.2f}", size=12, weight="bold", color="#2E86C1")], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ], tight=True)

        dialogo = ft.AlertDialog(
            title=ft.Text(f"Venta: {cliente}", weight="bold", size=16),
            content=ft.Container(width=300, content=contenido),
            actions=[
                ft.ElevatedButton("Ver PDF", icon="picture_as_pdf", bgcolor="#212F3D", color="white", on_click=lambda _: self.reimprimir_pdf(nota, dialogo)),
                ft.TextButton("Cerrar", on_click=lambda _: self.cerrar_dialogo(dialogo))
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
        
        self.page.dialog = dialogo
        dialogo.open = True
        self.page.update()

    def cerrar_dialogo(self, dialogo):
        dialogo.open = False
        self.page.update()

    def reimprimir_pdf(self, nota, dialogo):
        self.cerrar_dialogo(dialogo)
        datos_pdf = {
            "cliente": nota.get('cliente',''), "telefono": nota.get('telefono',''), "domicilio": nota.get('domicilio',''), 
            "notas": nota.get('notas',''), "vendedor": nota.get('vendedor','')
        }
        totales = {"total": nota.get('total',0), "anticipo": nota.get('anticipo',0), "saldo": nota.get('saldo',0)}
        carrito = nota.get('productos', [])
        nombre_archivo = f"Reimpresion_{datos_pdf['cliente'].replace(' ', '_')}.pdf"
        
        try:
            generar_pdf(datos_pdf, carrito, totales, nombre_archivo)
            if os.name == 'nt': os.startfile(nombre_archivo)
        except Exception as e:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error: {e}"), bgcolor="red")
            self.page.snack_bar.open = True
            self.page.update()
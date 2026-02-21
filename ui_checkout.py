import flet as ft
from base_datos import GestorNube
from reporte import generar_pdf
import os
import base64 # 📦 IMPORTANTE: La nueva herramienta para enviar archivos web
from datetime import datetime, timedelta 

class Checkout(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.padding = 20
        self.nube = GestorNube() 

        # --- RECUPERAR DATOS ---
        self.total_venta = self.page.session.get("total_venta") or 0.0
        self.carrito = self.page.session.get("carrito") or []
        self.vendedor_actual = self.page.session.get("usuario_actual") or "Vendedor"
        self.agenda_clientes = self.nube.obtener_clientes_unicos()

        # 🚀 LA MAGIA INTERACTIVA: Agregamos los selectores al sistema con LÍMITES
        hoy = datetime.now()
        limite_futuro = hoy + timedelta(days=365) # Límite de 1 año

        self.date_picker = ft.DatePicker(
            value=hoy,
            current_date=hoy,          
            first_date=hoy,            
            last_date=limite_futuro,   
            on_change=self.seleccionar_fecha
        )
        self.time_picker = ft.TimePicker(
            value=hoy.time(),          
            on_change=self.seleccionar_hora
        )
        self.page.overlay.extend([self.date_picker, self.time_picker])

        # 🔔 DIÁLOGO DEL PERRO GUARDIÁN (Recordatorios)
        self.dialogo_recordatorio = ft.AlertDialog(
            title=ft.Row([ft.Icon(ft.icons.NOTIFICATIONS_ACTIVE, color="#F39C12"), ft.Text("Falta Fecha", weight="bold")]),
            content=ft.Text("No agendaste fecha de instalación.\n¿Qué deseas hacer?"),
            actions=[
                ft.TextButton("Agendar Ahora", on_click=self.cerrar_dialogo),
                ft.ElevatedButton("Recordar Luego", bgcolor="#F39C12", color="white", on_click=self.guardar_con_recordatorio),
                ft.TextButton("No Recordar", on_click=self.guardar_sin_fecha)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        self.page.overlay.append(self.dialogo_recordatorio)

        # --- CAMPOS CLIENTE ---
        self.in_cliente = ft.TextField(label="Nombre del Cliente", prefix_icon="person", border_radius=10, on_change=self.filtrar_clientes)
        self.caja_sugerencias = ft.Column(visible=False, spacing=2)
        self.in_telefono = ft.TextField(label="Teléfono", prefix_icon="phone", border_radius=10, keyboard_type="phone")
        self.in_domicilio = ft.TextField(label="Domicilio / Dirección", prefix_icon="home", border_radius=10, multiline=True)
        self.in_notas = ft.TextField(label="Notas de Venta", prefix_icon="note", border_radius=10, multiline=True)
        self.in_vendedor = ft.TextField(value=self.vendedor_actual, border_radius=10, read_only=True)
        
        # 📅 CAMPOS LOGÍSTICOS 
        self.in_fecha_inst = ft.TextField(label="Fecha", border_radius=10, expand=True, read_only=True)
        self.btn_fecha = ft.IconButton(icon=ft.icons.CALENDAR_MONTH, icon_color="#E67E22", icon_size=30, on_click=lambda _: self.date_picker.pick_date())
        
        self.in_hora_inst = ft.TextField(label="Hora", border_radius=10, expand=True, read_only=True)
        self.btn_hora = ft.IconButton(icon=ft.icons.ACCESS_TIME, icon_color="#E67E22", icon_size=30, on_click=lambda _: self.time_picker.pick_time())

        self.in_notas_inst = ft.TextField(label="Detalles", prefix_icon="build", border_radius=10, multiline=True)

        self.sw_factura = ft.Switch(label="¿Requiere Factura? (+16%)", value=False, active_color="#28B463", on_change=self.calcular_saldo)
        
        self.lbl_total_real = ft.Text(f"Total de la Nota: ${self.total_venta:,.2f}", color="#2E86C1", weight="bold", size=16)
        self.lbl_resta = ft.Text("Saldo Pendiente: $0.00", color="#E74C3C", weight="bold")
        self.in_anticipo = ft.TextField(label="Anticipo dejado ($)", value="0", keyboard_type="number", prefix_icon="attach_money", on_change=self.calcular_saldo)

        # 🔥 BOTÓN DE GUARDAR AHORA DISPARA LA VALIDACIÓN DEL RADAR
        self.btn_guardar = ft.ElevatedButton(
            content=ft.Row([ft.Icon("picture_as_pdf"), ft.Text("GENERAR NOTA Y GUARDAR", weight="bold")], alignment=ft.MainAxisAlignment.CENTER),
            bgcolor="#212F3D", color="white", height=55, on_click=self.validar_antes_de_procesar
        )

        self.content = ft.Column([
            ft.Text("DATOS DE CIERRE", size=22, weight="bold", color="#212F3D"),
            ft.Text("Completa la información para generar la nota.", color="grey", size=12),
            ft.Divider(height=10, color="transparent"),
            
            self.in_cliente, self.caja_sugerencias, self.in_telefono, self.in_domicilio, self.in_notas, self.in_vendedor, 
            
            ft.Divider(height=10),
            ft.Text("🚚 Logística de Instalación", size=16, weight="bold", color="#D35400"),
            ft.Row([self.in_fecha_inst, self.btn_fecha, self.in_hora_inst, self.btn_hora]),
            self.in_notas_inst,
            ft.Divider(height=10),

            self.sw_factura,
            ft.Container(
                bgcolor="#EAEDED", padding=15, border_radius=10, margin=ft.margin.only(top=10, bottom=20),
                content=ft.Column([ft.Text("Resumen Financiero", weight="bold"), self.lbl_total_real, self.in_anticipo, self.lbl_resta])
            ),
            self.btn_guardar
        ], scroll=ft.ScrollMode.AUTO)
        self.calcular_saldo(None)

    # ⏱️ FUNCIONES DE LOS CALENDARIOS
    def seleccionar_fecha(self, e):
        if self.date_picker.value: self.in_fecha_inst.value = self.date_picker.value.strftime("%d/%m/%Y"); self.page.update()

    def seleccionar_hora(self, e):
        if self.time_picker.value: self.in_hora_inst.value = self.time_picker.value.strftime("%H:%M"); self.page.update()

    def cerrar_dialogo(self, e):
        self.dialogo_recordatorio.open = False
        self.page.update()

    # 🧠 LÓGICA DE VALIDACIÓN Y ALERTAS
    def validar_antes_de_procesar(self, e):
        fecha = self.in_fecha_inst.value
        hora = self.in_hora_inst.value
        if not fecha or not hora or fecha == "Por Asignar" or hora == "Por Asignar":
            # Si no hay fecha, soltamos al perro guardián
            self.dialogo_recordatorio.open = True
            self.page.update()
        else:
            # Si hay fecha, procesamos directo y el radar revisará los choques
            self.ejecutar_procesar_venta(con_fecha=True)

    def guardar_con_recordatorio(self, e):
        self.cerrar_dialogo(None)
        cliente = self.in_cliente.value or "Sin Nombre"
        # Se envía una alerta a SÍ MISMO para recordar agendar
        self.nube.crear_notificacion(self.vendedor_actual, f"🔔 Recordatorio: Pendiente agendar a {cliente}.", "recordatorio")
        self.ejecutar_procesar_venta(con_fecha=False)

    def guardar_sin_fecha(self, e):
        self.cerrar_dialogo(None)
        self.ejecutar_procesar_venta(con_fecha=False)

    def filtrar_clientes(self, e):
        texto = self.in_cliente.value.lower().strip()
        self.caja_sugerencias.controls.clear()
        if len(texto) >= 2:
            coincidencias = 0
            for nombre, datos in self.agenda_clientes.items():
                if texto in nombre.lower():
                    self.caja_sugerencias.controls.append(
                        ft.Container(
                            content=ft.Row([ft.Icon("history", size=16, color="grey"), ft.Text(nombre, weight="bold", color="#2E86C1")]),
                            bgcolor="#EAF2F8", padding=10, border_radius=5, on_click=lambda _, n=nombre, d=datos: self.autocompletar(n, d)
                        )
                    )
                    coincidencias += 1
                    if coincidencias >= 3: break 
            self.caja_sugerencias.visible = coincidencias > 0
        else:
            self.caja_sugerencias.visible = False
        self.page.update()

    def autocompletar(self, nombre, datos):
        self.in_cliente.value = nombre
        self.in_telefono.value = datos['telefono']
        self.in_domicilio.value = datos['domicilio']
        self.caja_sugerencias.visible = False 
        self.page.update()

    def calcular_saldo(self, e):
        total_con_impuestos = self.total_venta * 1.16 if self.sw_factura.value else self.total_venta
        self.lbl_total_real.value = f"Total de la Nota: ${total_con_impuestos:,.2f}"
        try: anticipo = float(self.in_anticipo.value) if self.in_anticipo.value else 0.0
        except: anticipo = 0.0 
        saldo = total_con_impuestos - anticipo
        self.lbl_resta.value = f"Saldo Pendiente: ${saldo:,.2f}"
        if saldo <= 0: self.lbl_resta.color = "#28B463"
        else: self.lbl_resta.color = "#E74C3C"
        self.page.update()

    # 🚀 LA FUNCIÓN MAESTRA: PROCESAR + RADAR DE CHOQUES
    def ejecutar_procesar_venta(self, con_fecha):
        anticipo = float(self.in_anticipo.value) if self.in_anticipo.value else 0.0
        total_final = self.total_venta * 1.16 if self.sw_factura.value else self.total_venta
        saldo = total_final - anticipo
        costo_fabrica_oculto = self.page.session.get("costo_fabrica_total") or 0.0
        cliente = self.in_cliente.value or "Sin Nombre"

        # 💥 RADAR SILENCIOSO DE CHOQUES
        if con_fecha:
            fecha_nueva = self.in_fecha_inst.value
            hora_nueva = self.in_hora_inst.value
            try:
                t_nueva = datetime.strptime(hora_nueva, "%H:%M")
                todas_las_inst = self.nube.obtener_instalaciones()
                choque = False
                for otra in todas_las_inst:
                    if otra.get('fecha_instalacion') == fecha_nueva and otra.get('hora_instalacion') not in ["Por Asignar", ""]:
                        try:
                            t_otra = datetime.strptime(otra.get('hora_instalacion'), "%H:%M")
                            if abs((t_nueva - t_otra).total_seconds()) / 60 < 60: # Menos de 1 hora de diferencia
                                choque = True
                                break
                        except: pass
                
                # Despachar notificaciones según el radar
                if choque:
                    self.nube.crear_notificacion("admin", f"🚨 CHOKE LOGÍSTICO: {self.vendedor_actual} agendó a {cliente} el {fecha_nueva} a las {hora_nueva}, pero choca con otra cita.", "choque")
                    self.page.snack_bar = ft.SnackBar(ft.Text("⚠️ Hora de alta demanda. Se notificará al Administrador para confirmación."), bgcolor="orange")
                    self.page.snack_bar.open = True
                else:
                    self.nube.crear_notificacion("admin", f"📅 {self.vendedor_actual} agendó a {cliente} el {fecha_nueva} a las {hora_nueva}.", "nueva_cita")
            except: pass

        datos_nota = {
            "cliente": cliente,
            "telefono": self.in_telefono.value or "",
            "domicilio": self.in_domicilio.value or "",
            "notas": self.in_notas.value or "",
            "vendedor": self.vendedor_actual,
            "total": total_final,
            "anticipo": anticipo,
            "saldo": saldo,
            "costo_fabrica": costo_fabrica_oculto,
            "productos": self.carrito,
            "fecha_instalacion": self.in_fecha_inst.value or "Por Asignar",
            "hora_instalacion": self.in_hora_inst.value or "Por Asignar",
            "notas_instalacion": self.in_notas_inst.value or "Ninguna"
        }

        exito_nube = self.nube.guardar_venta(datos_nota)

        if exito_nube:
            nombre_cliente_limpio = datos_nota["cliente"].replace(" ", "_")
            nombre_pdf = f"Nota_{nombre_cliente_limpio}.pdf"
            try:
                generar_pdf(datos_nota, self.carrito, {"total": total_final, "anticipo": anticipo, "saldo": saldo}, nombre_pdf)
                self.page.session.set("carrito", [])
                self.page.session.set("total_venta", 0.0)
                self.page.session.set("costo_fabrica_total", 0.0)
                
                if not con_fecha:
                    self.page.snack_bar = ft.SnackBar(ft.Text(f"✅ Venta guardada con éxito."), bgcolor="green")
                    self.page.snack_bar.open = True
                    
                # 🔥 LA CURA WEB: Leemos el PDF, lo codificamos a texto y lo forzamos al navegador
                with open(nombre_pdf, "rb") as archivo_pdf:
                    pdf_base64 = base64.b64encode(archivo_pdf.read()).decode('utf-8')
                
                self.page.launch_url(f"data:application/pdf;base64,{pdf_base64}", web_window_name="_blank")
                
                self.page.go('/home')
            except Exception as ex:
                self.page.snack_bar = ft.SnackBar(ft.Text(f"✅ Guardado, pero error en PDF: {ex}"), bgcolor="orange")
                self.page.snack_bar.open = True
                self.page.go('/home')
        else:
            self.page.snack_bar = ft.SnackBar(ft.Text("❌ Error al conectar con la base de datos."), bgcolor="red")
            self.page.snack_bar.open = True
        self.page.update()
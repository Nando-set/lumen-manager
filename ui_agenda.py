import flet as ft
from base_datos import GestorNube
import urllib.parse
from datetime import datetime, timedelta

class AgendaInstalaciones(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.nube = GestorNube()
        self.expand = True
        self.padding = 10
        
        self.usuario_actual = self.page.session.get("usuario_actual") or "Desconocido"
        self.rol_actual = self.page.session.get("rol_actual") or "vendedor"

        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(text="Por Vendedor", icon=ft.icons.PEOPLE),
                ft.Tab(text="Cronograma", icon=ft.icons.VIEW_TIMELINE),
            ],
            on_change=lambda _: self.cargar_datos() 
        )

        self.lista_agenda = ft.Column(spacing=15, scroll=ft.ScrollMode.AUTO, expand=True)

        # --- HERRAMIENTAS DE EDICIÓN Y RADAR ---
        self.inst_id_actual = None 
        
        hoy = datetime.now()
        self.date_picker = ft.DatePicker(current_date=hoy, first_date=hoy, last_date=hoy + timedelta(days=365), on_change=self.set_fecha_edit)
        self.time_picker = ft.TimePicker(value=hoy.time(), on_change=self.set_hora_edit)
        self.page.overlay.extend([self.date_picker, self.time_picker])

        self.edit_fecha = ft.TextField(label="Fecha", read_only=True, expand=True)
        self.edit_hora = ft.TextField(label="Hora", read_only=True, expand=True)
        self.edit_estado = ft.Dropdown(label="Estado", options=[
            ft.dropdown.Option("Por Agendar"), ft.dropdown.Option("En Camino"), ft.dropdown.Option("Instalada")
        ])
        self.edit_notas = ft.TextField(label="Notas Técnicas (Ej: Andamios)", multiline=True)

        self.dialogo_editar = ft.AlertDialog(
            title=ft.Text("Administrar Instalación", weight="bold"),
            content=ft.Column([
                self.edit_estado,
                ft.Row([self.edit_fecha, ft.IconButton(ft.icons.CALENDAR_MONTH, on_click=lambda _: self.date_picker.pick_date())]),
                ft.Row([self.edit_hora, ft.IconButton(ft.icons.ACCESS_TIME, on_click=lambda _: self.time_picker.pick_time())]),
                self.edit_notas
            ], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=self.cerrar_dialogos),
                ft.ElevatedButton("Guardar Cambios", bgcolor="green", color="white", on_click=self.verificar_radar)
            ]
        )

        self.dialogo_choque = ft.AlertDialog(
            title=ft.Row([ft.Icon(ft.icons.WARNING_AMBER, color="red"), ft.Text("¡Alerta de Choque!", color="red", weight="bold")]),
            content=ft.Text(""), 
            actions=[
                ft.TextButton("Cambiar Hora", on_click=lambda _: (setattr(self.dialogo_choque, 'open', False), self.page.update())),
                ft.ElevatedButton("Forzar Agenda", bgcolor="red", color="white", on_click=self.guardar_edicion_final)
            ]
        )

        # 🧾 NUEVO: DIÁLOGO DE DETALLES DE VENTA (SCROLLABLE, COMPLETO Y CON WHATSAPP)
        self.info_productos = ft.Column(spacing=5) # Le quitamos el scroll aquí para dárselo a toda la ventana
        self.info_domicilio = ft.Text(size=14, color="#212F3D")
        self.info_notas = ft.Text(size=13, color="#D35400", italic=True)
        self.btn_maps_detalle = ft.TextButton("Abrir en mapa", icon=ft.icons.LOCATION_ON, icon_color="blue")
        
        self.info_total = ft.Text(weight="bold", size=14, color="#212F3D")
        self.info_anticipo = ft.Text(weight="bold", size=14, color="#28B463")
        self.info_saldo = ft.Text(weight="bold", size=15, color="#C0392B")
        
        self.btn_wa_instalador = ft.ElevatedButton("Compartir con Instalador", icon=ft.icons.SHARE, bgcolor="#25D366", color="white", width=float('inf'))

        self.dialogo_info = ft.AlertDialog(
            title=ft.Row([ft.Icon(ft.icons.RECEIPT_LONG, color="#2980B9"), ft.Text("Detalles de Venta", weight="bold", size=18)]),
            content=ft.Container(
                width=400,
                # 🔥 EL MOTOR DE SCROLL ESTÁ AQUÍ. Si la info crece, todo desliza parejo.
                content=ft.Column([
                    ft.Text("📍 Ubicación Exacta:", weight="bold", color="grey", size=12),
                    ft.Container(
                        padding=10, bgcolor="#FBFCFC", border=ft.border.all(1, "#D5D8DC"), border_radius=8,
                        content=ft.Column([
                            self.info_domicilio,
                            ft.Row([self.btn_maps_detalle], alignment=ft.MainAxisAlignment.END)
                        ], spacing=0)
                    ),
                    ft.Text("📝 Notas Logísticas:", weight="bold", color="grey", size=12),
                    self.info_notas,
                    ft.Divider(),
                    ft.Text("🪟 Productos a instalar:", weight="bold", color="grey", size=12),
                    self.info_productos, 
                    ft.Divider(),
                    ft.Row([ft.Text("Valor Venta:"), self.info_total], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Row([ft.Text("Anticipo dejado:"), self.info_anticipo], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Row([ft.Text("Saldo Pendiente:", weight="bold"), self.info_saldo], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(),
                    self.btn_wa_instalador
                ], scroll=ft.ScrollMode.AUTO, spacing=10)
            ),
            actions=[ft.TextButton("Cerrar", on_click=self.cerrar_dialogos)]
        )

        self.page.overlay.extend([self.dialogo_editar, self.dialogo_choque, self.dialogo_info])

        self.content = ft.Column([
            ft.Row([
                ft.Icon(ft.icons.CALENDAR_MONTH, size=30, color="#E67E22"),
                ft.Text("AGENDA DE INSTALACIONES", size=20, weight="bold")
            ]),
            ft.Text("Organiza las visitas y envía los reportes.", color="grey", size=12),
            self.tabs,
            ft.Divider(height=10, color="transparent"),
            self.lista_agenda
        ], expand=True)
        
        self.cargar_datos()

    def set_fecha_edit(self, e):
        if self.date_picker.value: self.edit_fecha.value = self.date_picker.value.strftime("%d/%m/%Y"); self.page.update()

    def set_hora_edit(self, e):
        if self.time_picker.value: self.edit_hora.value = self.time_picker.value.strftime("%H:%M"); self.page.update()

    def cerrar_dialogos(self, e=None):
        self.dialogo_editar.open = False
        self.dialogo_choque.open = False
        self.dialogo_info.open = False 
        self.page.update()

    def parsear_fecha_hora(self, fecha_str, hora_str):
        try:
            if fecha_str == "Por Asignar" or not fecha_str: return datetime.max
            f_obj = datetime.strptime(fecha_str, "%d/%m/%Y")
            if hora_str == "Por Asignar" or not hora_str:
                h_obj = datetime.min.time()
            else:
                h_obj = datetime.strptime(hora_str, "%H:%M").time()
            return datetime.combine(f_obj, h_obj)
        except: return datetime.max 

    def cargar_datos(self):
        self.lista_agenda.controls.clear()
        datos_completos = self.nube.obtener_instalaciones()
        if self.rol_actual != "admin":
            datos = [inst for inst in datos_completos if inst.get('vendedor') == self.usuario_actual]
        else:
            datos = datos_completos
        indice_pestana = self.tabs.selected_index

        if indice_pestana == 0:
            vendedores_agrupados = {}
            for inst in datos:
                vendedor = inst.get('vendedor', 'Sin Vendedor')
                if vendedor not in vendedores_agrupados: vendedores_agrupados[vendedor] = []
                vendedores_agrupados[vendedor].append(inst)

            for vendedor, instalaciones in vendedores_agrupados.items():
                if self.rol_actual == "admin":
                    self.lista_agenda.controls.append(
                        ft.Container(
                            bgcolor="#212F3D", padding=10, border_radius=8, margin=ft.margin.only(top=10, bottom=5),
                            content=ft.Row([
                                ft.Icon(ft.icons.ENGINEERING, color="white", size=20),
                                ft.Text(f"Instalaciones de: {vendedor}", weight="bold", color="white", size=14)
                            ])
                        )
                    )
                for inst in instalaciones:
                    self.lista_agenda.controls.append(self.crear_tarjeta_instalacion(inst))
        elif indice_pestana == 1:
            datos_ordenados = sorted(datos, key=lambda x: self.parsear_fecha_hora(x.get('fecha_instalacion'), x.get('hora_instalacion')))
            fechas_agrupadas = {}
            for inst in datos_ordenados:
                fecha = inst.get('fecha_instalacion', 'Por Asignar')
                if fecha not in fechas_agrupadas: fechas_agrupadas[fecha] = []
                fechas_agrupadas[fecha].append(inst)
            for fecha, instalaciones in fechas_agrupadas.items():
                color_bg = "#E74C3C" if fecha == "Por Asignar" else "#2E86C1" 
                self.lista_agenda.controls.append(
                    ft.Container(
                        bgcolor=color_bg, padding=10, border_radius=8, margin=ft.margin.only(top=10, bottom=5),
                        content=ft.Row([
                            ft.Icon(ft.icons.EVENT, color="white", size=20),
                            ft.Text(f"📅 {fecha}", weight="bold", color="white", size=14)
                        ])
                    )
                )
                for inst in instalaciones:
                    self.lista_agenda.controls.append(self.crear_tarjeta_instalacion(inst, mostrar_vendedor=True))

        if not self.lista_agenda.controls:
            self.lista_agenda.controls.append(ft.Text("No hay instalaciones pendientes.", color="grey", italic=True))
        self.page.update()

    def crear_tarjeta_instalacion(self, inst, mostrar_vendedor=False):
        cliente = inst.get('cliente', 'Sin Nombre')
        telefono = inst.get('telefono', 'S/N')
        fecha = inst.get('fecha_instalacion', 'Por Asignar')
        hora = inst.get('hora_instalacion', 'Por Asignar')
        estado_bd = inst.get('estado', 'Por Agendar')
        vendedor = inst.get('vendedor', 'Desconocido')
        
        if fecha == "Por Asignar" or hora == "Por Asignar" or not fecha or not hora:
            estado_visual = "Por Agendar"; color_estado = "red"
        else:
            if estado_bd == "Por Agendar":
                estado_visual = "Agendada"; color_estado = "green"
            else:
                estado_visual = estado_bd; color_estado = "orange" if estado_bd == "En Camino" else "green"

        fila_botones = [
            ft.IconButton(
                icon=ft.icons.RECEIPT_LONG, icon_color="#2980B9", bgcolor="#EAF2F8", 
                tooltip="Ver Detalles y Dirección",
                on_click=lambda _, i=inst: self.abrir_detalles(i)
            )
        ]
        
        if self.rol_actual == "admin":
            fila_botones.insert(0, ft.ElevatedButton("Adm.", icon="edit", bgcolor="#8E44AD", color="white", on_click=lambda _, i=inst: self.abrir_editor(i)))

        fila_titulos = [ft.Text(f"{cliente}", weight="bold", size=16, expand=True)]
        if mostrar_vendedor and self.rol_actual == "admin":
            fila_titulos.append(ft.Container(content=ft.Text(f"👤 {vendedor}", size=10, color="white", weight="bold"), bgcolor="grey", padding=5, border_radius=5))
        fila_titulos.append(ft.Container(content=ft.Text(estado_visual, size=10, color="white", weight="bold"), bgcolor=color_estado, padding=5, border_radius=5))

        tarjeta = ft.Container(
            padding=15, bgcolor="white", border_radius=10, border=ft.border.all(1, "#E5E7E9"),
            shadow=ft.BoxShadow(blur_radius=4, color=ft.colors.with_opacity(0.1, "black")),
            content=ft.Column([
                ft.Row(fila_titulos),
                ft.Divider(height=5),
                ft.Row([
                    ft.Column([
                        ft.Row([ft.Icon(ft.icons.CALENDAR_TODAY, size=14, color="grey"), ft.Text(f"{fecha} - {hora}", size=13, weight="bold", color="#2E86C1")]),
                        ft.Row([ft.Icon(ft.icons.PHONE, size=14, color="grey"), ft.Text(telefono, size=13)]),
                    ], expand=True),
                    ft.Row(fila_botones)
                ])
            ], spacing=5)
        )
        return tarjeta

    # 🧾 ABRIR DETALLES DE VENTA (AHORA MUESTRA TODO Y ES SCROLLABLE)
    def abrir_detalles(self, inst):
        self.info_productos.controls.clear()
        
        productos = inst.get('productos') or []
        domicilio = inst.get('domicilio', 'Sin Dirección')
        notas_inst = inst.get('notas_instalacion', 'Ninguna')
        
        # Recuperamos datos financieros
        total = float(inst.get('total') or 0.0)
        anticipo = float(inst.get('anticipo') or 0.0)
        saldo = float(inst.get('saldo') or 0.0)

        # Configurar Dirección y Botón Maps
        self.info_domicilio.value = domicilio
        dir_codificada = urllib.parse.quote_plus(domicilio)
        url_mapas = f"https://www.google.com/maps/search/?api=1&query={dir_codificada}"
        self.btn_maps_detalle.on_click = lambda _: self.page.launch_url(url_mapas)
        
        # Configurar Notas Logísticas
        self.info_notas.value = notas_inst if notas_inst and notas_inst != "Ninguna" else "Sin notas adicionales."

        if not productos:
            self.info_productos.controls.append(ft.Text("No hay detalles de productos.", color="grey", italic=True))
        else:
            for p in productos:
                desc = p.get('desc', 'Producto')
                subt = p.get('subtotal', 0.0)
                self.info_productos.controls.append(
                    ft.Container(
                        bgcolor="#F8F9F9", padding=10, border_radius=8,
                        content=ft.Row([
                            ft.Icon(ft.icons.CHECK_CIRCLE_OUTLINE, size=16, color="#E67E22"),
                            # expand=True permite que textos muy largos pasen a la siguiente línea
                            ft.Text(desc, size=12, expand=True), 
                            ft.Text(f"${subt:,.2f}", weight="bold", size=12)
                        ])
                    )
                )

        self.info_total.value = f"${total:,.2f}"
        self.info_anticipo.value = f"${anticipo:,.2f}"
        self.info_saldo.value = f"${saldo:,.2f}"
        
        # 🔥 Vincular el botón de WhatsApp a nuestra nueva función
        self.btn_wa_instalador.on_click = lambda e: self.enviar_wa_instalador(e, inst, url_mapas)

        self.dialogo_info.open = True
        self.page.update()

    # 🚀 LA MAGIA: GENERAR WHATSAPP UNIVERSAL PARA INSTALADORES
    def enviar_wa_instalador(self, e, inst, url_mapas):
        cliente = inst.get('cliente', 'Cliente')
        telefono = inst.get('telefono', 'S/N')
        fecha = inst.get('fecha_instalacion', 'Por Asignar')
        hora = inst.get('hora_instalacion', 'Por Asignar')
        domicilio = inst.get('domicilio', 'Sin Dirección')
        notas = inst.get('notas_instalacion', 'Ninguna')
        saldo = float(inst.get('saldo') or 0.0)
        
        mensaje = f"📍 *DATOS DE INSTALACIÓN - MODA SPACIO*\n\n"
        mensaje += f"👤 *Cliente:* {cliente}\n"
        mensaje += f"📞 *Teléfono Cliente:* {telefono}\n"
        mensaje += f"📅 *Cita:* {fecha} a las {hora}\n"
        mensaje += f"💰 *Saldo a cobrar:* ${saldo:,.2f}\n\n"
        mensaje += f"🏠 *Dirección:*\n{domicilio}\n\n"
        mensaje += f"🗺️ *Mapa:* {url_mapas}\n\n"
        mensaje += f"📝 *Notas Logísticas:*\n{notas}"
        
        mensaje_codificado = urllib.parse.quote_plus(mensaje)
        
        # 🔥 EL SECRETO: Al no poner un número de teléfono, WhatsApp abre tu lista de contactos para que elijas a quién mandarlo.
        url_wa = f"https://wa.me/?text={mensaje_codificado}"
        
        self.page.launch_url(url_wa)
        self.cerrar_dialogos()

    def abrir_editor(self, inst):
        self.inst_id_actual = inst.get('id')
        self.edit_fecha.value = inst.get('fecha_instalacion', '')
        self.edit_hora.value = inst.get('hora_instalacion', '')
        self.edit_estado.value = inst.get('estado', 'Por Agendar')
        self.edit_notas.value = inst.get('notas_instalacion', '')
        self.dialogo_editar.open = True
        self.page.update()

    def verificar_radar(self, e):
        if self.edit_fecha.value in ["Por Asignar", ""] or self.edit_hora.value in ["Por Asignar", ""]:
            self.guardar_edicion_final(None); return
        fecha_nueva = self.edit_fecha.value
        hora_nueva = self.edit_hora.value
        try: t_nueva = datetime.strptime(hora_nueva, "%H:%M")
        except: self.guardar_edicion_final(None); return

        todas_las_inst = self.nube.obtener_instalaciones()
        choque_detectado = None
        for otra in todas_las_inst:
            if str(otra.get('id')) == str(self.inst_id_actual): continue
            if otra.get('fecha_instalacion') == fecha_nueva and otra.get('hora_instalacion') not in ["Por Asignar", ""]:
                try:
                    t_otra = datetime.strptime(otra.get('hora_instalacion'), "%H:%M")
                    if abs((t_nueva - t_otra).total_seconds()) / 60 < 60: 
                        choque_detectado = otra; break
                except: pass

        if choque_detectado:
            cliente_choque = choque_detectado.get('cliente', 'Otro Cliente')
            hora_choque = choque_detectado.get('hora_instalacion', '')
            self.dialogo_choque.content.value = f"Choque con {cliente_choque} a las {hora_choque}. ¿Forzar?"
            self.dialogo_editar.open = False; self.dialogo_choque.open = True; self.page.update()
        else: self.guardar_edicion_final(None) 

    def guardar_edicion_final(self, e):
        datos_nuevos = {
            "fecha_instalacion": self.edit_fecha.value, "hora_instalacion": self.edit_hora.value,
            "estado": self.edit_estado.value, "notas_instalacion": self.edit_notas.value
        }
        exito = self.nube.actualizar_instalacion(self.inst_id_actual, datos_nuevos)
        self.cerrar_dialogos()
        if exito:
            self.page.snack_bar = ft.SnackBar(ft.Text("✅ Logística actualizada"), bgcolor="green")
            self.cargar_datos() 
        else: self.page.snack_bar = ft.SnackBar(ft.Text("❌ Error al guardar"), bgcolor="red")
        self.page.snack_bar.open = True; self.page.update()
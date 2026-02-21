import flet as ft
from ui_cotizador import Cotizador
from ui_checkout import Checkout 
from ui_inventario import Inventario
from ui_historial import HistorialVentas
from ui_login import LoginScreen
from ui_reporte_fabrica import ReporteFabrica
from ui_agenda import AgendaInstalaciones
from base_datos import GestorNube 

class VistasManager:
    def __init__(self, page: ft.Page):
        self.page = page
        self.nube = GestorNube() 

    def cerrar_sesion(self):
        """Limpia la memoria del celular/PC para salir completamente"""
        self.page.client_storage.remove("sesion_modaspacio")
        self.page.session.clear()
        self.page.go('/login')

    # 🔔 --- FUNCIONES DEL CENTRO DE NOTIFICACIONES ---
    def abrir_centro_notificaciones(self, receptor):
        notificaciones = self.nube.obtener_notificaciones_no_leidas(receptor)

        if not notificaciones:
            contenido = ft.Text("No tienes notificaciones nuevas. ¡Todo al día! 😎", color="grey", text_align=ft.TextAlign.CENTER)
        else:
            lista = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, height=350)
            for notif in notificaciones:
                # Dar estilo dependiendo del tipo de alerta
                es_choque = notif.get("tipo") == "choque"
                icono = ft.icons.WARNING_AMBER if es_choque else ft.icons.NOTIFICATIONS_ACTIVE
                color_bg = "#FADBD8" if es_choque else "#EAF2F8"
                color_texto = "#C0392B" if es_choque else "#2980B9"

                tarjeta = ft.Container(
                    padding=10, bgcolor=color_bg, border_radius=8,
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(icono, color=color_texto), 
                            ft.Text(notif.get("mensaje", ""), size=13, weight="bold", color=color_texto, expand=True)
                        ]),
                        ft.ElevatedButton("Marcar como leída", icon="check", bgcolor="white", color="black", height=30, 
                                          on_click=lambda _, id_n=notif.get("id"): self.marcar_leida(id_n))
                    ])
                )
                lista.controls.append(tarjeta)
            contenido = lista

        self.dialogo_notif = ft.AlertDialog(
            title=ft.Row([ft.Icon(ft.icons.NOTIFICATIONS, color="#F39C12"), ft.Text("Centro de Alertas")]),
            content=contenido,
            actions=[ft.TextButton("Cerrar", on_click=lambda _: self.cerrar_dialogo_notif())]
        )
        self.page.overlay.append(self.dialogo_notif)
        self.dialogo_notif.open = True
        self.page.update()

    def marcar_leida(self, id_notif):
        self.nube.marcar_notificacion_leida(id_notif)
        self.cerrar_dialogo_notif()
        self.router('/home') # 🔥 AHORA FORZAMOS LA RECARGA DE LA PANTALLA INMEDIATAMENTE

    def cerrar_dialogo_notif(self):
        if hasattr(self, 'dialogo_notif'):
            self.dialogo_notif.open = False
            self.page.update()
    # ------------------------------------------------

    def router(self, route):
        self.page.views.clear()
        
        # --- RUTA 1: LOGIN ---
        if self.page.route == '/login':
            if self.page.client_storage.contains_key("sesion_modaspacio"):
                datos_guardados = self.page.client_storage.get("sesion_modaspacio")
                self.page.session.set("usuario_actual", datos_guardados.get('nombre_real', 'Usuario'))
                self.page.session.set("rol_actual", datos_guardados.get('rol', 'vendedor'))
                self.page.go('/home')
                return 

            self.page.views.append(
                ft.View(
                    "/login",
                    controls=[LoginScreen(self.page)],
                    bgcolor="#F4F6F7"
                )
            )

        # --- RUTA 2: DASHBOARD (HOME) ---
        elif self.page.route == '/home':
            nombre_usuario = self.page.session.get("usuario_actual") or "Equipo"
            rol_usuario = self.page.session.get("rol_actual") or "vendedor" 
            
            # 🔥 LECTURA DE NOTIFICACIONES PARA LA CAMPANITA
            receptor_notif = "admin" if rol_usuario == "admin" else nombre_usuario
            alertas = self.nube.obtener_notificaciones_no_leidas(receptor_notif)
            cantidad_alertas = len(alertas)

            # Construcción dinámica del botón campanita
            color_campana = "#F1C40F" if cantidad_alertas > 0 else "white"
            icono_campana = ft.icons.NOTIFICATIONS_ACTIVE if cantidad_alertas > 0 else ft.icons.NOTIFICATIONS

            btn_campanita = ft.Stack([
                ft.IconButton(icon=icono_campana, icon_color=color_campana, on_click=lambda _: self.abrir_centro_notificaciones(receptor_notif))
            ])
            
            # Si hay mensajes, le ponemos el globito rojo
            if cantidad_alertas > 0:
                btn_campanita.controls.append(
                    ft.Container(
                        content=ft.Text(str(cantidad_alertas), size=10, color="white", weight="bold"),
                        bgcolor="red", width=18, height=18, border_radius=9, alignment=ft.alignment.center,
                        top=0, right=0
                    )
                )

            # 1. Botones que TODOS pueden ver
            controles_menu = [
                self._crear_tarjeta_accion("Nueva Cotización", "Crear presupuesto", "add_circle", "#28B463", lambda _: self.page.go('/cotizar')),
                ft.Divider(height=10, color="transparent"),
            ]
            
            # 👑 2. Botones VIP (Solo lo ve el Admin)
            if rol_usuario == "admin":
                controles_menu.append(
                    self._crear_tarjeta_accion("Inventario y Precios", "Actualizar base de datos", "inventory", "#8E44AD", lambda _: self.page.go('/inventario'))
                )
                controles_menu.append(ft.Divider(height=10, color="transparent"))
                
                controles_menu.append(
                    self._crear_tarjeta_accion("Cortes de Fábrica", "Ver reportes y pagos", "factory", "#C0392B", lambda _: self.page.go('/reporte_fabrica'))
                )
                controles_menu.append(ft.Divider(height=10, color="transparent"))
                
            # 3. El resto de los botones para TODOS
            controles_menu.extend([
                self._crear_tarjeta_accion("Mis Ventas", "Ver historial y notas", "list", "#2E86C1", lambda _: self.page.go('/historial')),
                ft.Divider(height=10, color="transparent"),
                
                self._crear_tarjeta_accion("Agenda Instalaciones", "Organizar fechas y rutas", "map", "#E67E22", lambda _: self.page.go('/agenda')),
            ])

            self.page.views.append(
                ft.View(
                    "/home",
                    controls=[
                        ft.AppBar(
                            title=ft.Text(f"Hola, {nombre_usuario} 👋", size=20, weight="bold"),
                            bgcolor="#212F3D", color="white",
                            actions=[btn_campanita, ft.IconButton(icon="logout", icon_color="white", on_click=lambda _: self.cerrar_sesion())]
                        ),
                        ft.Container(
                            padding=20,
                            expand=True, # 🔥 ESTA ES LA PIEZA QUE FALTABA
                            content=ft.Column(controles_menu, scroll=ft.ScrollMode.AUTO) 
                        )
                    ], bgcolor="#F4F6F7"
                )
            )
            
        # --- RUTA 3: COTIZADOR ---
        elif self.page.route == '/cotizar':
            self.page.views.append(
                ft.View(
                    "/cotizar",
                    controls=[
                        ft.AppBar(
                            title=ft.Text("Cotizador"), 
                            bgcolor="#212F3D", color="white",
                            leading=ft.IconButton(icon="arrow_back", icon_color="white", on_click=lambda _: self.page.go('/home'))
                        ),
                        Cotizador(self.page) 
                    ],
                    bgcolor="#F4F6F7"
                )
            )
            
        # --- RUTA 4: CHECKOUT ---
        elif self.page.route == '/checkout':
            self.page.views.append(
                ft.View(
                    "/checkout",
                    controls=[
                        ft.AppBar(
                            title=ft.Text("Cierre de Venta"), 
                            bgcolor="#212F3D", color="white", 
                            leading=ft.IconButton(icon="arrow_back", icon_color="white", on_click=lambda _: self.page.go('/cotizar'))
                        ),
                        Checkout(self.page)
                    ],
                    bgcolor="#F4F6F7"
                )
            )
            
        # --- RUTA 5: INVENTARIO ---
        elif self.page.route == '/inventario':
            self.page.views.append(
                ft.View(
                    "/inventario",
                    controls=[
                        ft.AppBar(
                            title=ft.Text("Panel de Precios"), 
                            bgcolor="#212F3D", color="white", 
                            leading=ft.IconButton(icon="arrow_back", icon_color="white", on_click=lambda _: self.page.go('/home'))
                        ),
                        Inventario(self.page)
                    ],
                    bgcolor="#F4F6F7"
                )
            )

        # --- RUTA 6: HISTORIAL ---
        elif self.page.route == '/historial':
            self.page.views.append(
                ft.View(
                    "/historial",
                    controls=[
                        ft.AppBar(
                            title=ft.Text("Historial de Notas"), 
                            bgcolor="#212F3D", color="white", 
                            leading=ft.IconButton(icon="arrow_back", icon_color="white", on_click=lambda _: self.page.go('/home'))
                        ),
                        HistorialVentas(self.page)
                    ],
                    bgcolor="#F4F6F7"
                )
            )
            
        # --- RUTA 7: REPORTE DE FÁBRICA ---
        elif self.page.route == '/reporte_fabrica':
            self.page.views.append(
                ft.View(
                    "/reporte_fabrica",
                    controls=[
                        ft.AppBar(
                            title=ft.Text("Reporte de Fábrica"), 
                            bgcolor="#212F3D", color="white", 
                            leading=ft.IconButton(icon="arrow_back", icon_color="white", on_click=lambda _: self.page.go('/home'))
                        ),
                        ReporteFabrica(self.page)
                    ],
                    bgcolor="#F4F6F7"
                )
            )

        # --- RUTA 8: AGENDA DE INSTALACIONES ---
        elif self.page.route == '/agenda':
            self.page.views.append(
                ft.View(
                    "/agenda",
                    controls=[
                        ft.AppBar(
                            title=ft.Text("Agenda de Instalaciones"), 
                            bgcolor="#212F3D", color="white", 
                            leading=ft.IconButton(icon="arrow_back", icon_color="white", on_click=lambda _: self.page.go('/home'))
                        ),
                        AgendaInstalaciones(self.page)
                    ],
                    bgcolor="#F4F6F7"
                )
            )
        
        self.page.update()

    def _crear_tarjeta_accion(self, titulo, subtitulo, icono_code, color, funcion):
        return ft.Container(
            height=120, border_radius=15, bgcolor="white",
            shadow=ft.BoxShadow(blur_radius=10, color=ft.colors.with_opacity(0.1, "black")),
            padding=20, on_click=funcion,
            content=ft.Row([
                ft.Container(width=60, height=60, bgcolor=ft.colors.with_opacity(0.1, color), border_radius=30, content=ft.Icon(icono_code, color=color, size=30), alignment=ft.alignment.center),
                ft.VerticalDivider(width=20, color="transparent"),
                ft.Column([ft.Text(titulo, size=18, weight="bold", color="#212F3D"), ft.Text(subtitulo, size=12, color="grey")], alignment=ft.MainAxisAlignment.CENTER, spacing=2),
                ft.VerticalDivider(width=10, color="transparent"),
                ft.Icon("chevron_right", size=16, color="grey")
            ], alignment=ft.MainAxisAlignment.START)
        )
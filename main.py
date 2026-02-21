import flet as ft
from vistas import VistasManager

def main(page: ft.Page):
    # 1. CONFIGURACIÓN VISUAL (MODO MÓVIL)
    page.title = "Moda Spacio System 2.0"
    
    # 🖼️ EL LOGO DE LA APLICACIÓN
    page.window.icon = "logo.ico" # Si usas .ico, cámbialo a "logo.ico"
    
    # Tamaño simulado de celular (iPhone 14 Pro aprox)
    page.window_width = 390
    page.window_height = 844
    page.window_resizable = True 
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # --- CORRECCIÓN DEL COLOR DE FONDO ---
    page.bgcolor = "#F4F6F7"  # El fondo se define aquí ahora

    # Colores de la marca 
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary="#212F3D",      # Azul Oscuro 
            secondary="#28B463",    # Verde 
            surface="#FFFFFF",      # Blanco (Tarjetas)
            # Ya no ponemos 'background' aquí para evitar el error
        )
    )

    # 2. SISTEMA DE NAVEGACIÓN
    manager = VistasManager(page)

    # 3. ARRANCAR EN LOGIN
    page.on_route_change = manager.router
    page.go('/login')

# 🔥 IMPORTANTE: Agregamos assets_dir="assets" para que la App pueda leer el logo
ft.app(main, assets_dir="assets")
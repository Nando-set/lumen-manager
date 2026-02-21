import flet as ft
from vistas import VistasManager
import os

def main(page: ft.Page):
    # 1. CONFIGURACIÓN VISUAL (MODO MÓVIL)
    page.title = "Moda Spacio System 2.0"
    
    # 🖼️ EL LOGO DE LA APLICACIÓN
    page.window.icon = "logo.ico" 
    
    # Tamaño simulado para web
    page.window_width = 390
    page.window_height = 844
    page.window_resizable = True 
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # --- FONDO ---
    page.bgcolor = "#F4F6F7"  

    # Colores de la marca 
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary="#212F3D",      # Azul Oscuro 
            secondary="#28B463",    # Verde 
            surface="#FFFFFF",      # Blanco (Tarjetas)
        )
    )

    # 2. SISTEMA DE NAVEGACIÓN
    manager = VistasManager(page)

    # 3. ARRANCAR EN LOGIN
    page.on_route_change = manager.router
    page.go('/login')

# 🔥 CONFIGURACIÓN PARA EL DESPLIEGUE EN WEB 🔥
if __name__ == "__main__":
    # Render asigna un puerto dinámico mediante la variable de entorno PORT
    puerto = int(os.getenv("PORT", 8000))
    ft.app(
        target=main, 
        assets_dir="assets",
        view=ft.AppView.WEB_BROWSER,
        port=puerto,
        host="0.0.0.0" # IMPORTANTE: Permite que Render se conecte a la app
    )

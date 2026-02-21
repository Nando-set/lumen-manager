import math

class CalculadoraNegocio:
    def __init__(self):
        # Inventario Simulado (Luego vendrá de Supabase)
        self.inventario = {
            "Persiana Sheer": {"precio": 850.0, "limite_ancho": 2.5, "instalacion": 150.0},
            "Cortina Tradicional": {"precio": 1200.0, "limite_ancho": 2.5, "instalacion": 200.0},
            "Toldo Retráctil": {
                "precio": 13500.0,   # Precio A (< 3.30m)
                "precio_2": 16500.0, # Precio B (> 3.30m)
                "gatillo": 3.30,     # Punto de cambio
                "instalacion": 3500.0
            }
        }

    def obtener_precio_base(self, producto_nombre, ancho_m):
        """
        Regla de TOLDOS automática:
        Si es Toldo y mide más de 3.30, cambia el precio.
        """
        datos = self.inventario.get(producto_nombre, {})
        precio = datos.get("precio", 0.0)
        
        # Lógica de Gatillo (Precios dinámicos por medida)
        if "gatillo" in datos and ancho_m > datos["gatillo"]:
            precio = datos["precio_2"]
            
        return precio

    def calcular_instalaciones(self, producto_nombre, ancho_m):
        """
        Regla de CORTINAS:
        Cortinas NO suman piezas extra por ancho. El resto sí.
        """
        if ancho_m <= 0: return 0
        
        es_cortina = "Cortina" in producto_nombre
        
        if es_cortina:
            return 1 # Siempre 1 pieza de instalación
        else:
            # Persianas / Toldos: Se divide por el límite (ej. cada 2.5m)
            datos = self.inventario.get(producto_nombre, {})
            limite = datos.get("limite_ancho", 2.5)
            return math.ceil(ancho_m / limite)

    def calcular_item_carrito(self, producto, ancho, alto, precio_unitario, modo_manual=False):
        """
        Calcula el total de una línea.
        Soporta Modo Automático (m2) y Modo Manual (Input directo).
        """
        area = ancho * alto
        if modo_manual:
            # En manual, a veces el precio es fijo o por pieza, depende del usuario
            # Asumiremos lógica estándar: Precio * Area (o Precio * 1 si area es 0)
            factor = area if area > 0 else 1.0
            total = precio_unitario * factor
        else:
            # Automático
            total = area * precio_unitario
            
        return total

class GestorUsuarios:
    def es_admin(self, usuario):
        # Aquí validaremos si puede editar precios
        admins = ["dany", "karina", "nando"]
        return usuario.lower() in admins
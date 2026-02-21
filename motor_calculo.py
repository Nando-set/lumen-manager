import math

class MotorCalculo:
    def __init__(self):
        # Aquí definimos las constantes que ya tenías configuradas
        self.LIMITE_ANCHO_INST = 2.5  # Lo que usas para dividir piezas
    
    def calcular_instalacion(self, nombre_producto, ancho):
        """
        Copia exacta de tu lógica: 
        Si es cortina, piezas = 1. Si no, divide ancho/2.5 y redondea hacia arriba.
        """
        try:
            val_ancho = float(ancho)
            if val_ancho <= 0: return 0
            
            # Tu regla de oro: Cortinas no suman
            if "CORTINA" in nombre_producto.upper():
                return 1
            
            # Tu regla para persianas y toldos
            return math.ceil(val_ancho / self.LIMITE_ANCHO_INST)
        except:
            return 0

    def calcular_subtotal_item(self, precio, ancho, alto, cantidad=1):
        """
        Mantiene la precisión de tus cuentas actuales.
        """
        try:
            area = float(ancho) * float(alto)
            # Si el área es 0 (ej. un motor o cobro fijo), usamos solo el precio
            factor = area if area > 0 else 1.0
            return (precio * factor) * int(cantidad)
        except:
            return 0.0
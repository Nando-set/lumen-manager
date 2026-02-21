from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
from reportlab.lib import colors 
import os
from datetime import datetime # <--- Esto es vital

def pos(x_mm, y_mm):
    return (x_mm * mm, (279.4 - y_mm - 1.0) * mm)

def generar_pdf(datos, carrito, totales, nombre_archivo):
    c = canvas.Canvas(nombre_archivo, pagesize=letter)
    
    carpeta_base = os.path.dirname(os.path.abspath(__file__))
    ruta_plantilla = os.path.join(carpeta_base, "plantilla.png")
    
    if os.path.exists(ruta_plantilla):
        c.drawImage(ruta_plantilla, 0, 0, width=215.9*mm, height=279.4*mm)

    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 11)
    
    # Usamos la fecha real de hoy
    hoy = datetime.now()
    c.drawString(*pos(90.8065, 36.2686), str(hoy.day).zfill(2))
    c.drawString(*pos(106.8341, 36.2686), str(hoy.month).zfill(2))
    c.drawString(*pos(124.1327, 36.2686), str(hoy.year))
    
    c.drawString(*pos(48.2003, 49.3288), datos.get('cliente', ''))
    c.drawString(*pos(127.015, 49.3288), datos.get('telefono', ''))
    c.drawString(*pos(47.7526, 59.4168), datos.get('domicilio', ''))
    c.drawString(*pos(47.9327, 68.4259), datos.get('notas', ''))

    # 📅 INYECCIÓN DE LA FECHA Y HORA DE INSTALACIÓN
    fecha_entrega = f"{datos.get('fecha_instalacion', '')} {datos.get('hora_instalacion', '')}".strip()
    c.drawString(*pos(69.865, 209.4299), fecha_entrega)

    # Productos
    y_prod = 92.6225
    for i, item in enumerate(carrito):
        c.drawCentredString(24.2441*mm, (279.4 - y_prod)*mm, str(i + 1)) 
        desc = item['desc']
        if len(desc) > 65: desc = desc[:65] + "..." 
        c.drawString(35*mm, (279.4 - y_prod)*mm, desc)
        c.drawRightString(192*mm, (279.4 - y_prod)*mm, f"${item['subtotal']:,.2f}")
        y_prod += 7

    # Totales
    c.drawCentredString(*pos(62.859, 232.6232), f"${totales['anticipo']:,.2f}")
    c.drawCentredString(*pos(100.6703, 232.6232), f"${totales['saldo']:,.2f}")
    c.drawCentredString(*pos(139.9689, 232.6232), datos.get('vendedor', ''))
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(*pos(177.7178, 232.6232), f"${totales['total']:,.2f}")

    c.save()
    return nombre_archivo
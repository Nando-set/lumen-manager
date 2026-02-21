import os
from supabase import create_client

# 🔑 PON AQUÍ TUS CREDENCIALES DE SUPABASE
SUPABASE_URL = "https://lmccqzcorqridvbcboov.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxtY2NxemNvcnFyaWR2YmNib292Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE0ODQ1NTcsImV4cCI6MjA4NzA2MDU1N30.-QgS5U-qCOUMyy5YGllVEpNWIGnbJZ_gJwILNLr9S7Y"

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print("❌ Error al conectar. Revisa tus credenciales.")
    exit()

# 📦 LA LISTA DE PRODUCTOS PREPARADA (Añadido el campo 'tipo' para separar en pestañas)
productos_a_inyectar = [
    # --- CORTINAS Y PERSIANAS ---
    {"nombre": "Sheer Elegance (Básica)", "tipo": "Persiana", "precio_base": 650.0, "costo_instalacion": 150.0, "limite_ancho": 2.5, "precio_fabrica": 400.0},
    {"nombre": "Persiana Lisa (Blackout)", "tipo": "Persiana", "precio_base": 650.0, "costo_instalacion": 150.0, "limite_ancho": 2.5, "precio_fabrica": 295.0},
    {"nombre": "Cortina Onda Perfecta (Tergal)", "tipo": "Persiana", "precio_base": 800.0, "costo_instalacion": 150.0, "limite_ancho": 3.0, "precio_fabrica": 90.0},
    {"nombre": "Cortina Ojillo (Tergal)", "tipo": "Persiana", "precio_base": 800.0, "costo_instalacion": 150.0, "limite_ancho": 3.0, "precio_fabrica": 90.0},
    {"nombre": "Cortina Onda Perfecta (Blackout)", "tipo": "Persiana", "precio_base": 950.0, "costo_instalacion": 150.0, "limite_ancho": 3.0, "precio_fabrica": 320.0},
    {"nombre": "Cortina Ojillo (Blackout)", "tipo": "Persiana", "precio_base": 950.0, "costo_instalacion": 150.0, "limite_ancho": 3.0, "precio_fabrica": 320.0},
    
    # --- TOLDOS ---
    {"nombre": "Toldo Vertical", "tipo": "Toldo", "precio_base": 1450.0, "costo_instalacion": 800.0, "limite_ancho": 3.3, "precio_fabrica": 345.0},
    {"nombre": "Toldo Retráctil Pequeño", "tipo": "Toldo", "precio_base": 13500.0, "costo_instalacion": 0.0, "limite_ancho": 0.0, "precio_fabrica": 8500.0},
    {"nombre": "Toldo Retráctil Grande", "tipo": "Toldo", "precio_base": 16500.0, "costo_instalacion": 0.0, "limite_ancho": 0.0, "precio_fabrica": 10500.0},
    
    # --- MOTORES Y EXTRAS ---
    {"nombre": "Motor Extra", "tipo": "Motor", "precio_base": 3500.0, "costo_instalacion": 0.0, "limite_ancho": 0.0, "precio_fabrica": 2200.0}
]

print("🚀 Iniciando inyección masiva de productos en Supabase...\n")

for prod in productos_a_inyectar:
    try:
        # Insertamos directo a tu tabla 'productos'
        respuesta = supabase.table("productos").insert(prod).execute()
        print(f"✅ Inyectado con éxito: {prod['nombre']} ({prod['tipo']})")
    except Exception as e:
        print(f"❌ Falló al inyectar {prod['nombre']}: {e}")

print("\n🎉 ¡INYECCIÓN TERMINADA! Ya puedes borrar este archivo.")
print("Abre tu App Moda Spacio y ve al Cotizador o al Inventario para ver la magia.")
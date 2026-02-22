from supabase import create_client, Client
from datetime import datetime

class GestorNube:
    def __init__(self):
        self.url = "https://lmccqzcorqridvbcboov.supabase.co"
        self.key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxtY2NxemNvcnFyaWR2YmNib292Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE0ODQ1NTcsImV4cCI6MjA4NzA2MDU1N30.-QgS5U-qCOUMyy5YGllVEpNWIGnbJZ_gJwILNLr9S7Y"
        
        try:
            self.supabase: Client = create_client(self.url, self.key)
            self.conexion_activa = True
        except:
            self.conexion_activa = False

    # --- SECCIÓN USUARIOS ---
    def registrar_usuario(self, nombre_real, usuario, pin, codigo_secreto):
        """Registra empleado según el código de invitación"""
        if not self.conexion_activa: return False, "Sin conexión."
        
        if codigo_secreto == "0752MS": rol_asignado = "admin"
        elif codigo_secreto == "0147147": rol_asignado = "vendedor"
        else: return False, "❌ Código de autorización inválido."

        try:
            existe = self.supabase.table("usuarios").select("*").eq("usuario", usuario).execute()
            if len(existe.data) > 0: return False, "❌ Usuario ya ocupado."

            nuevo = {"nombre_real": nombre_real, "usuario": usuario, "pin": pin, "rol": rol_asignado}
            self.supabase.table("usuarios").insert(nuevo).execute()
            return True, f"✅ Registrado como {rol_asignado.upper()}."
        except Exception as e:
            return False, f"❌ Error: {e}"

    def verificar_login(self, usuario, pin):
        """Verifica si el usuario y PIN coinciden en Virginia"""
        if not self.conexion_activa: return False, None
        try:
            res = self.supabase.table("usuarios").select("*").eq("usuario", usuario).eq("pin", pin).execute()
            if len(res.data) > 0:
                return True, res.data[0] # Retorna los datos del usuario
            return False, None
        except:
            return False, None
            
    # --- SECCIÓN NOTIFICACIONES (¡NUEVO SISTEMA!) ---
    def crear_notificacion(self, receptor, mensaje, tipo):
        """Envía una alerta a la base de datos"""
        if not self.conexion_activa: return False
        try:
            datos = {
                "receptor": receptor, # Puede ser 'admin' o el nombre del vendedor
                "mensaje": mensaje,
                "tipo": tipo,
                "leida": False,
                "created_at": datetime.now().isoformat()
            }
            self.supabase.table("notificaciones").insert(datos).execute()
            return True
        except Exception as e:
            print(f"❌ Error al crear notificación: {e}")
            return False

    def obtener_notificaciones_no_leidas(self, receptor):
        """Descarga las alertas pendientes del usuario actual"""
        if not self.conexion_activa: return []
        try:
            res = self.supabase.table("notificaciones").select("*").eq("receptor", receptor).eq("leida", False).execute()
            return res.data
        except Exception as e:
            print(f"❌ Error al obtener notificaciones: {e}")
            return []

    def marcar_notificacion_leida(self, id_notif):
        """Apaga la alerta"""
        if not self.conexion_activa: return False
        try:
            self.supabase.table("notificaciones").update({"leida": True}).eq("id", id_notif).execute()
            return True
        except Exception as e:
            print(f"❌ Error al apagar notificación: {e}")
            return False

    # --- SECCIÓN VENTAS E INSTALACIONES ---
    def guardar_venta(self, datos_venta):
        if not self.conexion_activa: return False
        try:
            anticipo = float(datos_venta.get('anticipo', 0))
            estado_nota = "VENTA" if anticipo > 0 else "PENDIENTES"
            
            # 🔥 REGISTRO EN VENTAS (Con soporte para método de pago)
            registro = {
                "cliente": datos_venta.get('cliente'),
                "telefono": datos_venta.get('telefono'),
                "domicilio": datos_venta.get('domicilio'),
                "notas": datos_venta.get('notas'),
                "vendedor": datos_venta.get('vendedor'),
                "total": float(datos_venta.get('total')),
                "anticipo": anticipo,
                "saldo": float(datos_venta.get('saldo')),
                "metodo_pago": datos_venta.get('metodo_pago', 'Efectivo'), # Nuevo dato
                "estado": estado_nota,
                "costo_fabrica": float(datos_venta.get('costo_fabrica', 0.0)),
                "productos": datos_venta.get('productos'),
                "fecha_instalacion": datos_venta.get('fecha_instalacion', 'Por Asignar'),
                "hora_instalacion": datos_venta.get('hora_instalacion', 'Por Asignar'),
                "notas_instalacion": datos_venta.get('notas_instalacion', ''),
                "created_at": datetime.now().isoformat()
            }
            self.supabase.table("ventas").insert(registro).execute()
            
            # 🔥 LA MAGIA ARREGLADA: Pasa a la agenda INCLUYENDO EL DINERO
            if estado_nota == "VENTA":
                registro_inst = {
                    "vendedor": datos_venta.get('vendedor'),
                    "cliente": datos_venta.get('cliente'),
                    "telefono": datos_venta.get('telefono'),
                    "domicilio": datos_venta.get('domicilio'),
                    "productos": datos_venta.get('productos'),
                    "total": float(datos_venta.get('total')),         # 💸 ¡Dato Financiero Recuperado!
                    "anticipo": anticipo,                             # 💸 ¡Dato Financiero Recuperado!
                    "saldo": float(datos_venta.get('saldo')),         # 💸 ¡Dato Financiero Recuperado!
                    "fecha_instalacion": datos_venta.get('fecha_instalacion', 'Por Asignar'),
                    "hora_instalacion": datos_venta.get('hora_instalacion', 'Por Asignar'),
                    "notas_instalacion": datos_venta.get('notas_instalacion', ''),
                    "estado": "Por Agendar",
                    "created_at": datetime.now().isoformat()
                }
                self.supabase.table("instalaciones").insert(registro_inst).execute()
                
            return True
        except Exception as e:
            print(f"❌ Error al guardar venta: {e}")
            return False

    def obtener_instalaciones(self):
        """Descarga las instalaciones pendientes y programadas"""
        if not self.conexion_activa: return []
        try:
            response = self.supabase.table("instalaciones").select("*").execute()
            return response.data
        except Exception as e:
            print(f"❌ Error al obtener instalaciones: {e}")
            return []
            
    def actualizar_datos_cliente(self, nombre_cliente, nuevo_telefono, nueva_direccion):
        """Busca todas las notas de este cliente y le actualiza el teléfono y domicilio"""
        try:
            self.supabase.table("Ventas").update({
                "telefono": nuevo_telefono,
                "domicilio": nueva_direccion
            }).eq("cliente", nombre_cliente).execute()
            return True
        except Exception as e:
            print(f"Error al actualizar cliente: {e}")
            return False        
            
    # 🚀 NUEVA FUNCIÓN: Para que la jefa pueda editar desde la agenda
    def actualizar_instalacion(self, id_inst, datos_nuevos):
        """Actualiza fecha, hora, estado y notas de una instalación"""
        if not self.conexion_activa: return False
        try:
            self.supabase.table("instalaciones").update(datos_nuevos).eq("id", id_inst).execute()
            return True
        except Exception as e:
            print(f"❌ Error actualizando instalación: {e}")
            return False
            
    def obtener_historial_ventas(self):
        if not self.conexion_activa: return []
        try:
            response = self.supabase.table("ventas").select("*").execute()
            return response.data
        except Exception as e:
            print(f"❌ Error al obtener historial: {e}")
            return []
            
    def obtener_clientes_unicos(self):
        """Descarga el historial y extrae un diccionario de clientes sin repetir"""
        if not self.conexion_activa: return {}
        try:
            res = self.supabase.table("ventas").select("cliente, telefono, domicilio").execute()
            clientes_dict = {}
            for fila in res.data:
                nombre = fila.get("cliente", "").strip()
                if nombre and nombre not in clientes_dict:
                    clientes_dict[nombre] = {
                        "telefono": fila.get("telefono", ""),
                        "domicilio": fila.get("domicilio", "")
                    }
            return clientes_dict
        except Exception as e:
            print(f"❌ Error buscando clientes: {e}")
            return {}
            
    # --- SECCIÓN PRODUCTOS ---
    def obtener_productos(self):
        if not self.conexion_activa: return {}
        try:
            response = self.supabase.table("productos").select("*").execute()
            productos_dict = {}
            for p in response.data:
                productos_dict[p["nombre"]] = {
                    "precio": p.get("precio_base", 0.0),
                    "costo_instalacion": p.get("costo_instalacion", 0.0),
                    "limite_ancho": p.get("limite_ancho", 2.5),
                    "precio_2": p.get("precio_2", 0.0),
                    "limite_precio_2": p.get("limite_precio_2", 0.0),
                    "precio_fabrica": float(p.get("precio_fabrica") or 0.0) 
                }
            return productos_dict
        except Exception as e:
            print(f"❌ Error al obtener productos: {e}")
            return {}

    def actualizar_producto_completo(self, nombre, precio, costo_inst, limite_ancho, precio_2, limite_precio_2):
        try:
            datos = {
                "precio_base": float(precio),
                "costo_instalacion": float(costo_inst),
                "limite_ancho": float(limite_ancho),
                "precio_2": float(precio_2),
                "limite_precio_2": float(limite_precio_2)
            }
            self.supabase.table("productos").update(datos).eq("nombre", nombre).execute()
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def agregar_producto_completo(self, nombre, precio, costo_inst, limite_ancho, precio_2, limite_precio_2):
        try:
            datos = {
                "nombre": nombre, "precio_base": float(precio), "costo_instalacion": float(costo_inst),
                "limite_ancho": float(limite_ancho), "precio_2": float(precio_2),
                "limite_precio_2": float(limite_precio_2), "tipo": "Persiana"
            }
            self.supabase.table("productos").insert(datos).execute()
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def eliminar_producto(self, nombre_producto):
        try:
            self.supabase.table("productos").delete().eq("nombre", nombre_producto).execute()
            return True
        except: return False
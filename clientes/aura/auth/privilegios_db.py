#!/usr/bin/env python3
"""
🔐 Módulo de Privilegios de Acceso a Bases de Datos
Define qué tablas y operaciones puede realizar cada tipo de usuario
"""

from typing import Dict, List, Optional, Set
from enum import Enum
from clientes.aura.utils.error_logger import registrar_error

class TipoUsuario(Enum):
    """Tipos de usuario en el sistema"""
    SUPERADMIN = "superadmin"
    ADMIN = "admin" 
    INTERNO = "interno"
    SUPERVISOR = "supervisor"
    CLIENTE = "cliente"
    VISITANTE = "visitante"

class TipoOperacion(Enum):
    """Tipos de operaciones en BD"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"

class PrivilegiosDB:
    """
    Maneja los privilegios de acceso a bases de datos según el tipo de usuario
    """
    
    # Definición de privilegios por tabla y tipo de usuario
    PRIVILEGIOS_TABLAS = {
        # 👑 TABLAS DE ADMINISTRACIÓN - Solo SuperAdmin/Admin
        "usuarios_clientes": {
            TipoUsuario.SUPERADMIN: [TipoOperacion.READ, TipoOperacion.WRITE, TipoOperacion.DELETE, TipoOperacion.ADMIN],
            TipoUsuario.ADMIN: [TipoOperacion.READ, TipoOperacion.WRITE],
            TipoUsuario.INTERNO: [TipoOperacion.READ],
            TipoUsuario.SUPERVISOR: [TipoOperacion.READ],
        },
        
        "configuracion_bot": {
            TipoUsuario.SUPERADMIN: [TipoOperacion.READ, TipoOperacion.WRITE, TipoOperacion.DELETE, TipoOperacion.ADMIN],
            TipoUsuario.ADMIN: [TipoOperacion.READ, TipoOperacion.WRITE],
            TipoUsuario.INTERNO: [TipoOperacion.READ],
        },
        
        "cliente_empresas": {
            TipoUsuario.SUPERADMIN: [TipoOperacion.READ, TipoOperacion.WRITE, TipoOperacion.DELETE, TipoOperacion.ADMIN],
            TipoUsuario.ADMIN: [TipoOperacion.READ, TipoOperacion.WRITE],
            TipoUsuario.INTERNO: [TipoOperacion.READ],
            TipoUsuario.SUPERVISOR: [TipoOperacion.READ],
            TipoUsuario.CLIENTE: [TipoOperacion.READ],  # Solo sus propias empresas
        },
        
        # 📊 TABLAS DE DATOS OPERACIONALES
        "clientes": {
            TipoUsuario.SUPERADMIN: [TipoOperacion.READ, TipoOperacion.WRITE, TipoOperacion.DELETE, TipoOperacion.ADMIN],
            TipoUsuario.ADMIN: [TipoOperacion.READ, TipoOperacion.WRITE, TipoOperacion.DELETE],
            TipoUsuario.INTERNO: [TipoOperacion.READ, TipoOperacion.WRITE],
            TipoUsuario.SUPERVISOR: [TipoOperacion.READ, TipoOperacion.WRITE],
            TipoUsuario.CLIENTE: [TipoOperacion.READ],  # Solo sus propios datos
        },
        
        "contactos": {
            TipoUsuario.SUPERADMIN: [TipoOperacion.READ, TipoOperacion.WRITE, TipoOperacion.DELETE, TipoOperacion.ADMIN],
            TipoUsuario.ADMIN: [TipoOperacion.READ, TipoOperacion.WRITE, TipoOperacion.DELETE],
            TipoUsuario.INTERNO: [TipoOperacion.READ, TipoOperacion.WRITE],
            TipoUsuario.SUPERVISOR: [TipoOperacion.READ, TipoOperacion.WRITE],
            TipoUsuario.CLIENTE: [TipoOperacion.READ],  # Solo sus contactos
        },
        
        "conversaciones": {
            TipoUsuario.SUPERADMIN: [TipoOperacion.READ, TipoOperacion.WRITE, TipoOperacion.DELETE, TipoOperacion.ADMIN],
            TipoUsuario.ADMIN: [TipoOperacion.READ, TipoOperacion.WRITE],
            TipoUsuario.INTERNO: [TipoOperacion.READ, TipoOperacion.WRITE],
            TipoUsuario.SUPERVISOR: [TipoOperacion.READ],
            TipoUsuario.CLIENTE: [TipoOperacion.READ],  # Solo sus conversaciones
        },
        
        # 🧠 TABLAS DE CONOCIMIENTO
        "base_conocimiento": {
            TipoUsuario.SUPERADMIN: [TipoOperacion.READ, TipoOperacion.WRITE, TipoOperacion.DELETE, TipoOperacion.ADMIN],
            TipoUsuario.ADMIN: [TipoOperacion.READ, TipoOperacion.WRITE, TipoOperacion.DELETE],
            TipoUsuario.INTERNO: [TipoOperacion.READ, TipoOperacion.WRITE],
            TipoUsuario.SUPERVISOR: [TipoOperacion.READ, TipoOperacion.WRITE],
            TipoUsuario.CLIENTE: [TipoOperacion.READ, TipoOperacion.WRITE],  # Solo su base de conocimiento
        },
        
        "entrenamientos": {
            TipoUsuario.SUPERADMIN: [TipoOperacion.READ, TipoOperacion.WRITE, TipoOperacion.DELETE, TipoOperacion.ADMIN],
            TipoUsuario.ADMIN: [TipoOperacion.READ, TipoOperacion.WRITE],
            TipoUsuario.INTERNO: [TipoOperacion.READ, TipoOperacion.WRITE],
            TipoUsuario.SUPERVISOR: [TipoOperacion.READ],
            TipoUsuario.CLIENTE: [TipoOperacion.READ, TipoOperacion.WRITE],  # Solo sus entrenamientos
        },
        
        # 📈 TABLAS DE MÉTRICAS Y LOGS
        "metricas_uso": {
            TipoUsuario.SUPERADMIN: [TipoOperacion.READ, TipoOperacion.WRITE, TipoOperacion.DELETE, TipoOperacion.ADMIN],
            TipoUsuario.ADMIN: [TipoOperacion.READ, TipoOperacion.WRITE],
            TipoUsuario.INTERNO: [TipoOperacion.READ],
            TipoUsuario.SUPERVISOR: [TipoOperacion.READ],
            TipoUsuario.CLIENTE: [TipoOperacion.READ],  # Solo sus métricas
        },
        
        "logs_sistema": {
            TipoUsuario.SUPERADMIN: [TipoOperacion.READ, TipoOperacion.WRITE, TipoOperacion.DELETE, TipoOperacion.ADMIN],
            TipoUsuario.ADMIN: [TipoOperacion.READ],
            TipoUsuario.INTERNO: [TipoOperacion.READ],
        },
        
        # 💰 TABLAS FINANCIERAS - Solo Admin+
        "facturacion": {
            TipoUsuario.SUPERADMIN: [TipoOperacion.READ, TipoOperacion.WRITE, TipoOperacion.DELETE, TipoOperacion.ADMIN],
            TipoUsuario.ADMIN: [TipoOperacion.READ, TipoOperacion.WRITE],
        },
        
        "pagos": {
            TipoUsuario.SUPERADMIN: [TipoOperacion.READ, TipoOperacion.WRITE, TipoOperacion.DELETE, TipoOperacion.ADMIN],
            TipoUsuario.ADMIN: [TipoOperacion.READ],
        }
    }

    @classmethod
    def determinar_tipo_usuario(cls, usuario: Dict) -> TipoUsuario:
        """
        Determina el tipo de usuario basado en sus datos
        """
        if not usuario:
            return TipoUsuario.VISITANTE
        
        rol = usuario.get("rol", "").lower()
        es_supervisor = usuario.get("es_supervisor", False)
        modulos = usuario.get("modulos", [])
        
        # Verificar SuperAdmin
        if rol == "superadmin":
            return TipoUsuario.SUPERADMIN
        
        # Verificar Admin
        if rol in ["admin", "administrador"]:
            return TipoUsuario.ADMIN
        
        # Verificar Interno
        if rol == "interno":
            return TipoUsuario.INTERNO
        
        # Verificar Supervisor
        if es_supervisor or rol == "supervisor":
            return TipoUsuario.SUPERVISOR
        
        # Verificar por módulos
        if isinstance(modulos, list):
            modulos_admin = ["admin", "administracion", "configuracion"]
            if any(mod.lower() in modulos_admin for mod in modulos):
                return TipoUsuario.ADMIN
        elif isinstance(modulos, dict):
            for modulo, permisos in modulos.items():
                if isinstance(permisos, dict) and permisos.get("admin", False):
                    return TipoUsuario.ADMIN
        
        # Por defecto es cliente si está en usuarios_clientes
        if usuario.get("tipo") == "usuario_cliente":
            return TipoUsuario.CLIENTE
        
        return TipoUsuario.VISITANTE

    @classmethod
    def tiene_acceso(cls, usuario: Dict, tabla: str, operacion: TipoOperacion) -> bool:
        """
        Verifica si un usuario tiene acceso a una tabla con una operación específica
        """
        try:
            tipo_usuario = cls.determinar_tipo_usuario(usuario)
            
            # Si la tabla no está definida, denegar acceso
            if tabla not in cls.PRIVILEGIOS_TABLAS:
                print(f"⚠️ Tabla '{tabla}' no definida en privilegios")
                return False
            
            # Obtener privilegios para la tabla
            privilegios_tabla = cls.PRIVILEGIOS_TABLAS[tabla]
            
            # Verificar si el tipo de usuario tiene privilegios en esta tabla
            if tipo_usuario not in privilegios_tabla:
                print(f"❌ Usuario tipo {tipo_usuario.value} sin acceso a tabla '{tabla}'")
                return False
            
            # Verificar si tiene la operación específica
            operaciones_permitidas = privilegios_tabla[tipo_usuario]
            tiene_permiso = operacion in operaciones_permitidas
            
            print(f"🔍 Usuario {tipo_usuario.value} -> Tabla '{tabla}' -> Operación {operacion.value}: {'✅' if tiene_permiso else '❌'}")
            
            return tiene_permiso
            
        except Exception as e:
            registrar_error("Privilegios", f"Error verificando acceso: {e}")
            return False

    @classmethod
    def obtener_tablas_accesibles(cls, usuario: Dict, operacion: TipoOperacion) -> List[str]:
        """
        Obtiene lista de tablas accesibles para un usuario con una operación específica
        """
        try:
            tipo_usuario = cls.determinar_tipo_usuario(usuario)
            tablas_accesibles = []
            
            for tabla, privilegios in cls.PRIVILEGIOS_TABLAS.items():
                if tipo_usuario in privilegios and operacion in privilegios[tipo_usuario]:
                    tablas_accesibles.append(tabla)
            
            return tablas_accesibles
            
        except Exception as e:
            registrar_error("Privilegios", f"Error obteniendo tablas accesibles: {e}")
            return []

    @classmethod 
    def obtener_operaciones_permitidas(cls, usuario: Dict, tabla: str) -> List[TipoOperacion]:
        """
        Obtiene las operaciones permitidas para un usuario en una tabla específica
        """
        try:
            tipo_usuario = cls.determinar_tipo_usuario(usuario)
            
            if tabla not in cls.PRIVILEGIOS_TABLAS:
                return []
            
            privilegios_tabla = cls.PRIVILEGIOS_TABLAS[tabla]
            
            if tipo_usuario not in privilegios_tabla:
                return []
            
            return privilegios_tabla[tipo_usuario]
            
        except Exception as e:
            registrar_error("Privilegios", f"Error obteniendo operaciones permitidas: {e}")
            return []

    @classmethod
    def generar_reporte_privilegios(cls, usuario: Dict) -> Dict:
        """
        Genera un reporte completo de privilegios para un usuario
        """
        tipo_usuario = cls.determinar_tipo_usuario(usuario)
        reporte = {
            "usuario": usuario.get("nombre", "Sin nombre"),
            "tipo": tipo_usuario.value,
            "tablas_acceso": {},
            "resumen": {
                "total_tablas": len(cls.PRIVILEGIOS_TABLAS),
                "tablas_con_acceso": 0,
                "solo_lectura": 0,
                "lectura_escritura": 0,
                "acceso_admin": 0
            }
        }
        
        for tabla, privilegios in cls.PRIVILEGIOS_TABLAS.items():
            if tipo_usuario in privilegios:
                operaciones = privilegios[tipo_usuario]
                reporte["tablas_acceso"][tabla] = [op.value for op in operaciones]
                reporte["resumen"]["tablas_con_acceso"] += 1
                
                if TipoOperacion.ADMIN in operaciones:
                    reporte["resumen"]["acceso_admin"] += 1
                elif TipoOperacion.WRITE in operaciones:
                    reporte["resumen"]["lectura_escritura"] += 1
                elif TipoOperacion.READ in operaciones:
                    reporte["resumen"]["solo_lectura"] += 1
        
        return reporte

# Decorador para verificar privilegios automáticamente
def requiere_privilegio(tabla: str, operacion: TipoOperacion):
    """
    Decorador para verificar privilegios antes de ejecutar una función
    """
    def decorador(func):
        def wrapper(usuario, *args, **kwargs):
            if not PrivilegiosDB.tiene_acceso(usuario, tabla, operacion):
                raise PermissionError(f"Usuario sin privilegios para {operacion.value} en tabla {tabla}")
            return func(usuario, *args, **kwargs)
        return wrapper
    return decorador

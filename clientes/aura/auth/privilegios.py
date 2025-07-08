#!/usr/bin/env python3
"""
🔒 Sistema de Privilegios y Gestión de Acceso a Bases de Datos
Controla qué usuarios pueden acceder a qué tablas según su tipo y rol
"""

from typing import Dict, List, Optional, Union

class PrivilegiosManager:
    """
    Gestor de privilegios que determina el acceso a bases de datos
    según el tipo de usuario y su rol
    """
    
    def __init__(self, usuario: Dict):
        """
        Inicializa el gestor con los datos del usuario
        """
        self.usuario = usuario
        self.tipo_usuario = self._determinar_tipo_usuario()
        
    def _determinar_tipo_usuario(self) -> str:
        """
        Determina el tipo de usuario basado en sus datos
        """
        if not self.usuario:
            return "anonimo"
            
        tipo = self.usuario.get("tipo", "")
        rol = self.usuario.get("rol", "").lower()
        es_supervisor = self.usuario.get("es_supervisor", False)
        
        # SuperAdmin / Admin supremo
        if rol in ["superadmin", "super_admin"]:
            return "superadmin"
            
        # Admin / Administrador
        if rol in ["admin", "administrador", "interno"] or es_supervisor:
            return "admin"
            
        # Usuario interno (empleado)
        if tipo == "usuario_cliente":
            return "usuario_interno"
            
        # Cliente registrado
        if tipo == "cliente":
            return "cliente"
            
        # Visitante sin identificar
        return "visitante"
    
    def get_tipo_usuario(self) -> str:
        """Retorna el tipo de usuario determinado"""
        return self.tipo_usuario
    
    def _definir_privilegios_tabla(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Define los privilegios por tabla para cada tipo de usuario
        """
        return {
            # 👑 SUPERADMIN - Acceso total a todo
            "superadmin": {
                "usuarios_clientes": ["read", "write", "admin"],
                "configuracion_bot": ["read", "write", "admin"],
                "base_conocimiento": ["read", "write", "admin"],
                "clientes": ["read", "write", "admin"],
                "cliente_empresas": ["read", "write", "admin"],
                "tareas": ["read", "write", "admin"],  # 🆕 Gestión completa de tareas
                "facturacion": ["read", "write", "admin"],
                "logs_sistema": ["read", "write", "admin"],
                "meta_ads_anuncios": ["read", "write", "admin"],
                "meta_ads_cuentas": ["read", "write", "admin"],
                "reportes": ["read", "write", "admin"],
                "configuracion_global": ["read", "write", "admin"]
            },
            
            # 🛡️ ADMIN - Acceso amplio pero sin algunas funciones críticas
            "admin": {
                "usuarios_clientes": ["read", "write"],  # Sin admin total
                "configuracion_bot": ["read", "write"],
                "base_conocimiento": ["read", "write", "admin"],
                "clientes": ["read", "write", "admin"],
                "cliente_empresas": ["read", "write", "admin"],
                "tareas": ["read", "write"],  # 🆕 Gestión de tareas sin admin total
                "facturacion": ["read"],  # Solo lectura
                "logs_sistema": ["read"],  # Solo lectura
                "meta_ads_anuncios": ["read", "write"],
                "meta_ads_cuentas": ["read", "write"],
                "reportes": ["read", "write"]
            },
            
            # 👨‍💼 USUARIO INTERNO - Acceso a funciones de trabajo
            "usuario_interno": {
                "configuracion_bot": ["read"],  # Solo lectura
                "base_conocimiento": ["read", "write"],  # Su área de trabajo
                "clientes": ["read", "write"],  # Gestión de clientes
                "cliente_empresas": ["read", "write"],
                "tareas": ["read", "write"],  # 🆕 Gestión de tareas asignadas
                "meta_ads_anuncios": ["read", "write"],
                "meta_ads_cuentas": ["read"],
                "reportes": ["read"]
            },
            
            # 👤 CLIENTE - Acceso limitado a sus datos
            "cliente": {
                "base_conocimiento": ["read", "write"],  # Su IA
                "clientes": ["read"],  # Sus propios datos
                "cliente_empresas": ["read"],  # Sus empresas
                "tareas": ["read"],  # 🆕 Solo sus tareas asignadas
                "reportes": ["read"]  # Sus reportes
            },
            
            # 🌐 VISITANTE - Acceso mínimo
            "visitante": {
                "base_conocimiento": ["read"]  # Solo consulta básica
            },
            
            # 🚫 ANÓNIMO - Sin acceso
            "anonimo": {}
        }
    
    def puede_acceder(self, tabla: str, operacion: str = "read") -> bool:
        """
        Verifica si el usuario puede realizar una operación en una tabla
        
        Args:
            tabla: Nombre de la tabla
            operacion: Tipo de operación ("read", "write", "admin")
            
        Returns:
            bool: True si tiene acceso, False si no
        """
        privilegios = self._definir_privilegios_tabla()
        
        # Obtener privilegios del tipo de usuario
        privilegios_usuario = privilegios.get(self.tipo_usuario, {})
        
        # Verificar si tiene acceso a la tabla
        if tabla not in privilegios_usuario:
            print(f"❌ Usuario tipo {self.tipo_usuario} sin acceso a tabla '{tabla}'")
            return False
        
        # Verificar si puede realizar la operación
        operaciones_permitidas = privilegios_usuario[tabla]
        tiene_acceso = operacion in operaciones_permitidas
        
        if tiene_acceso:
            print(f"🔍 Usuario {self.tipo_usuario} -> Tabla '{tabla}' -> Operación {operacion}: ✅")
        else:
            print(f"🔍 Usuario {self.tipo_usuario} -> Tabla '{tabla}' -> Operación {operacion}: ❌")
            
        return tiene_acceso
    
    def obtener_tablas_accesibles(self, operacion: str = "read") -> List[str]:
        """
        Obtiene lista de tablas a las que el usuario puede acceder
        """
        privilegios = self._definir_privilegios_tabla()
        privilegios_usuario = privilegios.get(self.tipo_usuario, {})
        
        tablas_accesibles = []
        for tabla, operaciones in privilegios_usuario.items():
            if operacion in operaciones:
                tablas_accesibles.append(tabla)
                
        return tablas_accesibles
    
    def obtener_resumen_privilegios(self) -> Dict[str, Dict[str, bool]]:
        """
        Obtiene un resumen completo de todos los privilegios del usuario
        """
        privilegios = self._definir_privilegios_tabla()
        privilegios_usuario = privilegios.get(self.tipo_usuario, {})
        
        resumen = {}
        for tabla, operaciones in privilegios_usuario.items():
            resumen[tabla] = {
                "read": "read" in operaciones,
                "write": "write" in operaciones,
                "admin": "admin" in operaciones
            }
            
        return resumen
    
    def es_operacion_critica(self, tabla: str, operacion: str) -> bool:
        """
        Determina si una operación es considerada crítica
        """
        operaciones_criticas = {
            "usuarios_clientes": ["write", "admin"],
            "configuracion_bot": ["write", "admin"],
            "facturacion": ["write", "admin"],
            "logs_sistema": ["write", "admin"],
            "configuracion_global": ["write", "admin"]
        }
        
        tabla_critica = operaciones_criticas.get(tabla, [])
        return operacion in tabla_critica
    
    def registrar_acceso(self, tabla: str, operacion: str, exitoso: bool = True):
        """
        Registra un intento de acceso para auditoria
        """
        status = "PERMITIDO" if exitoso else "DENEGADO"
        es_critica = "🔥" if self.es_operacion_critica(tabla, operacion) else "📝"
        
        print(f"{es_critica} ACCESO {status}: {self.tipo_usuario} -> {tabla}.{operacion}")
        
        # Aquí podrías enviar a logs o base de datos para auditoria
        # supabase.table("logs_acceso").insert({
        #     "usuario_id": self.usuario.get("id"),
        #     "tabla": tabla,
        #     "operacion": operacion,
        #     "exitoso": exitoso,
        #     "timestamp": datetime.now()
        # })

def crear_manager_privilegios(usuario: Dict) -> PrivilegiosManager:
    """
    Factory function para crear un gestor de privilegios
    """
    return PrivilegiosManager(usuario)

def verificar_acceso_rapido(usuario: Dict, tabla: str, operacion: str = "read") -> bool:
    """
    Función de conveniencia para verificación rápida de acceso
    """
    manager = PrivilegiosManager(usuario)
    return manager.puede_acceder(tabla, operacion)

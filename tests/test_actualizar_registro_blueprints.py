#!/usr/bin/env python3
"""
🔄 SCRIPT: Actualizar registro de blueprints optimizados
Registra el nuevo módulo facebook_detalle y optimiza el principal
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from clientes.aura.utils.supabase_client import supabase

def actualizar_registro_blueprints():
    """Actualizar tabla modulos_disponibles con nuevos módulos optimizados"""
    
    print("🔄 Actualizando registro de blueprints...")
    
    # 1. Verificar si redes_sociales ya existe
    result = supabase.table('modulos_disponibles').select('*').eq('nombre', 'redes_sociales').execute()
    
    if not result.data:
        # Crear registro para redes_sociales si no existe
        nuevo_modulo = {
            'nombre': 'redes_sociales',
            'descripcion': 'Gestión de redes sociales - Módulo principal optimizado',
            'icono': '🌐',
            'ruta': 'panel_cliente_redes_sociales.panel_cliente_redes_sociales_bp'
        }
        
        insert_result = supabase.table('modulos_disponibles').insert(nuevo_modulo).execute()
        print(f"✅ Módulo redes_sociales creado: {insert_result.data}")
    else:
        # Actualizar ruta al módulo optimizado
        update_result = supabase.table('modulos_disponibles').update({
            'ruta': 'panel_cliente_redes_sociales.panel_cliente_redes_sociales_bp',
            'descripcion': 'Gestión de redes sociales - Módulo principal optimizado'
        }).eq('nombre', 'redes_sociales').execute()
        print(f"✅ Módulo redes_sociales actualizado: {update_result.data}")
    
    # 2. Agregar facebook_detalle como módulo independiente
    detalle_result = supabase.table('modulos_disponibles').select('*').eq('nombre', 'facebook_detalle').execute()
    
    if not detalle_result.data:
        modulo_detalle = {
            'nombre': 'facebook_detalle',
            'descripcion': 'Detalle optimizado de páginas Facebook',
            'icono': '📘',
            'ruta': 'panel_cliente_redes_sociales.facebook_detalle_bp'
        }
        
        insert_detalle = supabase.table('modulos_disponibles').insert(modulo_detalle).execute()
        print(f"✅ Módulo facebook_detalle creado: {insert_detalle.data}")
    else:
        print("ℹ️ Módulo facebook_detalle ya existe")
    
    # 3. Verificar configuración de aura
    config_result = supabase.table('configuracion_bot').select('modulos').eq('nombre_nora', 'aura').execute()
    
    if config_result.data:
        modulos_actuales = config_result.data[0].get('modulos', {})
        
        # Asegurar que ambos módulos estén activos
        modulos_actuales['redes_sociales'] = True
        modulos_actuales['facebook_detalle'] = True
        
        update_config = supabase.table('configuracion_bot').update({
            'modulos': modulos_actuales
        }).eq('nombre_nora', 'aura').execute()
        
        print(f"✅ Configuración de aura actualizada: {update_config.data}")
    
    print("🎉 Registro de blueprints actualizado exitosamente!")

if __name__ == "__main__":
    actualizar_registro_blueprints()

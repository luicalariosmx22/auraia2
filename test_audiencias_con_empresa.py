#!/usr/bin/env python3
"""
Script para probar las audiencias con información de empresa
"""

import sys
sys.path.append('.')

from clientes.aura.routes.panel_cliente_meta_ads.campanas import obtener_audiencias_con_filtros

def main():
    print("🧪 PRUEBA DE AUDIENCIAS CON INFORMACIÓN DE EMPRESA")
    print("=" * 60)
    
    # Obtener audiencias con filtros
    print("📋 Obteniendo audiencias para 'aura'...")
    audiencias = obtener_audiencias_con_filtros('aura', {})
    
    if not audiencias:
        print("❌ No se encontraron audiencias")
        return
    
    print(f"✅ Se encontraron {len(audiencias)} audiencias")
    print()
    
    # Mostrar las primeras 5 audiencias con información de empresa
    print("📊 PRIMERAS 5 AUDIENCIAS CON INFORMACIÓN DE EMPRESA:")
    print("-" * 60)
    
    for i, audiencia in enumerate(audiencias[:5]):
        print(f"\n🔸 Audiencia {i+1}:")
        print(f"   ID: {audiencia.get('audience_id', 'N/A')}")
        print(f"   Nombre: {audiencia.get('nombre_audiencia', 'N/A')}")
        print(f"   Empresa: {audiencia.get('nombre_empresa', 'Sin empresa')}")
        print(f"   Cliente: {audiencia.get('nombre_cliente', 'Sin cliente')}")
        print(f"   Tipo: {audiencia.get('tipo_audiencia', 'N/A')}")
        print(f"   Estado: {audiencia.get('estado', 'N/A')}")
        print(f"   Tamaño: {audiencia.get('tamaño_fmt', '0')}")
        print(f"   Origen: {audiencia.get('origen', 'N/A')}")
        print(f"   Creada: {audiencia.get('creada_en_fmt', 'N/A')}")
    
    # Estadísticas por empresa
    empresas = {}
    for audiencia in audiencias:
        empresa = audiencia.get('nombre_empresa', 'Sin empresa')
        if empresa not in empresas:
            empresas[empresa] = 0
        empresas[empresa] += 1
    
    print(f"\n📈 DISTRIBUCIÓN POR EMPRESA:")
    print("-" * 40)
    for empresa, cantidad in sorted(empresas.items(), key=lambda x: x[1], reverse=True):
        print(f"   {empresa}: {cantidad} audiencias")

if __name__ == "__main__":
    main()

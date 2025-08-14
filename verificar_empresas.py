from clientes.aura.utils.supabase_client import supabase

print("🔍 VERIFICANDO EMPRESAS")
print("=" * 50)

try:
    # Verificar todas las empresas
    result = supabase.table('cliente_empresas').select('*').execute()
    print(f"📊 Total empresas encontradas: {len(result.data)}")
    
    if result.data:
        print("\n📋 Empresas disponibles:")
        for empresa in result.data:
            print(f"   - {empresa.get('nombre_empresa')} (ID: {empresa.get('id')}, Nora: {empresa.get('nombre_nora')})")
    else:
        print("❌ No hay empresas en la tabla")
    
    # Verificar específicamente para nora 'aura'
    print("\n🎯 Verificando empresas para nora 'aura':")
    result_aura = supabase.table('cliente_empresas').select('*').eq('nombre_nora', 'aura').execute()
    print(f"📊 Empresas para aura: {len(result_aura.data)}")
    
    if result_aura.data:
        for empresa in result_aura.data:
            print(f"   ✅ {empresa.get('nombre_empresa')} (ID: {empresa.get('id')})")
    else:
        print("❌ No hay empresas para nora aura")
        
except Exception as e:
    print(f"❌ Error: {e}")

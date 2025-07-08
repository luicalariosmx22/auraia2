from keywords_generator import KeywordsExcelToSQL

print("🧪 Probando filtrado de filas de totales...")

gen = KeywordsExcelToSQL()
success = gen.process_excel_to_sql('ejemplo_keywords_con_totales.xlsx', 'test_filtered_keywords.sql')

print(f"✅ Test result: {'Success' if success else 'Failed'}")

if success:
    # Leer y mostrar el resultado
    try:
        with open('test_filtered_keywords.sql', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Contar líneas INSERT
        insert_count = content.count('INSERT INTO')
        print(f"📊 Sentencias INSERT generadas: {insert_count}")
        
        if insert_count > 0:
            print("\n📝 Primeras líneas del SQL generado:")
            lines = content.split('\n')[:10]
            for line in lines:
                print(f"  {line}")
        
    except Exception as e:
        print(f"❌ Error leyendo resultado: {e}")

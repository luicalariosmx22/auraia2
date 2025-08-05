from clientes.aura.utils.supabase_client import supabase

def obtener_columnas_tabla(tabla):
    """
    Obtiene las columnas disponibles para una tabla dada
    """
    try:
        columnas = supabase.table(tabla).select('*').limit(1).execute()
        if columnas.data:
            return list(columnas.data[0].keys())
        return []
    except Exception as e:
        print(f"Error al obtener columnas de {tabla}: {e}")
        return []

def obtener_nombres_batch(object_ids, access_token, tipo='campaign', batch_size=50):
    """
    Obtiene nombres de múltiples objetos usando batch requests
    """
    if not object_ids:
        return {}
    
    nombres = {}
    import requests
    import time
    
    for i in range(0, len(object_ids), batch_size):
        batch = object_ids[i:i + batch_size]
        fields = 'id,name' if tipo == 'campaign' else 'id,name'
        
        try:
            ids_str = ','.join(batch)
            url = f"https://graph.facebook.com/v19.0/?ids={ids_str}&fields={fields}&access_token={access_token}"
            r = requests.get(url, timeout=10)
            
            if r.status_code == 200:
                data = r.json()
                for id_, info in data.items():
                    nombres[id_] = info.get('name', f"{tipo} {id_}")
            else:
                print(f"Error {r.status_code} obteniendo nombres batch: {r.text}")
                
        except Exception as e:
            print(f"Error en batch request: {e}")
            continue
            
        time.sleep(1)  # Pausa entre batches
        
    return nombres

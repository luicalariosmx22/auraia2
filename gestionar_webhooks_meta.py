#!/usr/bin/env python3
"""
Script mejorado para gestionar webhooks de Meta - evitar duplicados
"""
import os
import requests
from dotenv import load_dotenv

def gestionar_webhooks_meta():
    """Gestiona webhooks de Meta evitando duplicados"""
    load_dotenv()
    
    app_id = os.getenv('META_APP_ID')
    app_secret = os.getenv('META_APP_SECRET')
    webhook_url = os.getenv('META_WEBHOOK_URL')
    webhook_verify_token = os.getenv('META_WEBHOOK_VERIFY_TOKEN', 'nora123')
    
    print('🔧 GESTIÓN DE WEBHOOKS META')
    print('=' * 50)
    
    app_access_token = f'{app_id}|{app_secret}'
    
    # 1. Obtener suscripciones existentes
    print('1. 📋 Obteniendo suscripciones existentes...')
    url = f'https://graph.facebook.com/v18.0/{app_id}/subscriptions'
    params = {'access_token': app_access_token}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            print(f'❌ Error obteniendo suscripciones: {response.text}')
            return
        
        data = response.json()
        suscripciones_existentes = data.get('data', [])
        
        # Mostrar suscripciones existentes
        print(f'   Encontradas {len(suscripciones_existentes)} suscripciones:')
        objetos_existentes = []
        
        for sub in suscripciones_existentes:
            objeto = sub.get('object')
            callback_url = sub.get('callback_url', '')
            activa = sub.get('active', False)
            objetos_existentes.append(objeto)
            
            estado = '✅ Activa' if activa else '❌ Inactiva'
            print(f'     • {objeto}: {estado} -> {callback_url}')
        
        # 2. Verificar si necesitamos agregar 'page'
        print('\n2. 🔍 Verificando necesidad de suscripción a pages...')
        
        if 'page' in objetos_existentes:
            print('   ✅ Ya existe suscripción a "page"')
            # Verificar si está activa y con la URL correcta
            page_sub = next((s for s in suscripciones_existentes if s.get('object') == 'page'), None)
            if page_sub:
                if page_sub.get('active') and page_sub.get('callback_url') == webhook_url:
                    print('   ✅ Suscripción "page" está activa y configurada correctamente')
                else:
                    print('   ⚠️  Suscripción "page" existe pero puede necesitar actualización')
        else:
            print('   ℹ️  No existe suscripción a "page", la crearemos...')
            
            # Crear suscripción a page
            data_page = {
                'object': 'page',
                'callback_url': webhook_url,
                'fields': ['feed', 'leadgen'],
                'verify_token': webhook_verify_token,
                'access_token': app_access_token
            }
            
            try:
                response = requests.post(url, data=data_page, timeout=10)
                print(f'   Status: {response.status_code}')
                
                if response.status_code == 200:
                    print('   ✅ Suscripción a "page" creada exitosamente')
                else:
                    print(f'   ❌ Error creando suscripción page: {response.text}')
            except Exception as e:
                print(f'   ❌ Error: {e}')
        
        # 3. Verificar cuentas publicitarias
        print('\n3. 💼 Verificando cuentas publicitarias...')
        
        # Obtener cuentas desde Supabase
        try:
            from clientes.aura.utils.supabase_client import supabase
            
            cuentas_result = supabase.table('meta_ads_cuentas') \
                .select('id_cuenta_publicitaria, nombre_cliente') \
                .eq('estado_actual', 'ACTIVE') \
                .execute()
            
            cuentas = cuentas_result.data if cuentas_result.data else []
            print(f'   Encontradas {len(cuentas)} cuentas activas en Supabase')
            
            if not cuentas:
                print('   ⚠️  No hay cuentas publicitarias activas en Supabase')
                print('   💡 Tip: Ejecuta sincronizador para cargar cuentas')
                return
            
            # Suscribir cada cuenta individualmente
            for cuenta in cuentas[:3]:  # Limitar a 3 para evitar spam
                id_cuenta = cuenta['id_cuenta_publicitaria']
                nombre = cuenta.get('nombre_cliente', 'Sin nombre')
                
                print(f'\n   📊 Procesando cuenta: {nombre} ({id_cuenta})')
                
                # Verificar si ya tiene webhook
                webhook_url_cuenta = f'https://graph.facebook.com/v18.0/act_{id_cuenta}/subscriptions'
                
                try:
                    response = requests.get(webhook_url_cuenta, 
                                          params={'access_token': app_access_token}, 
                                          timeout=10)
                    
                    if response.status_code == 200:
                        subs_cuenta = response.json().get('data', [])
                        
                        if subs_cuenta:
                            print(f'     ✅ Ya tiene {len(subs_cuenta)} suscripciones')
                        else:
                            print('     ℹ️  Sin suscripciones, creando...')
                            
                            # Crear suscripción para la cuenta
                            data_cuenta = {
                                'object': 'adaccount',
                                'callback_url': webhook_url,
                                'fields': ['campaign', 'adset', 'ad'],
                                'verify_token': webhook_verify_token,
                                'access_token': app_access_token
                            }
                            
                            response_sub = requests.post(webhook_url_cuenta, 
                                                       data=data_cuenta, 
                                                       timeout=10)
                            
                            if response_sub.status_code == 200:
                                print('     ✅ Suscripción creada')
                            else:
                                print(f'     ❌ Error: {response_sub.text}')
                    
                    elif response.status_code == 403:
                        print('     ⚠️  Sin permisos para esta cuenta')
                    else:
                        print(f'     ❌ Error {response.status_code}: {response.text}')
                        
                except Exception as e:
                    print(f'     ❌ Error: {e}')
            
        except ImportError:
            print('   ⚠️  No se pudo importar supabase_client')
        except Exception as e:
            print(f'   ❌ Error obteniendo cuentas: {e}')
        
        print('\n' + '=' * 50)
        print('✅ Gestión de webhooks completada')
        print('💡 Tip: Verifica en Meta Developer Console que todo esté configurado')
        
    except Exception as e:
        print(f'❌ Error general: {e}')

if __name__ == "__main__":
    gestionar_webhooks_meta()

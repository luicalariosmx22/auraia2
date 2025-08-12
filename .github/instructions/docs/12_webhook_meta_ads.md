# 📢 Webhook de Meta Ads

El webhook de Meta Ads permite recibir notificaciones en tiempo real sobre cambios en anuncios, campañas, audiencias y páginas de Facebook/Instagram.

## 🏗️ Configuración del webhook

### 1. URL del webhook
```
https://tu-dominio.com/meta/webhook
```

### 2. Variables de entorno necesarias
```bash
# En .env.local y Railway
META_WEBHOOK_VERIFY_TOKEN=nora123
META_WEBHOOK_SECRET=1002ivimyH!
META_ACCESS_TOKEN=EAAPJAAprGjgBPCe4wJe1KWvePSX1Vg6nVx7j9fygNvMpQPZBwLSELLZAdPm1RNbZAZAPohPPangdlMygB02ZBZA3jmUxWxlw4JtgYNMm63ZCjHZBBHSC5kKaOuRp7OyCb2dKDUqTWeRZCZAVURtNNkZCdYqf0J5ZBaHmvjwy0oZCbRELn80E6vJOWz6Wm7DZCM2jx7
META_APP_ID=1065426942106168
META_APP_SECRET=0c7873a69248f693f21fb9de4d1dca6d
```

---

## 🔗 Estructura del webhook real

### Blueprint principal
```python
# clientes/aura/routes/panel_cliente_meta_ads/webhooks_meta.py
from flask import Blueprint, request, jsonify, Response
from datetime import datetime, timedelta
import os
import hashlib
import hmac
from dotenv import load_dotenv
from clientes.aura.utils.meta_webhook_helpers import (
    registrar_evento_supabase, 
    procesar_evento_audiencia, 
    procesar_evento_anuncio,
    verificar_webhook_registrado,
    registrar_webhook_en_cuenta,
    registrar_webhooks_en_cuentas_activas
)
from clientes.aura.utils.supabase_client import supabase

webhooks_meta_bp = Blueprint('webhooks_meta_bp', __name__)

@webhooks_meta_bp.route('/meta/webhook', methods=['GET', 'POST'])
def recibir_webhook():
    """Endpoint unificado para verificación y recepción de webhooks de Meta"""
    
    if request.method == 'GET':
        # Verificación del webhook por parte de Meta
        mode = request.args.get("hub.mode")
        challenge = request.args.get("hub.challenge")
        verify_token = request.args.get("hub.verify_token")

        TOKEN_VERIFICACION = os.getenv('META_WEBHOOK_VERIFY_TOKEN', 'nora123')

        if mode == "subscribe" and verify_token == TOKEN_VERIFICACION:
            print("✅ Verificación de webhook exitosa")
            return Response(challenge, status=200, mimetype='text/plain')
        else:
            print(f"❌ Token inválido. Recibido: {verify_token}, Esperado: {TOKEN_VERIFICACION}")
            return Response("❌ Token inválido", status=403)
    
    elif request.method == 'POST':
        # Procesamiento de eventos del webhook
        return procesar_eventos_webhook()

def procesar_eventos_webhook():
    """Procesa eventos entrantes de Meta con verificación de firma"""
    try:
        # Obtener payload y firma
        payload_body = request.get_data()
        signature_header = request.headers.get('X-Hub-Signature-256')
        
        # Verificación de firma HMAC
        app_secret = os.getenv("META_WEBHOOK_SECRET")
        
        if app_secret and signature_header:
            expected_signature = hmac.new(
                bytes(app_secret, "utf-8"),
                payload_body,
                hashlib.sha256
            ).hexdigest()
            
            firma_recibida = signature_header.replace("sha256=", "")
            
            if not hmac.compare_digest(firma_recibida, expected_signature):
                print("❌ Firma del webhook inválida")
                return jsonify({"status": "error", "message": "Firma inválida"}), 403
            else:
                print("✅ Firma del webhook verificada correctamente")
        
        # Procesar JSON
        payload = request.get_json()
        if not payload:
            return jsonify({"status": "error", "message": "No payload"}), 400
            
        return procesar_entradas_meta(payload)
        
    except Exception as e:
        print(f"❌ Error en webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
```

---

## 📊 Procesamiento de eventos reales

### Función principal de procesamiento
```python
def procesar_entradas_meta(payload):
    """Procesa todas las entradas del webhook Meta"""
    try:
        ahora = datetime.utcnow().isoformat()
        eventos_procesados = 0

        print(f"📥 Webhook recibido: {payload}")

        for entry in payload.get('entry', []):
            entry_id = entry.get('id')  # ID de la página
            
            for cambio in entry.get('changes', []):
                objeto = cambio.get('field')  # account, audience, campaign, feed
                valor = cambio.get('value', {})
                
                # Extraer objeto_id de forma robusta
                objeto_id = extraer_objeto_id(objeto, valor, entry_id)
                
                if not objeto or not objeto_id:
                    print(f"⚠️ Evento incompleto: objeto={objeto}, objeto_id={objeto_id}")
                    continue
                
                # Procesar según tipo de objeto
                eventos_procesados += procesar_evento_por_tipo(objeto, objeto_id, valor, entry_id, ahora)
        
        return jsonify({
            "status": "recibido",
            "eventos_procesados": eventos_procesados
        }), 200
        
    except Exception as e:
        print(f"❌ Error procesando entradas: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

def extraer_objeto_id(objeto, valor, entry_id):
    """Extrae ID del objeto según el tipo"""
    if objeto == "account":
        return valor.get("ad_account_id") or entry_id
    elif objeto == "audience":
        return valor.get("id") or valor.get("audience_id")
    elif objeto == "campaign":
        return valor.get("campaign_id")
    elif objeto == "ad":
        return valor.get("ad_id")
    elif objeto == "feed":
        # Filtrar eventos no deseados de feed
        excluir_items = {'reaction', 'comment', 'share'}
        if valor.get("item") in excluir_items:
            print(f"⏩ Ignorando evento feed tipo '{valor.get('item')}'")
            return None
        return valor.get("post_id") or valor.get("parent_id")
    else:
        return valor.get("id") or entry_id

def procesar_evento_por_tipo(objeto, objeto_id, valor, entry_id, ahora):
    """Procesa evento según su tipo"""
    eventos_procesados = 0
    
    try:
        # Actualizar sincronización de página
        if entry_id:
            actualizar_sincronizacion_pagina(entry_id, ahora)
        
        # Registrar eventos en logs_webhooks_meta
        eventos_procesados += registrar_eventos_supabase(objeto, objeto_id, valor, ahora)
        
        # Procesamiento específico por tipo
        if objeto == 'audience':
            procesar_evento_audiencia(objeto_id)
            print(f"🎯 Evento de audiencia procesado: {objeto_id}")
        
        elif objeto in ['ad', 'adset', 'campaign']:
            procesar_evento_anuncio_webhook(objeto_id, objeto, ahora)
            print(f"📢 Evento de anuncio procesado: {objeto_id}")
        
        elif objeto == 'feed':
            procesar_evento_feed(objeto_id, valor)
            print(f"📄 Evento de publicación procesado: {objeto_id}")
        
        return eventos_procesados
        
    except Exception as e:
        print(f"❌ Error procesando evento {objeto}/{objeto_id}: {e}")
        return eventos_procesados

def procesar_evento_feed(objeto_id, valor):
    """Procesa eventos de publicaciones (feed)"""
    try:
        from clientes.aura.routes.panel_cliente_meta_ads.automatizacion_campanas import procesar_publicacion_webhook
        
        # Procesar automatización de campañas
        payload_completo = {'entry': [{'changes': [{'field': 'feed', 'value': valor}]}]}
        resultado_automatizacion = procesar_publicacion_webhook(payload_completo)
        
        if resultado_automatizacion['ok']:
            print(f"🚀 Automatización procesada: {resultado_automatizacion['anuncios_creados']} anuncios creados")
        else:
            print(f"⚠️ Error en automatización: {resultado_automatizacion.get('error', 'Error desconocido')}")
            
    except Exception as e:
        print(f"⚠️ Error procesando feed {objeto_id}: {e}")

def actualizar_sincronizacion_pagina(entry_id, ahora):
    """Actualiza timestamp de sincronización de página"""
    try:
        supabase.table("facebook_paginas") \
            .update({
                "ultima_sincronizacion": ahora,
                "actualizado_en": ahora
            }) \
            .eq("page_id", entry_id) \
            .execute()
        
        print(f"✅ Página {entry_id} sincronizada en {ahora}")
    except Exception as e:
        print(f"⚠️ Error actualizando sincronización de página {entry_id}: {e}")

def registrar_eventos_supabase(objeto, objeto_id, valor, ahora):
    """Registra eventos en logs_webhooks_meta"""
    eventos_procesados = 0
    
    # Filtrar campos que no van en logs_webhooks_meta
    campos_excluidos = {'nombre_nora', 'created_time', 'updated_time'}
    
    for campo, val in valor.items():
        if campo in campos_excluidos:
            print(f"⚠️ Saltando campo excluido: {campo} = {val}")
            continue
            
        if registrar_evento_supabase(
            objeto=objeto,
            objeto_id=objeto_id,
            campo=campo,
            valor=val,
            hora_evento=ahora
        ):
            eventos_procesados += 1
    
    return eventos_procesados
```

---

## �️ APIs de gestión del webhook

### Endpoints principales disponibles
```python
# Estado de cuentas registradas
@webhooks_meta_bp.route('/api/webhooks/estado_cuentas', methods=['GET'])
def obtener_estado_cuentas():
    """Obtiene el estado de registro de webhooks para todas las cuentas"""
    try:
        access_token = os.getenv('META_ACCESS_TOKEN')
        if not access_token:
            return jsonify({"success": False, "message": "Access token no configurado"}), 500
        
        # Obtener cuentas activas
        response = supabase.table('meta_ads_cuentas') \
            .select('id_cuenta_publicitaria, nombre_cliente, estado_actual') \
            .eq('estado_actual', 'ACTIVE') \
            .execute()
        
        cuentas_con_estado = []
        for cuenta in response.data:
            id_cuenta = cuenta['id_cuenta_publicitaria']
            webhook_registrado = verificar_webhook_registrado(id_cuenta, access_token)
            
            cuentas_con_estado.append({
                'id_cuenta_publicitaria': id_cuenta,
                'nombre_cliente': cuenta['nombre_cliente'],
                'estado_actual': cuenta['estado_actual'],
                'webhook_registrado': webhook_registrado
            })
        
        return jsonify({"success": True, "cuentas": cuentas_con_estado}), 200
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# Registro de webhook individual
@webhooks_meta_bp.route('/api/webhooks/registrar_cuenta', methods=['POST'])
def registrar_webhook_cuenta_individual():
    """Registra webhook para una cuenta específica"""
    try:
        access_token = os.getenv('META_ACCESS_TOKEN')
        data = request.get_json()
        id_cuenta = data.get('id_cuenta')
        
        if not id_cuenta:
            return jsonify({"success": False, "message": "ID de cuenta requerido"}), 400
        
        resultado = registrar_webhook_en_cuenta(id_cuenta, access_token)
        
        if resultado:
            return jsonify({
                "success": True,
                "message": f"Webhook registrado exitosamente para cuenta {id_cuenta}"
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": f"Error registrando webhook para cuenta {id_cuenta}"
            }), 500
            
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# Estadísticas de eventos
@webhooks_meta_bp.route('/api/webhooks/estadisticas', methods=['GET'])
def obtener_estadisticas_webhooks():
    """Obtiene estadísticas de eventos de webhook"""
    try:
        # Estadísticas de logs_webhooks_meta
        response_logs = supabase.table('logs_webhooks_meta').select('procesado').execute()
        eventos_logs = response_logs.data if response_logs.data else []
        
        total_logs = len(eventos_logs)
        procesados_logs = len([e for e in eventos_logs if e.get('procesado', False)])
        
        # Estadísticas de meta_publicaciones_webhook
        response_pub = supabase.table('meta_publicaciones_webhook').select('procesada').execute()
        eventos_pub = response_pub.data if response_pub.data else []
        
        total_pub = len(eventos_pub)
        procesados_pub = len([e for e in eventos_pub if e.get('procesada', False)])
        
        # Totales combinados
        total_eventos = total_logs + total_pub
        procesados = procesados_logs + procesados_pub
        no_procesados = total_eventos - procesados
        
        # Eventos recientes (últimos 7 días)
        hace_7_dias = (datetime.utcnow() - timedelta(days=7)).isoformat()
        
        response_recientes_logs = supabase.table('logs_webhooks_meta') \
            .select('id').gte('timestamp', hace_7_dias).execute()
        recientes_logs = len(response_recientes_logs.data) if response_recientes_logs.data else 0
        
        response_recientes_pub = supabase.table('meta_publicaciones_webhook') \
            .select('id').gte('creada_en', hace_7_dias).execute()
        recientes_pub = len(response_recientes_pub.data) if response_recientes_pub.data else 0
        
        eventos_recientes = recientes_logs + recientes_pub
        
        return jsonify({
            "success": True,
            "estadisticas": {
                "total_eventos": total_eventos,
                "procesados": procesados,
                "no_procesados": no_procesados,
                "eventos_recientes": eventos_recientes,
                "detalle": {
                    "logs_webhooks": {
                        "total": total_logs,
                        "procesados": procesados_logs,
                        "recientes": recientes_logs
                    },
                    "publicaciones": {
                        "total": total_pub,
                        "procesados": procesados_pub,
                        "recientes": recientes_pub
                    }
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# Gestión de tokens de páginas
@webhooks_meta_bp.route('/api/webhooks/tokens_paginas', methods=['GET'])
def obtener_estado_tokens_paginas():
    """Obtiene el estado de tokens de todas las páginas"""
    try:
        response = supabase.table("facebook_paginas") \
            .select("page_id, nombre_pagina, access_token_valido, ultima_sincronizacion, activa") \
            .order("nombre_pagina") \
            .execute()
        
        paginas_con_estado = []
        for pagina in response.data or []:
            tiene_token = bool(obtener_token_pagina(pagina['page_id']))
            
            paginas_con_estado.append({
                'page_id': pagina['page_id'],
                'nombre_pagina': pagina['nombre_pagina'],
                'activa': pagina['activa'],
                'tiene_token': tiene_token,
                'token_valido': pagina.get('access_token_valido', True),
                'ultima_sincronizacion': pagina.get('ultima_sincronizacion')
            })
        
        # Estadísticas
        total_paginas = len(paginas_con_estado)
        activas = len([p for p in paginas_con_estado if p['activa']])
        con_token = len([p for p in paginas_con_estado if p['tiene_token']])
        tokens_validos = len([p for p in paginas_con_estado if p['tiene_token'] and p['token_valido']])
        
        return jsonify({
            "success": True,
            "paginas": paginas_con_estado,
            "estadisticas": {
                "total_paginas": total_paginas,
                "activas": activas,
                "con_token": con_token,
                "tokens_validos": tokens_validos,
                "sin_token": activas - con_token
            }
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# Validación de token específico
@webhooks_meta_bp.route('/api/webhooks/validar_token_pagina/<page_id>', methods=['POST'])
def validar_token_pagina_api(page_id):
    """Valida el token de una página específica"""
    try:
        import requests
        
        token = obtener_token_pagina(page_id)
        if not token:
            return jsonify({
                "success": False,
                "message": "No hay token guardado para esta página"
            }), 400
        
        # Validar token con Facebook API
        url = f"https://graph.facebook.com/v18.0/{page_id}"
        params = {'access_token': token, 'fields': 'id,name,access_token'}
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Actualizar estado como válido
            supabase.table("facebook_paginas") \
                .update({
                    "access_token_valido": True,
                    "actualizado_en": datetime.now().isoformat(),
                    "ultima_sincronizacion": datetime.now().isoformat()
                }) \
                .eq("page_id", page_id) \
                .execute()
            
            return jsonify({
                "success": True,
                "message": "Token válido",
                "page_name": data.get('name'),
                "validado_en": datetime.now().isoformat()
            }), 200
        else:
            # Token inválido - marcar como inválido
            supabase.table("facebook_paginas") \
                .update({
                    "access_token_valido": False,
                    "actualizado_en": datetime.now().isoformat()
                }) \
                .eq("page_id", page_id) \
                .execute()
            
            return jsonify({
                "success": False,
                "message": f"Token inválido: {response.status_code}",
                "facebook_error": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            }), 400
            
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
```

---

## � Sistema de gestión de tokens

### Funciones de tokens de página
```python
def obtener_token_pagina(page_id):
    """
    Obtiene el token de acceso específico de una página desde la base de datos.
    """
    try:
        print(f"🔍 DEBUG: Obteniendo token para página {page_id}")
        
        response = supabase.table("facebook_paginas") \
            .select("access_token, nombre_pagina, access_token_valido") \
            .eq("page_id", page_id) \
            .eq("activa", True) \
            .single() \
            .execute()
        
        if response.data:
            token_valido = response.data.get('access_token_valido', True)
            if not token_valido:
                print(f"⚠️ WARNING: Token marcado como inválido para página {page_id}")
                return None
            
            token = response.data.get('access_token')
            nombre_pagina = response.data.get('nombre_pagina', 'Desconocida')
            
            if token:
                print(f"✅ Token encontrado para página '{nombre_pagina}' ({page_id})")
                return token
            else:
                print(f"❌ No hay token guardado para página '{nombre_pagina}' ({page_id})")
                return None
        else:
            print(f"❌ Página {page_id} no encontrada en base de datos")
            return None
            
    except Exception as e:
        print(f"❌ ERROR obteniendo token para página {page_id}: {str(e)}")
        return None

def obtener_token_principal():
    """
    Obtiene el token principal de Meta desde las variables de entorno.
    """
    token = os.getenv('META_ACCESS_TOKEN')
    if token:
        print("✅ Token principal META obtenido")
        return token
    else:
        print("❌ ERROR: META_ACCESS_TOKEN no encontrado en variables de entorno")
        return None

def obtener_token_apropiado(page_id):
    """
    Obtiene el token más apropiado: token específico de página o token principal como fallback.
    """
    # Primero intentar token específico de página
    token_pagina = obtener_token_pagina(page_id)
    if token_pagina:
        print(f"🎯 Usando token específico para página {page_id}")
        return token_pagina
    
    # Fallback al token principal
    token_principal = obtener_token_principal()
    if token_principal:
        print(f"🔄 Usando token principal como fallback para página {page_id}")
        return token_principal
    
    print(f"❌ No se pudo obtener ningún token para página {page_id}")
    return None

def actualizar_estado_token_pagina(page_id, es_valido=True):
    """Actualiza el estado de validez del token de una página"""
    try:
        supabase.table("facebook_paginas") \
            .update({
                "access_token_valido": es_valido,
                "actualizado_en": "now()"
            }) \
            .eq("page_id", page_id) \
            .execute()
        
        print(f"✅ Estado de token actualizado para página {page_id}: {'válido' if es_valido else 'inválido'}")
    except Exception as e:
        print(f"❌ ERROR actualizando estado de token para página {page_id}: {str(e)}")

def validar_todos_los_tokens():
    """Valida todos los tokens de páginas almacenados"""
    try:
        # Obtener todas las páginas activas
        response = supabase.table("facebook_paginas") \
            .select("page_id, nombre_pagina, access_token") \
            .eq("activa", True) \
            .execute()
        
        tokens_validos = 0
        tokens_invalidos = 0
        
        for pagina in response.data or []:
            page_id = pagina['page_id']
            token = pagina.get('access_token')
            
            if not token:
                print(f"⚠️ Página {page_id} sin token")
                continue
            
            # Validar token con Meta API
            es_valido = validar_token_con_meta_api(page_id, token)
            
            # Actualizar estado en BD
            actualizar_estado_token_pagina(page_id, es_valido)
            
            if es_valido:
                tokens_validos += 1
            else:
                tokens_invalidos += 1
        
        print(f"📊 Validación completa: {tokens_validos} válidos, {tokens_invalidos} inválidos")
        
        return {
            'tokens_validos': tokens_validos,
            'tokens_invalidos': tokens_invalidos,
            'total_verificados': tokens_validos + tokens_invalidos
        }
        
    except Exception as e:
        print(f"❌ Error validando tokens: {e}")
        return None

def validar_token_con_meta_api(page_id, token):
    """Valida un token específico contra la API de Meta"""
    try:
        import requests
        
        url = f"https://graph.facebook.com/v18.0/{page_id}"
        params = {
            'access_token': token,
            'fields': 'id,name'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Token válido para página: {data.get('name', page_id)}")
            return True
        else:
            print(f"❌ Token inválido para página {page_id}: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error validando token: {e}")
        return False
```

---

## �️ Base de datos y esquemas

### Tablas principales del webhook
```sql
-- logs_webhooks_meta: Almacena todos los eventos del webhook
CREATE TABLE logs_webhooks_meta (
    id BIGSERIAL PRIMARY KEY,
    tipo_evento VARCHAR(50) NOT NULL,        -- account, audience, campaign, ad, feed
    objeto_id VARCHAR(100) NOT NULL,         -- ID del objeto (ad_id, campaign_id, etc.)
    campo VARCHAR(100),                      -- Campo que cambió
    valor_anterior TEXT,                     -- Valor anterior (si aplica)
    valor_nuevo TEXT,                        -- Valor nuevo
    timestamp TIMESTAMPTZ DEFAULT NOW(),     -- Momento del evento
    page_id VARCHAR(50),                     -- ID de página asociada
    procesado BOOLEAN DEFAULT FALSE,         -- Si fue procesado
    error_mensaje TEXT,                      -- Error si hubo problemas
    datos JSON                               -- Datos completos del evento
);

-- facebook_paginas: Información de páginas conectadas
CREATE TABLE facebook_paginas (
    id BIGSERIAL PRIMARY KEY,
    nombre_nora VARCHAR(50) NOT NULL,
    page_id VARCHAR(50) UNIQUE NOT NULL,
    nombre_pagina VARCHAR(200),
    access_token TEXT,                       -- Token específico de la página
    access_token_valido BOOLEAN DEFAULT TRUE,
    activa BOOLEAN DEFAULT TRUE,
    ultima_sincronizacion TIMESTAMPTZ,
    creada_en TIMESTAMPTZ DEFAULT NOW(),
    actualizada_en TIMESTAMPTZ DEFAULT NOW()
);

-- meta_ads_cuentas: Cuentas publicitarias conectadas
CREATE TABLE meta_ads_cuentas (
    id BIGSERIAL PRIMARY KEY,
    nombre_nora VARCHAR(50) NOT NULL,
    id_cuenta_publicitaria VARCHAR(50) NOT NULL,
    nombre_cliente VARCHAR(200),
    estado_actual VARCHAR(50) DEFAULT 'ACTIVE',
    conectada BOOLEAN DEFAULT TRUE,
    webhook_registrado BOOLEAN DEFAULT FALSE,
    ultima_sincronizacion TIMESTAMPTZ,
    creada_en TIMESTAMPTZ DEFAULT NOW(),
    actualizada_en TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para optimizar consultas
CREATE INDEX idx_logs_webhooks_tipo ON logs_webhooks_meta(tipo_evento);
CREATE INDEX idx_logs_webhooks_timestamp ON logs_webhooks_meta(timestamp DESC);
CREATE INDEX idx_logs_webhooks_procesado ON logs_webhooks_meta(procesado);
CREATE INDEX idx_facebook_paginas_nora ON facebook_paginas(nombre_nora);
CREATE INDEX idx_facebook_paginas_activa ON facebook_paginas(activa);
CREATE INDEX idx_meta_ads_cuentas_nora ON meta_ads_cuentas(nombre_nora);
CREATE INDEX idx_meta_ads_cuentas_estado ON meta_ads_cuentas(estado_actual);
```

### Funciones de base de datos
```python
def registrar_evento_supabase(objeto, objeto_id, campo, valor, hora_evento):
    """Registra evento en logs_webhooks_meta"""
    try:
        supabase.table("logs_webhooks_meta").insert({
            "tipo_evento": objeto,
            "objeto_id": str(objeto_id),
            "campo": campo,
            "valor_nuevo": str(valor) if valor is not None else None,
            "timestamp": hora_evento,
            "procesado": True
        }).execute()
        
        return True
    except Exception as e:
        print(f"❌ Error registrando evento {objeto}/{objeto_id}: {str(e)}")
        return False

def obtener_nora_por_page_id(page_id):
    """Obtiene nombre_nora asociado a page_id"""
    try:
        result = supabase.table('facebook_paginas') \
            .select('nombre_nora') \
            .eq('page_id', page_id) \
            .eq('activa', True) \
            .single() \
            .execute()
        
        return result.data['nombre_nora'] if result.data else None
        
    except Exception as e:
        print(f"Error obteniendo nora por page_id: {e}")
        return None

def actualizar_sincronizacion_pagina(page_id, timestamp):
    """Actualiza timestamp de última sincronización"""
    try:
        supabase.table("facebook_paginas") \
            .update({
                "ultima_sincronizacion": timestamp,
                "actualizada_en": timestamp
            }) \
            .eq("page_id", page_id) \
            .execute()
        
        print(f"✅ Sincronización actualizada para página {page_id}")
        
    except Exception as e:
        print(f"❌ Error actualizando sincronización: {e}")

def verificar_webhook_registrado(id_cuenta, access_token):
    """Verifica si webhook está registrado para una cuenta"""
    try:
        import requests
        
        url = f"https://graph.facebook.com/v18.0/act_{id_cuenta}/subscriptions"
        params = {'access_token': access_token}
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            webhooks = data.get('data', [])
            
            # Buscar webhook activo
            for webhook in webhooks:
                if webhook.get('status') == 'active':
                    return True
            
            return False
        else:
            print(f"❌ Error verificando webhook para cuenta {id_cuenta}: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando webhook: {e}")
        return False

def registrar_webhook_en_cuenta(id_cuenta, access_token):
    """Registra webhook en una cuenta publicitaria"""
    try:
        import requests
        
        webhook_url = f"{os.getenv('BASE_URL', 'https://app.soynoraai.com')}/meta/webhook"
        
        url = f"https://graph.facebook.com/v18.0/act_{id_cuenta}/subscriptions"
        
        data = {
            'object': 'adaccount',
            'callback_url': webhook_url,
            'fields': ['campaign', 'adset', 'ad', 'creative'],
            'verify_token': os.getenv('META_WEBHOOK_VERIFY_TOKEN', 'nora123'),
            'access_token': access_token
        }
        
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            # Actualizar estado en BD
            supabase.table('meta_ads_cuentas') \
                .update({'webhook_registrado': True}) \
                .eq('id_cuenta_publicitaria', id_cuenta) \
                .execute()
            
            print(f"✅ Webhook registrado para cuenta {id_cuenta}")
            return True
        else:
            print(f"❌ Error registrando webhook: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error registrando webhook: {e}")
        return False

def obtener_estadisticas_eventos(dias=7):
    """Obtiene estadísticas de eventos de webhook"""
    try:
        from datetime import datetime, timedelta
        
        fecha_inicio = (datetime.now() - timedelta(days=dias)).isoformat()
        
        # Total de eventos por tipo
        eventos_por_tipo = supabase.table('logs_webhooks_meta') \
            .select('tipo_evento') \
            .gte('timestamp', fecha_inicio) \
            .execute()
        
        # Agrupar por tipo
        conteo_tipos = {}
        for evento in eventos_por_tipo.data or []:
            tipo = evento['tipo_evento']
            conteo_tipos[tipo] = conteo_tipos.get(tipo, 0) + 1
        
        # Eventos procesados vs no procesados
        eventos_estado = supabase.table('logs_webhooks_meta') \
            .select('procesado') \
            .gte('timestamp', fecha_inicio) \
            .execute()
        
        total_eventos = len(eventos_estado.data or [])
        procesados = len([e for e in eventos_estado.data or [] if e.get('procesado')])
        no_procesados = total_eventos - procesados
        
        return {
            'periodo_dias': dias,
            'total_eventos': total_eventos,
            'procesados': procesados,
            'no_procesados': no_procesados,
            'eventos_por_tipo': conteo_tipos,
            'fecha_inicio': fecha_inicio
        }
        
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")
        return {}
```

---

## � Configuración y variables de entorno

### Variables requeridas
```bash
# Meta Ads API
META_ACCESS_TOKEN=EAAPJAAprGjgBPCe4wJe1KWvePSX1Vg6nVx7j9fygNvMpQPZBwLSELLZAdPm1RNbZAZAPohPPangdlMygB02ZBZA3jmUxWxlw4JtgYNMm63ZCjHZBBHSC5kKaOuRp7OyCb2dKDUqTWeRZCZAVURtNNkZCdYqf0J5ZBaHmvjwy0oZCbRELn80E6vJOWz6Wm7DZCM2jx7
META_APP_ID=1065426942106168
META_APP_SECRET=0c7873a69248f693f21fb9de4d1dca6d

# Webhook configuration
META_WEBHOOK_SECRET=1002ivimyH!
META_WEBHOOK_VERIFY_TOKEN=nora123
META_WEBHOOK_URL=https://app.soynoraai.com/meta/webhook

# Base URL para webhook registration
BASE_URL=https://app.soynoraai.com

# Supabase configuration
SUPABASE_URL=https://sylqljdiiyhtgtrghwjk.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN5bHFsamRpaXlodGd0cmdod2prIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NDcwMzUzMiwiZXhwIjoyMDYwMjc5NTMyfQ.Y-LTUYS0qg8bKEX1c6MLdxudNUsJuZdQfV2Z0dx9n1Q
```

### URL del webhook
```
https://app.soynoraai.com/meta/webhook
```

### Configuración en Facebook Developer
1. **App ID**: 1065426942106168
2. **Webhook URL**: https://app.soynoraai.com/meta/webhook
3. **Verify Token**: nora123
4. **Subscribed Fields**: 
   - `page` - Para eventos de páginas
   - `adaccount` - Para eventos de cuentas publicitarias
   - `campaign` - Para cambios en campañas
   - `adset` - Para cambios en conjuntos de anuncios
   - `ad` - Para cambios en anuncios individuales

### Verificación HMAC de seguridad
```python
def verificar_firma_webhook(payload, signature, secret):
    """Verifica firma HMAC SHA-256 del webhook"""
    import hmac
    import hashlib
    
    if not signature:
        return False
    
    # Remover prefijo si existe
    if '=' in signature:
        signature = signature.split('=', 1)[1]
    
    # Calcular firma esperada
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)
```

---

## 📋 Registro en app principal

### En registro_dinamico.py
```python
# Registrar blueprint del webhook Meta
if "meta_ads" in modulos:
    try:
        # Blueprint principal de Meta Ads
        from clientes.aura.routes.panel_cliente_meta_ads import panel_cliente_meta_ads_bp
        safe_register_blueprint(app, panel_cliente_meta_ads_bp)
        
        # Blueprint de webhooks Meta
        from clientes.aura.routes.panel_cliente_meta_ads.webhooks_meta import webhooks_meta_bp
        safe_register_blueprint(app, webhooks_meta_bp)
        
        print(f"✅ Módulo Meta Ads y webhooks registrados")
        
    except Exception as e:
        print(f"❌ Error registrando Meta Ads: {e}")
```

### En __init__.py del módulo
```python
# clientes/aura/routes/panel_cliente_meta_ads/__init__.py
from .panel_cliente_meta_ads import panel_cliente_meta_ads_bp
from .webhooks_meta import webhooks_meta_bp
from .automatizacion_routes import automatizacion_routes_bp
from .webhooks_api import webhooks_api_bp

__all__ = [
    'panel_cliente_meta_ads_bp',
    'webhooks_meta_bp', 
    'automatizacion_routes_bp',
    'webhooks_api_bp'
]
```

---

## ✅ Verificación de funcionamiento

### 1. Test de verificación (GET)
```bash
curl "https://app.soynoraai.com/meta/webhook?hub.mode=subscribe&hub.verify_token=nora123&hub.challenge=test123"
# Debe retornar: test123
```

### 2. Verificar configuración en Facebook Developer
- Ir a https://developers.facebook.com/apps/1065426942106168/
- Productos → Webhooks
- Verificar URL y token configurados

### 3. Monitorear logs de eventos
```python
# Ver eventos recientes
logs = supabase.table('logs_webhooks_meta') \
    .select('*') \
    .order('timestamp', desc=True) \
    .limit(10) \
    .execute()

for log in logs.data:
    print(f"{log['timestamp']}: {log['tipo_evento']} - {log['objeto_id']}")
```

### 4. Verificar páginas conectadas
```python
# Ver páginas configuradas
paginas = supabase.table('facebook_paginas') \
    .select('nombre_nora, page_id, nombre_pagina, activa') \
    .eq('activa', True) \
    .execute()

for pagina in paginas.data:
    print(f"{pagina['nombre_nora']}: {pagina['nombre_pagina']} ({pagina['page_id']})")
```

### 5. Test de evento sintético
```python
# Enviar evento de prueba para verificar procesamiento
evento_test = {
    "object": "page",
    "entry": [
        {
            "id": "test_page_id",
            "time": int(time.time()),
            "changes": [
                {
                    "field": "feed",
                    "value": {
                        "post_id": "test_page_id_123",
                        "message": "Test post from webhook",
                        "created_time": datetime.now().isoformat()
                    }
                }
            ]
        }
    ]
}

# Enviar POST al webhook con firma HMAC
```

---

## 🚨 Troubleshooting

### Errores comunes

1. **Webhook no verifica (GET request fails)**
   - Verificar `META_WEBHOOK_VERIFY_TOKEN` en variables de entorno
   - Confirmar que coincide con Facebook Developer Console

2. **Eventos no llegan (POST request issues)**
   - Verificar `META_WEBHOOK_SECRET` para validación HMAC
   - Confirmar suscripciones activas en Facebook Developer
   - Revisar logs en `logs_webhooks_meta` tabla

3. **Token inválido para páginas**
   - Ejecutar `/api/webhooks/validar_token_pagina/<page_id>`
   - Renovar tokens desde Facebook Developer
   - Verificar permisos de la aplicación

4. **Eventos no se procesan**
   - Verificar tabla `facebook_paginas` tiene registros activos
   - Confirmar `nombre_nora` está correctamente asociado
   - Revisar logs de errores en `error_mensaje` campo

### Logs de debugging
```python
# Habilitar logging detallado
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# En las funciones del webhook
logger.debug(f"Procesando evento: {tipo_evento} para objeto: {objeto_id}")
logger.info(f"Token obtenido para página {page_id}: {'✅' if token else '❌'}")
logger.error(f"Error procesando evento: {str(e)}")
```

### Health check endpoint
```python
@webhooks_meta_bp.route('/meta/webhook/health')
def webhook_health():
    """Health check para el webhook Meta"""
    try:
        # Verificar últimos eventos
        eventos_recientes = supabase.table('logs_webhooks_meta') \
            .select('id') \
            .gte('timestamp', (datetime.now() - timedelta(hours=24)).isoformat()) \
            .execute()
        
        return jsonify({
            'status': 'healthy',
            'webhook_url': '/meta/webhook',
            'eventos_24h': len(eventos_recientes.data or []),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500
```

### Comandos de verificación
```bash
# Verificar que webhook responde
curl -I https://app.soynoraai.com/meta/webhook

# Verificar health check
curl https://app.soynoraai.com/meta/webhook/health

# Verificar logs del servidor
tail -f logs/nora.log | grep webhook
```

---

## 🔍 Verificación y Testing del Webhook

### 1. **Verificar configuración básica**

#### Variables de entorno
```bash
# Verificar que están configuradas
echo $META_WEBHOOK_VERIFY_TOKEN
echo $META_WEBHOOK_SECRET
echo $META_ACCESS_TOKEN
echo $META_APP_ID
```

#### En Railway (si aplica)
- Panel de Railway > Variables
- Confirmar que están todas las variables META_*

---

### 2. **Probar verificación del webhook**

#### Test manual con curl
```bash
# Reemplazar con tu dominio y token
curl -X GET "https://tu-dominio.com/meta/webhook?hub.mode=subscribe&hub.verify_token=TU_TOKEN_VERIFICACION&hub.challenge=test123"

# Debe retornar: test123
```

#### Test desde Facebook Developer Console
1. Ir a https://developers.facebook.com/apps/
2. Tu app > Productos > Webhooks
3. Configurar nuevo webhook:
   - URL: `https://tu-dominio.com/meta/webhook`
   - Token de verificación: tu `META_WEBHOOK_VERIFY_TOKEN`
4. Hacer clic en "Verificar y guardar"

---

### 3. **Scripts de diagnóstico completos**

#### Script de diagnóstico principal
```python
# diagnostico_webhook_meta.py
from clientes.aura.utils.supabase_client import supabase
from datetime import datetime, timedelta

def verificar_webhook_meta():
    """Verifica funcionamiento del webhook Meta"""
    print("🔍 DIAGNÓSTICO WEBHOOK META")
    print("=" * 50)
    
    # 1. Verificar logs recientes
    print("\n1. 📋 Logs recientes (últimas 24h):")
    verificar_logs_recientes()
    
    # 2. Verificar publicaciones recibidas
    print("\n2. 📊 Publicaciones recibidas:")
    verificar_publicaciones_recientes()
    
    # 3. Verificar configuración de páginas
    print("\n3. 📄 Páginas configuradas:")
    verificar_paginas_configuradas()
    
    # 4. Test de conectividad API
    print("\n4. 🌐 Test conectividad Meta API:")
    test_conectividad_api()
    
    print("\n" + "=" * 50)
    print("✅ Diagnóstico completado")

def verificar_logs_recientes():
    """Verifica logs del webhook en las últimas 24h"""
    try:
        ayer = datetime.now() - timedelta(days=1)
        
        logs = supabase.table('logs_webhooks_meta') \
            .select('tipo_evento, timestamp, error_mensaje') \
            .gte('timestamp', ayer.isoformat()) \
            .order('timestamp', desc=True) \
            .limit(10) \
            .execute()
        
        if logs.data:
            print(f"   📈 {len(logs.data)} eventos en últimas 24h")
            for log in logs.data[:5]:
                timestamp = log['timestamp'][:19]  # Solo fecha y hora
                tipo = log['tipo_evento']
                error = log.get('error_mensaje', 'Sin errores')
                print(f"   • {timestamp} - {tipo} - {error}")
        else:
            print("   ⚠️  No hay logs recientes")
            print("   💡 Posibles causas:")
            print("      - Webhook no está recibiendo eventos")
            print("      - URL del webhook incorrecta")
            print("      - Problemas de autenticación")
            
    except Exception as e:
        print(f"   ❌ Error verificando logs: {e}")

def verificar_publicaciones_recientes():
    """Verifica publicaciones recibidas recientemente"""
    try:
        ayer = datetime.now() - timedelta(days=7)  # Últimos 7 días
        
        publicaciones = supabase.table('meta_publicaciones_webhook') \
            .select('nombre_nora, post_id, created_time, procesado') \
            .gte('recibido_en', ayer.isoformat()) \
            .order('recibido_en', desc=True) \
            .limit(10) \
            .execute()
        
        if publicaciones.data:
            print(f"   📊 {len(publicaciones.data)} publicaciones recibidas (7 días)")
            
            # Agrupar por nora
            por_nora = {}
            for pub in publicaciones.data:
                nora = pub['nombre_nora']
                if nora not in por_nora:
                    por_nora[nora] = {'total': 0, 'procesadas': 0}
                por_nora[nora]['total'] += 1
                if pub['procesado']:
                    por_nora[nora]['procesadas'] += 1
            
            for nora, stats in por_nora.items():
                print(f"   • {nora}: {stats['total']} total, {stats['procesadas']} procesadas")
        else:
            print("   ⚠️  No hay publicaciones recientes")
            print("   💡 Posibles causas:")
            print("      - No hay actividad en páginas de Facebook")
            print("      - Webhook no suscrito a eventos de 'page'")
            print("      - Páginas no vinculadas correctamente")
            
    except Exception as e:
        print(f"   ❌ Error verificando publicaciones: {e}")

def verificar_paginas_configuradas():
    """Verifica páginas de Facebook configuradas"""
    try:
        paginas = supabase.table('facebook_paginas') \
            .select('nombre_nora, page_id, nombre_pagina, activa') \
            .execute()
        
        if paginas.data:
            print(f"   📄 {len(paginas.data)} páginas configuradas")
            for pagina in paginas.data:
                estado = "✅ Activa" if pagina['activa'] else "❌ Inactiva"
                print(f"   • {pagina['nombre_nora']}: {pagina['nombre_pagina']} ({pagina['page_id']}) - {estado}")
        else:
            print("   ⚠️  No hay páginas configuradas")
            print("   💡 Ejecutar: crear_tabla_facebook_paginas.py")
            
    except Exception as e:
        print(f"   ❌ Error verificando páginas: {e}")

def test_conectividad_api():
    """Prueba conectividad con Meta API"""
    try:
        import requests
        import os
        
        access_token = os.getenv('META_ACCESS_TOKEN')
        if not access_token:
            print("   ❌ META_ACCESS_TOKEN no configurado")
            return
        
        # Test básico de API
        url = "https://graph.facebook.com/v18.0/me"
        params = {'access_token': access_token}
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API conectada - App: {data.get('name', 'N/A')}")
        else:
            print(f"   ❌ Error API: {response.status_code}")
            print(f"   📋 Respuesta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error probando API: {e}")

if __name__ == "__main__":
    verificar_webhook_meta()
```

---

### 4. **Monitoreo en tiempo real**

#### Script para monitorear logs
```python
# monitor_webhook.py
import time
from datetime import datetime
from clientes.aura.utils.supabase_client import supabase

def monitorear_webhook(duracion_minutos=10):
    """Monitorea webhook en tiempo real"""
    print(f"🔍 Monitoreando webhook por {duracion_minutos} minutos...")
    print("Presiona Ctrl+C para parar\n")
    
    ultimo_timestamp = datetime.now().isoformat()
    
    try:
        for _ in range(duracion_minutos * 6):  # Cada 10 segundos
            # Buscar eventos nuevos
            nuevos_logs = supabase.table('logs_webhooks_meta') \
                .select('tipo_evento, timestamp, datos') \
                .gt('timestamp', ultimo_timestamp) \
                .order('timestamp', desc=True) \
                .execute()
            
            if nuevos_logs.data:
                for log in reversed(nuevos_logs.data):  # Mostrar en orden cronológico
                    timestamp = log['timestamp'][:19]
                    tipo = log['tipo_evento']
                    print(f"📨 {timestamp} - {tipo}")
                    
                    # Actualizar último timestamp
                    if log['timestamp'] > ultimo_timestamp:
                        ultimo_timestamp = log['timestamp']
            
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n⏹️  Monitoreo detenido")

if __name__ == "__main__":
    monitorear_webhook()
```

---

### 5. **Test de eventos sintéticos**

#### Simulador de webhook
```python
# test_webhook_sintetico.py
import requests
import json
import hmac
import hashlib
import os

def test_webhook_sintetico():
    """Envía evento sintético al webhook para testing"""
    
    webhook_url = "https://tu-dominio.com/meta/webhook"  # Cambiar por tu URL
    secret = os.getenv('META_WEBHOOK_SECRET')
    
    # Evento sintético de publicación
    evento_test = {
        "object": "page",
        "entry": [
            {
                "id": "123456789",
                "time": 1640995200,
                "changes": [
                    {
                        "field": "feed",
                        "value": {
                            "page_id": "123456789",
                            "post_id": "123456789_987654321",
                            "created_time": "2024-01-01T12:00:00Z",
                            "message": "Publicación de prueba del webhook",
                            "type": "status"
                        }
                    }
                ]
            }
        ]
    }
    
    # Convertir a JSON
    payload = json.dumps(evento_test)
    
    # Generar firma
    signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # Headers
    headers = {
        'Content-Type': 'application/json',
        'X-Hub-Signature-256': f'sha256={signature}'
    }
    
    # Enviar
    try:
        response = requests.post(webhook_url, data=payload, headers=headers, timeout=10)
        
        print(f"🧪 Test sintético enviado")
        print(f"📊 Status: {response.status_code}")
        print(f"📋 Respuesta: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook procesó evento correctamente")
        else:
            print("❌ Error en el webhook")
            
    except Exception as e:
        print(f"❌ Error enviando test: {e}")

if __name__ == "__main__":
    test_webhook_sintetico()
```

---

### 6. **Verificar suscripciones en Facebook**

#### En Facebook Developer Console
1. Ir a tu app en https://developers.facebook.com/apps/
2. Productos > Webhooks
3. Verificar que esté suscrito a:
   - **page**: Para eventos de páginas
   - **leadgen**: Para leads (si aplica)
   - **ads_insights**: Para métricas de anuncios (si aplica)

#### Script para verificar suscripciones
```python
def verificar_suscripciones_facebook():
    """Verifica suscripciones del webhook en Facebook"""
    import requests
    import os
    
    access_token = os.getenv('META_ACCESS_TOKEN')
    app_id = os.getenv('META_APP_ID')
    
    if not access_token or not app_id:
        print("❌ META_ACCESS_TOKEN o META_APP_ID no configurados")
        return
    
    url = f"https://graph.facebook.com/v18.0/{app_id}/subscriptions"
    params = {'access_token': access_token}
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            suscripciones = data.get('data', [])
            
            print(f"📋 Suscripciones actuales ({len(suscripciones)}):")
            
            for sus in suscripciones:
                objeto = sus.get('object')
                callback_url = sus.get('callback_url')
                fields = sus.get('fields', [])
                active = sus.get('active', False)
                
                estado = "✅ Activa" if active else "❌ Inactiva"
                print(f"• {objeto}: {callback_url} - {estado}")
                print(f"  Campos: {', '.join(fields)}")
        else:
            print(f"❌ Error obteniendo suscripciones: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")
```

---

### 7. **Troubleshooting avanzado**

#### Error: Webhook no verifica
```bash
# 1. Verificar token
echo $META_WEBHOOK_VERIFY_TOKEN

# 2. Test manual
curl "https://tu-dominio.com/meta/webhook?hub.mode=subscribe&hub.verify_token=TU_TOKEN&hub.challenge=test"

# 3. Verificar logs del servidor
tail -f error.log
```

#### Error: Eventos no llegan
```python
# Verificar suscripciones
verificar_suscripciones_facebook()

# Verificar páginas activas
verificar_paginas_configuradas()

# Crear actividad en Facebook y monitorear
monitorear_webhook(5)  # 5 minutos
```

#### Error: Firma inválida
```bash
# Verificar secret
echo $META_WEBHOOK_SECRET

# Verificar que se use el mismo secret en Facebook Developer
```

---

### 8. **Dashboard de salud del webhook**

#### Endpoint de status completo
```python
@webhooks_meta_bp.route('/meta/webhook/status')
def webhook_meta_status():
    """Status completo del webhook Meta"""
    try:
        # Verificar logs recientes
        ayer = datetime.now() - timedelta(days=1)
        logs_count = supabase.table('logs_webhooks_meta') \
            .select('id', count='exact') \
            .gte('timestamp', ayer.isoformat()) \
            .execute()
        
        # Verificar publicaciones recientes
        pub_count = supabase.table('meta_publicaciones_webhook') \
            .select('id', count='exact') \
            .gte('recibido_en', ayer.isoformat()) \
            .execute()
        
        # Verificar errores
        errores_count = supabase.table('logs_webhooks_meta') \
            .select('id', count='exact') \
            .gte('timestamp', ayer.isoformat()) \
            .eq('tipo_evento', 'error') \
            .execute()
        
        # Verificar páginas activas
        paginas_activas = supabase.table('facebook_paginas') \
            .select('id', count='exact') \
            .eq('activa', True) \
            .execute()
        
        # Verificar tokens válidos
        tokens_validos = supabase.table('facebook_paginas') \
            .select('id', count='exact') \
            .eq('activa', True) \
            .eq('access_token_valido', True) \
            .execute()
        
        status = {
            'webhook_activo': True,
            'eventos_24h': logs_count.count,
            'publicaciones_24h': pub_count.count,
            'errores_24h': errores_count.count,
            'paginas_activas': paginas_activas.count,
            'tokens_validos': tokens_validos.count,
            'ultima_verificacion': datetime.now().isoformat(),
            'status_general': 'healthy' if errores_count.count == 0 else 'warning'
        }
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({
            'webhook_activo': False,
            'error': str(e),
            'status_general': 'unhealthy'
        }), 500
```

#### Acceder al status
```bash
curl https://tu-dominio.com/meta/webhook/status
```

---

## 🎯 Checklist completo de verificación

### Configuración básica
- [ ] Variables de entorno configuradas
- [ ] URL del webhook verificada en Facebook
- [ ] Test de verificación pasa (GET request)
- [ ] App ID y App Secret correctos

### Funcionalidad
- [ ] Logs muestran eventos recientes
- [ ] Publicaciones se guardan en BD
- [ ] Páginas de Facebook vinculadas
- [ ] API de Meta responde correctamente
- [ ] Suscripciones activas en Facebook
- [ ] Firma HMAC válida

### Troubleshooting
- [ ] No hay errores en logs
- [ ] Tokens de páginas válidos
- [ ] Sincronización de páginas actualizada
- [ ] Health check endpoint responde
- [ ] Monitor en tiempo real funciona

### Testing avanzado
- [ ] Eventos sintéticos procesan correctamente
- [ ] Scripts de diagnóstico ejecutan sin errores
- [ ] Dashboard de salud muestra métricas correctas
- [ ] Suscripciones de Facebook activas

El webhook Meta Ads está diseñado para ser robusto, escalable y facilitar la integración completa con el ecosistema Meta Business para automatizaciones avanzadas y análisis en tiempo real.

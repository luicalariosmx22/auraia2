"""
Servicio de integración con Google Calendar API
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from clientes.aura.utils.supabase_client import supabase

class GoogleCalendarService:
    """Servicio para integración con Google Calendar API"""
    
    def __init__(self, nombre_nora: str):
        self.nombre_nora = nombre_nora
        self.scopes = ['https://www.googleapis.com/auth/calendar']
        self.client_config = {
            "web": {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [f"{os.getenv('BASE_URL')}/panel_cliente/{nombre_nora}/agenda/auth/google/callback"]
            }
        }
    
    def get_authorization_url(self) -> str:
        """Genera URL de autorización OAuth2"""
        try:
            flow = Flow.from_client_config(
                self.client_config,
                scopes=self.scopes
            )
            flow.redirect_uri = self.client_config["web"]["redirect_uris"][0]
            
            authorization_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true'
            )
            
            # Guardar state para validación posterior
            self._save_oauth_state(state)
            
            return authorization_url
            
        except Exception as e:
            print(f"Error generando URL de autorización: {e}")
            raise
    
    def handle_oauth_callback(self, code: str, state: str) -> bool:
        """Maneja el callback de OAuth2 y guarda tokens"""
        try:
            # Validar state
            if not self._validate_oauth_state(state):
                raise ValueError("State inválido")
            
            # Intercambiar código por tokens
            flow = Flow.from_client_config(
                self.client_config,
                scopes=self.scopes,
                state=state
            )
            flow.redirect_uri = self.client_config["web"]["redirect_uris"][0]
            
            flow.fetch_token(code=code)
            
            credentials = flow.credentials
            
            # Guardar credenciales en BD
            self._save_credentials(credentials)
            
            return True
            
        except Exception as e:
            print(f"Error en callback OAuth2: {e}")
            return False
    
    def get_events(self, start_date: str, end_date: str) -> List[Dict]:
        """Obtiene eventos de Google Calendar"""
        try:
            service = self._get_calendar_service()
            if not service:
                return []
            
            # Convertir fechas a formato RFC3339
            time_min = datetime.fromisoformat(start_date).isoformat() + 'Z'
            time_max = datetime.fromisoformat(end_date).isoformat() + 'Z'
            
            events_result = service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Convertir a formato estándar
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                formatted_events.append({
                    'id': f"google_{event['id']}",
                    'title': event.get('summary', 'Sin título'),
                    'start': start,
                    'end': end,
                    'description': event.get('description', ''),
                    'location': event.get('location', ''),
                    'type': 'google_calendar',
                    'color': '#34d399',  # Verde para eventos de Google
                    'editable': True,
                    'google_event_id': event['id']
                })
            
            return formatted_events
            
        except HttpError as e:
            print(f"Error obteniendo eventos de Google Calendar: {e}")
            return []
        except Exception as e:
            print(f"Error general: {e}")
            return []
    
    def create_event(self, event_data: Dict) -> Optional[str]:
        """Crea evento en Google Calendar"""
        try:
            service = self._get_calendar_service()
            if not service:
                return None
            
            # Preparar datos del evento
            google_event = {
                'summary': event_data['titulo'],
                'description': event_data.get('descripcion', ''),
                'start': {
                    'dateTime': event_data['fecha_inicio'],
                    'timeZone': 'America/Mexico_City',
                },
                'end': {
                    'dateTime': event_data.get('fecha_fin', event_data['fecha_inicio']),
                    'timeZone': 'America/Mexico_City',
                },
            }
            
            if event_data.get('ubicacion'):
                google_event['location'] = event_data['ubicacion']
            
            # Crear evento
            event = service.events().insert(
                calendarId='primary',
                body=google_event
            ).execute()
            
            return event.get('id')
            
        except HttpError as e:
            print(f"Error creando evento en Google Calendar: {e}")
            return None
        except Exception as e:
            print(f"Error general: {e}")
            return None
    
    def update_event(self, google_event_id: str, event_data: Dict) -> bool:
        """Actualiza evento en Google Calendar"""
        try:
            service = self._get_calendar_service()
            if not service:
                return False
            
            # Obtener evento actual
            event = service.events().get(
                calendarId='primary',
                eventId=google_event_id
            ).execute()
            
            # Actualizar campos
            event['summary'] = event_data.get('titulo', event.get('summary'))
            event['description'] = event_data.get('descripcion', event.get('description'))
            
            if 'fecha_inicio' in event_data:
                event['start'] = {
                    'dateTime': event_data['fecha_inicio'],
                    'timeZone': 'America/Mexico_City',
                }
            
            if 'fecha_fin' in event_data:
                event['end'] = {
                    'dateTime': event_data['fecha_fin'],
                    'timeZone': 'America/Mexico_City',
                }
            
            if 'ubicacion' in event_data:
                event['location'] = event_data['ubicacion']
            
            # Actualizar evento
            updated_event = service.events().update(
                calendarId='primary',
                eventId=google_event_id,
                body=event
            ).execute()
            
            return True
            
        except HttpError as e:
            print(f"Error actualizando evento en Google Calendar: {e}")
            return False
        except Exception as e:
            print(f"Error general: {e}")
            return False
    
    def delete_event(self, google_event_id: str) -> bool:
        """Elimina evento de Google Calendar"""
        try:
            service = self._get_calendar_service()
            if not service:
                return False
            
            service.events().delete(
                calendarId='primary',
                eventId=google_event_id
            ).execute()
            
            return True
            
        except HttpError as e:
            print(f"Error eliminando evento de Google Calendar: {e}")
            return False
        except Exception as e:
            print(f"Error general: {e}")
            return False
    
    def is_configured(self) -> bool:
        """Verifica si Google Calendar está configurado"""
        try:
            config = supabase.table('google_calendar_sync') \
                .select('access_token') \
                .eq('nombre_nora', self.nombre_nora) \
                .single() \
                .execute()
            
            return bool(config.data and config.data.get('access_token'))
            
        except Exception:
            return False
    
    def _get_calendar_service(self):
        """Obtiene servicio de Google Calendar autenticado"""
        try:
            credentials = self._load_credentials()
            if not credentials:
                return None
            
            # Refrescar token si es necesario
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                self._save_credentials(credentials)
            
            service = build('calendar', 'v3', credentials=credentials)
            return service
            
        except Exception as e:
            print(f"Error obteniendo servicio de Google Calendar: {e}")
            return None
    
    def _load_credentials(self) -> Optional[Credentials]:
        """Carga credenciales desde la BD"""
        try:
            config = supabase.table('google_calendar_sync') \
                .select('*') \
                .eq('nombre_nora', self.nombre_nora) \
                .single() \
                .execute()
            
            if not config.data:
                return None
            
            credentials = Credentials(
                token=config.data['access_token'],
                refresh_token=config.data.get('refresh_token'),
                token_uri="https://oauth2.googleapis.com/token",
                client_id=os.getenv("GOOGLE_CLIENT_ID"),
                client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
                scopes=self.scopes
            )
            
            return credentials
            
        except Exception as e:
            print(f"Error cargando credenciales: {e}")
            return None
    
    def _save_credentials(self, credentials: Credentials):
        """Guarda credenciales en la BD"""
        try:
            credential_data = {
                'nombre_nora': self.nombre_nora,
                'access_token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'scopes': json.dumps(credentials.scopes),
                'actualizado_en': datetime.now().isoformat()
            }
            
            # Upsert (insert o update)
            supabase.table('google_calendar_sync') \
                .upsert(credential_data) \
                .execute()
            
        except Exception as e:
            print(f"Error guardando credenciales: {e}")
    
    def _save_oauth_state(self, state: str):
        """Guarda state de OAuth para validación"""
        try:
            # Guardar en tabla temporal o cache
            # Por simplicidad, lo guardamos en la misma tabla
            supabase.table('google_calendar_sync') \
                .upsert({
                    'nombre_nora': self.nombre_nora,
                    'oauth_state': state,
                    'state_expires': (datetime.now() + timedelta(minutes=10)).isoformat()
                }) \
                .execute()
            
        except Exception as e:
            print(f"Error guardando state OAuth: {e}")
    
    def _validate_oauth_state(self, state: str) -> bool:
        """Valida state de OAuth"""
        try:
            config = supabase.table('google_calendar_sync') \
                .select('oauth_state, state_expires') \
                .eq('nombre_nora', self.nombre_nora) \
                .single() \
                .execute()
            
            if not config.data:
                return False
            
            stored_state = config.data.get('oauth_state')
            expires = config.data.get('state_expires')
            
            if stored_state != state:
                return False
            
            if expires and datetime.fromisoformat(expires) < datetime.now():
                return False
            
            return True
            
        except Exception as e:
            print(f"Error validando state OAuth: {e}")
            return False

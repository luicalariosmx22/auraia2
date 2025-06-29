"""
Sistema de Respuestas Inteligentes para Nora
Maneja respuestas contextuales, opciones múltiples y detección de duplicados
"""

import re
import difflib
from typing import List, Dict, Optional, Tuple
from clientes.aura.utils.supabase_client import supabase
from clientes.aura.utils.memoria_conversacion import memoria_conversacion

class SistemaRespuestasInteligentes:
    def __init__(self, nombre_nora: str):
        self.nombre_nora = nombre_nora
        self.cache_conocimiento = None
        
    def obtener_conocimiento_completo(self) -> List[Dict]:
        """Obtiene todo el conocimiento disponible con metadatos"""
        if self.cache_conocimiento is not None:
            return self.cache_conocimiento
            
        try:
            response = supabase.table("conocimiento_nora") \
                .select("id, contenido, etiquetas, prioridad") \
                .eq("nombre_nora", self.nombre_nora) \
                .eq("activo", True) \
                .execute()
            
            self.cache_conocimiento = response.data if response.data else []
            return self.cache_conocimiento
        except Exception as e:
            print(f"❌ Error obteniendo conocimiento: {e}")
            return []
    
    def analizar_pregunta(self, mensaje_usuario: str) -> Dict:
        """Analiza la pregunta para determinar contexto e intención"""
        mensaje_lower = mensaje_usuario.lower()
        
        # Detectar preguntas sobre precios/costos
        palabras_precio = ['costo', 'precio', 'cuanto', 'cuánto', 'vale', 'cobran', 'pago']
        es_pregunta_precio = any(palabra in mensaje_lower for palabra in palabras_precio)
        
        # Detectar preguntas sobre cursos
        palabras_curso = ['curso', 'capacitacion', 'capacitación', 'taller', 'entrenamiento', 'clase']
        es_pregunta_curso = any(palabra in mensaje_lower for palabra in palabras_curso)
        
        # Detectar preguntas sobre ubicación/lugar
        palabras_ubicacion = ['donde', 'dónde', 'ubicacion', 'ubicación', 'lugar', 'direccion', 'dirección']
        es_pregunta_ubicacion = any(palabra in mensaje_lower for palabra in palabras_ubicacion)
        
        # Detectar preguntas sobre horarios
        palabras_horario = ['horario', 'hora', 'cuando', 'cuándo', 'fecha', 'día', 'dias']
        es_pregunta_horario = any(palabra in mensaje_lower for palabra in palabras_horario)
        
        # Detectar términos específicos (IA, marketing, etc.)
        palabras_ia = ['inteligencia artificial', 'ia', 'ai', 'artificial', 'inteligencia']
        es_pregunta_ia = any(palabra in mensaje_lower for palabra in palabras_ia)
        
        palabras_marketing = ['marketing', 'mercadotecnia', 'publicidad', 'contenido', 'redes']
        es_pregunta_marketing = any(palabra in mensaje_lower for palabra in palabras_marketing)
        
        return {
            'es_pregunta_precio': es_pregunta_precio,
            'es_pregunta_curso': es_pregunta_curso,
            'es_pregunta_ubicacion': es_pregunta_ubicacion,
            'es_pregunta_horario': es_pregunta_horario,
            'es_pregunta_ia': es_pregunta_ia,
            'es_pregunta_marketing': es_pregunta_marketing,
            'mensaje_original': mensaje_usuario,
            'mensaje_procesado': mensaje_lower
        }
    
    def buscar_opciones_relacionadas(self, analisis: Dict) -> List[Dict]:
        """Busca opciones relacionadas basadas en el análisis de la pregunta"""
        conocimiento = self.obtener_conocimiento_completo()
        opciones_encontradas = []
        
        for bloque in conocimiento:
            contenido = bloque.get('contenido', '').lower()
            etiquetas = [e.lower() for e in bloque.get('etiquetas', [])]
            
            # Buscar por términos específicos
            coincidencias = 0
            razones = []
            
            if analisis['es_pregunta_ia']:
                if any('inteligencia' in e or 'artificial' in e for e in etiquetas) or \
                   'inteligencia artificial' in contenido:
                    coincidencias += 3
                    razones.append('Contenido de IA')
            
            if analisis['es_pregunta_curso']:
                if any('curso' in e for e in etiquetas) or 'curso' in contenido:
                    coincidencias += 2
                    razones.append('Información de cursos')
            
            if analisis['es_pregunta_precio']:
                if any(palabra in contenido for palabra in ['costo', 'precio', '$', 'pago']):
                    coincidencias += 2
                    razones.append('Información de precios')
            
            if analisis['es_pregunta_ubicacion']:
                if any(palabra in contenido for palabra in ['ubicación', 'dirección', 'lugar', 'presencial']):
                    coincidencias += 2
                    razones.append('Información de ubicación')
            
            if analisis['es_pregunta_horario']:
                if any(palabra in contenido for palabra in ['horario', 'fecha', 'hora', 'día']):
                    coincidencias += 2
                    razones.append('Información de horarios')
            
            if coincidencias > 0:
                opciones_encontradas.append({
                    'bloque': bloque,
                    'puntuacion': coincidencias,
                    'razones': razones
                })
        
        # Ordenar por puntuación
        opciones_encontradas.sort(key=lambda x: x['puntuacion'], reverse=True)
        return opciones_encontradas[:5]  # Top 5 opciones
    
    def detectar_duplicados(self, opciones: List[Dict], umbral_similitud: float = 0.8) -> List[Dict]:
        """Detecta y agrupa contenido duplicado o muy similar"""
        if len(opciones) < 2:
            return opciones
        
        grupos_unicos = []
        procesados = set()
        
        for i, opcion in enumerate(opciones):
            if i in procesados:
                continue
                
            contenido_actual = opcion['bloque']['contenido']
            grupo_actual = [opcion]
            procesados.add(i)
            
            # Buscar similares
            for j, otra_opcion in enumerate(opciones[i+1:], i+1):
                if j in procesados:
                    continue
                    
                contenido_otro = otra_opcion['bloque']['contenido']
                similitud = difflib.SequenceMatcher(None, contenido_actual, contenido_otro).ratio()
                
                if similitud >= umbral_similitud:
                    grupo_actual.append(otra_opcion)
                    procesados.add(j)
            
            grupos_unicos.append(grupo_actual)
        
        # Retornar solo el mejor de cada grupo
        opciones_unicas = []
        for grupo in grupos_unicos:
            mejor_opcion = max(grupo, key=lambda x: x['puntuacion'])
            if len(grupo) > 1:
                mejor_opcion['tiene_duplicados'] = True
                mejor_opcion['num_similares'] = len(grupo) - 1
            opciones_unicas.append(mejor_opcion)
        
        return opciones_unicas
    
    def generar_respuesta_contextual(self, analisis: Dict, opciones: List[Dict]) -> str:
        """Genera una respuesta contextual basada en el análisis y opciones encontradas"""
        if not opciones:
            return self._generar_respuesta_sin_opciones(analisis)
        
        # Si hay una sola opción muy clara
        if len(opciones) == 1 and opciones[0]['puntuacion'] >= 3:
            respuesta = opciones[0]['bloque']['contenido']
            if opciones[0].get('tiene_duplicados'):
                respuesta += f"\n\n💡 Nota: Tengo información adicional relacionada si necesitas más detalles."
            return respuesta
        
        # Si hay múltiples opciones, ofrecer menú
        return self._generar_menu_opciones(analisis, opciones)
    
    def _generar_respuesta_sin_opciones(self, analisis: Dict) -> str:
        """Genera respuesta cuando no se encuentran opciones específicas"""
        if analisis['es_pregunta_curso'] and analisis['es_pregunta_precio']:
            return """
🎓 **Cursos Disponibles:**

Tengo información sobre varios cursos, pero necesito saber cuál te interesa específicamente:

1️⃣ Curso de Inteligencia Artificial
2️⃣ Cursos de Marketing Digital  
3️⃣ Otros cursos disponibles

¿Cuál te gustaría conocer en detalle? Así te puedo dar información exacta sobre costos, fechas y ubicación.
            """.strip()
        
        elif analisis['es_pregunta_curso']:
            return """
🎓 **Información de Cursos:**

Ofrecemos varios cursos especializados. ¿Te interesa alguno en particular?

• **Inteligencia Artificial** - Curso intensivo presencial
• **Marketing Digital** - Estrategias y contenido viral
• **Automatización** - Herramientas y procesos

Escribe el nombre del curso que te interesa y te doy toda la información completa.
            """.strip()
        
        elif analisis['es_pregunta_precio']:
            return """
💰 **Información de Precios:**

Para darte información precisa de costos, ¿me puedes especificar qué servicio o curso te interesa?

Tengo precios disponibles para:
• Cursos de capacitación
• Servicios de consultoría
• Proyectos de automatización

¿Cuál te gustaría conocer?
            """.strip()
        
        else:
            return """
🤔 No tengo información específica sobre eso, pero puedo ayudarte con:

📚 **Cursos y Capacitaciones**
💼 **Servicios de Consultoría** 
🤖 **Automatización e IA**
📈 **Marketing Digital**

¿Sobre cuál de estos temas te gustaría saber más?
            """.strip()
    
    def _generar_menu_opciones(self, analisis: Dict, opciones: List[Dict]) -> str:
        """Genera un menú de opciones cuando hay múltiples resultados"""
        intro = self._generar_intro_contextual(analisis)
        
        menu_items = []
        for i, opcion in enumerate(opciones, 1):
            bloque = opcion['bloque']
            etiquetas = bloque.get('etiquetas', [])
            preview = bloque.get('contenido', '')[:100] + '...'
            
            # Generar título basado en etiquetas o contenido
            titulo = self._generar_titulo_opcion(etiquetas, preview)
            
            emoji = self._obtener_emoji_por_categoria(etiquetas)
            menu_items.append(f"{emoji} **{i}️⃣ {titulo}**")
        
        menu_texto = '\n'.join(menu_items)
        
        return f"""
{intro}

{menu_texto}

Escribe el **número** de la opción que te interesa o pregúntame algo más específico.
        """.strip()
    
    def _generar_intro_contextual(self, analisis: Dict) -> str:
        """Genera introducción contextual basada en el análisis"""
        if analisis['es_pregunta_curso'] and analisis['es_pregunta_precio']:
            return "💰 Encontré información sobre costos de cursos. Tengo varias opciones:"
        elif analisis['es_pregunta_curso']:
            return "🎓 Encontré información sobre cursos disponibles:"
        elif analisis['es_pregunta_precio']:
            return "💰 Encontré información sobre precios y costos:"
        elif analisis['es_pregunta_ia']:
            return "🤖 Encontré información sobre Inteligencia Artificial:"
        elif analisis['es_pregunta_ubicacion']:
            return "📍 Encontré información sobre ubicaciones:"
        elif analisis['es_pregunta_horario']:
            return "🕒 Encontré información sobre horarios y fechas:"
        else:
            return "📋 Encontré información que puede interesarte:"
    
    def _generar_titulo_opcion(self, etiquetas: List[str], preview: str) -> str:
        """Genera título descriptivo para una opción"""
        if any('inteligencia artificial' in e.lower() for e in etiquetas):
            return "Curso de Inteligencia Artificial"
        elif any('curso' in e.lower() for e in etiquetas):
            return f"Curso - {etiquetas[0] if etiquetas else 'Información General'}"
        elif any('marketing' in e.lower() for e in etiquetas):
            return "Marketing Digital"
        else:
            # Extraer título del contenido
            lines = preview.split('\n')
            first_line = lines[0].strip()
            if len(first_line) > 5 and len(first_line) < 50:
                return first_line
            return "Información Disponible"
    
    def _obtener_emoji_por_categoria(self, etiquetas: List[str]) -> str:
        """Obtiene emoji apropiado según las etiquetas"""
        etiquetas_lower = [e.lower() for e in etiquetas]
        
        if any('inteligencia' in e or 'artificial' in e for e in etiquetas_lower):
            return "🤖"
        elif any('curso' in e for e in etiquetas_lower):
            return "📚"
        elif any('marketing' in e for e in etiquetas_lower):
            return "📈"
        elif any('precio' in e or 'costo' in e for e in etiquetas_lower):
            return "💰"
        elif any('ubicacion' in e or 'lugar' in e for e in etiquetas_lower):
            return "📍"
        else:
            return "📋"
    
    def procesar_seleccion_menu(self, mensaje_usuario: str, opciones_previas: List[Dict]) -> Optional[str]:
        """Procesa la selección del usuario de un menú previo"""
        mensaje_lower = mensaje_usuario.lower().strip()
        
        # Detectar números
        import re
        numeros = re.findall(r'\d+', mensaje_lower)
        
        if numeros:
            try:
                seleccion = int(numeros[0])
                if 1 <= seleccion <= len(opciones_previas):
                    opcion_seleccionada = opciones_previas[seleccion - 1]
                    respuesta = opcion_seleccionada['bloque']['contenido']
                    
                    if opcion_seleccionada.get('tiene_duplicados'):
                        respuesta += f"\n\n💡 Tengo {opcion_seleccionada['num_similares']} información(es) adicional(es) relacionada(s). ¿Te gustaría verla(s)?"
                    
                    return respuesta
            except (ValueError, IndexError):
                pass
        
        return None
    
    def procesar_pregunta(self, mensaje_usuario: str, telefono: str = None) -> Optional[str]:
        """
        Método principal para procesar preguntas y detectar si necesitan respuesta inteligente
        Retorna None si debe proceder con IA normal, o la respuesta inteligente si detecta ambigüedad
        """
        try:
            # Primero verificar si hay opciones previas en memoria
            opciones_previas = None
            if telefono:
                opciones_previas = memoria_conversacion.obtener_opciones(telefono, self.nombre_nora)
            
            # Si hay opciones previas, intentar procesar selección primero
            if opciones_previas:
                respuesta_seleccion = self.procesar_seleccion_menu(mensaje_usuario, opciones_previas)
                if respuesta_seleccion:
                    # Limpiar memoria después de una selección exitosa
                    if telefono:
                        memoria_conversacion.limpiar_memoria(telefono, self.nombre_nora)
                    return respuesta_seleccion
            
            # Analizar la pregunta actual
            analisis = self.analizar_pregunta(mensaje_usuario)
            
            # Solo procesar con sistema inteligente si detecta términos específicos que pueden ser ambiguos
            debe_procesar = (
                analisis['es_pregunta_precio'] or 
                analisis['es_pregunta_curso'] or
                analisis['es_pregunta_ia'] or
                (len(mensaje_usuario.split()) <= 5 and any([  # Preguntas muy cortas
                    analisis['es_pregunta_ubicacion'],
                    analisis['es_pregunta_horario']
                ]))
            )
            
            if not debe_procesar:
                return None  # Dejar que la IA normal lo maneje
            
            # Buscar opciones relacionadas
            opciones = self.buscar_opciones_relacionadas(analisis)
            
            if not opciones:
                # Si no encuentra opciones específicas pero detectó términos ambiguos, generar respuesta de clarificación
                return self._generar_respuesta_sin_opciones(analisis)
            
            # Detectar duplicados
            opciones_unicas = self.detectar_duplicados(opciones)
            
            # Si hay múltiples opciones o una sola pero con duplicados, generar menú
            if len(opciones_unicas) > 1 or (len(opciones_unicas) == 1 and opciones_unicas[0].get('tiene_duplicados')):
                # Guardar opciones en memoria para próxima interacción
                if telefono:
                    memoria_conversacion.guardar_opciones(telefono, self.nombre_nora, opciones_unicas)
                
                return self.generar_respuesta_contextual(analisis, opciones_unicas)
            
            # Si hay una sola opción clara y no tiene duplicados, dejar que la IA normal responda
            return None
            
        except Exception as e:
            print(f"❌ Error en sistema de respuestas inteligentes: {e}")
            return None

# Función de utilidad para usar el sistema
def generar_respuesta_inteligente(mensaje_usuario: str, nombre_nora: str, opciones_previas: List[Dict] = None) -> Tuple[str, List[Dict]]:
    """
    Función principal para generar respuestas inteligentes
    Retorna: (respuesta_texto, opciones_para_siguiente_interaccion)
    """
    sistema = SistemaRespuestasInteligentes(nombre_nora)
    
    # Si hay opciones previas, intentar procesar selección
    if opciones_previas:
        respuesta_seleccion = sistema.procesar_seleccion_menu(mensaje_usuario, opciones_previas)
        if respuesta_seleccion:
            return respuesta_seleccion, []
    
    # Analizar nueva pregunta
    analisis = sistema.analizar_pregunta(mensaje_usuario)
    opciones = sistema.buscar_opciones_relacionadas(analisis)
    opciones_unicas = sistema.detectar_duplicados(opciones)
    
    respuesta = sistema.generar_respuesta_contextual(analisis, opciones_unicas)
    
    return respuesta, opciones_unicas

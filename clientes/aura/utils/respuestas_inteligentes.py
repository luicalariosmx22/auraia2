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
        
        # NUEVA LÓGICA: Ser específico con lo que pregunta el usuario
        respuesta_especifica = self._generar_respuesta_especifica(analisis, opciones)
        if respuesta_especifica:
            return respuesta_especifica
        
        # Si hay una sola opción muy clara, dar respuesta completa
        if len(opciones) == 1 and opciones[0]['puntuacion'] >= 3:
            respuesta = opciones[0]['bloque']['contenido']
            if opciones[0].get('tiene_duplicados'):
                respuesta += f"\n\n💡 Nota: Tengo información adicional relacionada si necesitas más detalles."
            return respuesta
        
        # Si hay múltiples opciones, ofrecer menú
        return self._generar_menu_opciones(analisis, opciones)
    
    def _generar_respuesta_especifica(self, analisis: Dict, opciones: List[Dict]) -> str:
        """Genera respuesta específica basada en lo que exactamente pregunta el usuario"""
        mensaje_lower = analisis['mensaje_procesado']
        
        # Detectar si pregunta sobre un curso específico
        curso_especifico = None
        if 'marketing' in mensaje_lower:
            curso_especifico = 'marketing'
        elif 'inteligencia artificial' in mensaje_lower or 'ia' in mensaje_lower:
            curso_especifico = 'inteligencia artificial'
        
        if curso_especifico:
            # Buscar información específica del curso
            bloque_curso = self._encontrar_bloque_especifico(opciones, curso_especifico)
            if bloque_curso:
                contenido = bloque_curso['contenido']
                
                # Si pregunta precio específico, extraer solo el precio
                if analisis['es_pregunta_precio']:
                    precio_info = self._extraer_precio_especifico(contenido)
                    if precio_info:
                        return f"💰 **Precio del Curso de {curso_especifico.title()}:**\n\n{precio_info}"
                
                # Si pregunta ubicación específica, extraer solo ubicación
                elif analisis['es_pregunta_ubicacion']:
                    ubicacion_info = self._extraer_ubicacion_especifica(contenido)
                    if ubicacion_info:
                        return f"📍 **Ubicación del Curso de {curso_especifico.title()}:**\n\n{ubicacion_info}"
                
                # Si pregunta horario específico, extraer solo horario
                elif analisis['es_pregunta_horario']:
                    horario_info = self._extraer_horario_especifico(contenido)
                    if horario_info:
                        return f"🕒 **Horario del Curso de {curso_especifico.title()}:**\n\n{horario_info}"
                
                # Si pregunta sobre el curso en general, dar info completa
                else:
                    return f"🎓 **Curso de {curso_especifico.title()}:**\n\n{contenido}"
        
        # Si pregunta precio pero no especifica curso, mostrar precios disponibles
        elif analisis['es_pregunta_precio'] and not curso_especifico:
            precios_disponibles = self._extraer_todos_los_precios(opciones)
            if precios_disponibles:
                return f"💰 **Precios Disponibles:**\n\n{precios_disponibles}"
        
        return None  # No se pudo generar respuesta específica
    
    def _encontrar_bloque_especifico(self, opciones: List[Dict], curso_objetivo: str) -> Dict:
        """Encuentra el bloque específico del curso buscado"""
        for opcion in opciones:
            etiquetas = opcion['bloque'].get('etiquetas', [])
            for etiqueta in etiquetas:
                if curso_objetivo.lower() in etiqueta.lower():
                    return opcion['bloque']
        return None
    
    def _extraer_precio_especifico(self, contenido: str) -> str:
        """Extrae solo la información de precio del contenido"""
        lineas = contenido.split('\n')
        for linea in lineas:
            if any(palabra in linea.lower() for palabra in ['precio', 'costo', '$', 'mxn', 'pago']):
                return linea.strip()
        return None
    
    def _extraer_ubicacion_especifica(self, contenido: str) -> str:
        """Extrae solo la información de ubicación del contenido"""
        lineas = contenido.split('\n')
        for linea in lineas:
            if any(palabra in linea.lower() for palabra in ['ubicación', 'dirección', 'lugar', 'instalaciones', 'av.', 'calle']):
                return linea.strip()
        return None
    
    def _extraer_horario_especifico(self, contenido: str) -> str:
        """Extrae solo la información de horario del contenido"""
        lineas = contenido.split('\n')
        for linea in lineas:
            if any(palabra in linea.lower() for palabra in ['horario', 'fecha', 'hora', 'lunes', 'martes', 'miércoles', 'jueves', 'viernes']):
                return linea.strip()
        return None
    
    def _extraer_todos_los_precios(self, opciones: List[Dict]) -> str:
        """Extrae todos los precios disponibles de las opciones"""
        precios = []
        for opcion in opciones:
            contenido = opcion['bloque']['contenido']
            etiquetas = opcion['bloque'].get('etiquetas', [])
            
            # Determinar nombre del curso/servicio
            nombre_curso = "Servicio"
            for etiqueta in etiquetas:
                if 'marketing' in etiqueta.lower():
                    nombre_curso = "Marketing Digital"
                    break
                elif 'inteligencia artificial' in etiqueta.lower():
                    nombre_curso = "Inteligencia Artificial"
                    break
                elif 'curso' in etiqueta.lower():
                    nombre_curso = etiqueta
                    break
            
            # Extraer precio
            precio_info = self._extraer_precio_especifico(contenido)
            if precio_info:
                precios.append(f"• **{nombre_curso}:** {precio_info}")
        
        return '\n'.join(precios) if precios else None
    
    def _generar_respuesta_sin_opciones(self, analisis: Dict) -> str:
        """Genera respuesta cuando no se encuentran opciones específicas - busca por categorías"""
        conocimiento = self.obtener_conocimiento_completo()
        
        if analisis['es_pregunta_curso'] and analisis['es_pregunta_precio']:
            # Buscar todos los bloques relacionados con cursos
            bloques_cursos = self._buscar_por_categoria(conocimiento, ['curso', 'capacitacion', 'entrenamiento'])
            if bloques_cursos:
                return self._generar_respuesta_completa_cursos(bloques_cursos, incluir_precios=True)
            
        elif analisis['es_pregunta_curso']:
            # Buscar información de cursos
            bloques_cursos = self._buscar_por_categoria(conocimiento, ['curso', 'capacitacion', 'entrenamiento'])
            if bloques_cursos:
                return self._generar_respuesta_completa_cursos(bloques_cursos, incluir_precios=False)
        
        elif analisis['es_pregunta_precio']:
            # Buscar información de precios en general
            bloques_precios = self._buscar_por_categoria(conocimiento, ['precio', 'costo', 'pago'])
            if bloques_precios:
                return self._generar_respuesta_completa_precios(bloques_precios)
        
        elif analisis['es_pregunta_ia']:
            # Buscar específicamente información de IA
            bloques_ia = self._buscar_por_categoria(conocimiento, ['inteligencia artificial', 'ia', 'artificial'])
            if bloques_ia:
                return self._generar_respuesta_completa_ia(bloques_ia)
        
        # Si no encuentra nada específico, respuesta genérica
        return """
🤔 No tengo información específica sobre eso en este momento.

¿Podrías ser más específico sobre qué te interesa? Por ejemplo:
• "¿Cuánto cuesta el curso de inteligencia artificial?"
• "¿Qué cursos tienen disponibles?"
• "¿Cuál es la duración del curso?"

Así podré darte información más precisa.
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
            
            # Solo procesar con sistema inteligente si detecta términos específicos
            debe_procesar = (
                analisis['es_pregunta_precio'] or 
                analisis['es_pregunta_curso'] or
                analisis['es_pregunta_ia'] or
                analisis['es_pregunta_ubicacion'] or
                analisis['es_pregunta_horario']
            )
            
            if not debe_procesar:
                return None  # Dejar que la IA normal lo maneje
            
            # PRIMERO: Intentar dar respuesta específica basada en lo que exactamente pregunta el usuario
            conocimiento = self.obtener_conocimiento_completo()
            mensaje_lower = analisis['mensaje_procesado']
            
            # Detectar si pregunta sobre un curso específico
            curso_especifico = None
            if 'marketing' in mensaje_lower:
                curso_especifico = 'marketing'
            elif 'inteligencia artificial' in mensaje_lower or 'ia' in mensaje_lower:
                curso_especifico = 'inteligencia artificial'
            
            # Si pregunta sobre un curso específico, dar solo información de ese curso
            if curso_especifico:
                bloque_especifico = self._buscar_curso_especifico(conocimiento, curso_especifico)
                if bloque_especifico:
                    return self._generar_respuesta_curso_especifico(bloque_especifico, analisis, curso_especifico)
            
            # Si pregunta sobre cursos en general
            elif analisis['es_pregunta_curso']:
                bloques_cursos = self._buscar_por_categoria(conocimiento, ['curso', 'capacitacion', 'entrenamiento'])
                if bloques_cursos:
                    if analisis['es_pregunta_precio']:
                        # Si pregunta precio de cursos pero no especifica cuál, listar opciones
                        return self._generar_menu_precios_cursos(bloques_cursos)
                    else:
                        return self._generar_respuesta_completa_cursos(bloques_cursos, False)
            
            # Si pregunta sobre IA en general
            elif analisis['es_pregunta_ia']:
                bloques_ia = self._buscar_por_categoria(conocimiento, ['inteligencia artificial', 'ia', 'artificial'])
                if bloques_ia:
                    return self._generar_respuesta_completa_ia(bloques_ia)
            
            # Si pregunta solo precio sin especificar qué
            elif analisis['es_pregunta_precio'] and not analisis['es_pregunta_curso']:
                bloques_precios = self._buscar_por_categoria(conocimiento, ['precio', 'costo', 'pago'])
                if bloques_precios:
                    return self._generar_respuesta_completa_precios(bloques_precios)
            
            # Si no encuentra información específica por categorías, generar respuesta de clarificación
            return self._generar_respuesta_sin_opciones(analisis)
            
        except Exception as e:
            print(f"❌ Error en sistema de respuestas inteligentes: {e}")
            return None

    def _buscar_por_categoria(self, conocimiento: List[Dict], palabras_clave: List[str]) -> List[Dict]:
        """Busca bloques por palabras clave en etiquetas y contenido"""
        bloques_encontrados = []
        
        for bloque in conocimiento:
            contenido = bloque.get('contenido', '').lower()
            etiquetas = [e.lower() for e in bloque.get('etiquetas', [])]
            etiquetas_texto = ' '.join(etiquetas)
            
            # Buscar en etiquetas y contenido
            for palabra in palabras_clave:
                palabra_lower = palabra.lower()
                if (palabra_lower in etiquetas_texto or 
                    palabra_lower in contenido or
                    any(palabra_lower in etiqueta for etiqueta in etiquetas)):
                    bloques_encontrados.append(bloque)
                    break  # No agregar el mismo bloque múltiples veces
        
        return bloques_encontrados
    
    def _generar_respuesta_completa_cursos(self, bloques_cursos: List[Dict], incluir_precios: bool = False) -> str:
        """Genera respuesta completa con información de cursos"""
        if not bloques_cursos:
            return "No tengo información disponible sobre cursos en este momento."
        
        respuesta = "🎓 **Información de Cursos:**\n\n"
        
        # Agrupar por tipo de curso usando etiquetas
        cursos_agrupados = {}
        
        for bloque in bloques_cursos:
            etiquetas = bloque.get('etiquetas', [])
            contenido = bloque.get('contenido', '')
            
            # Determinar categoría del curso
            categoria = 'General'
            if any('inteligencia artificial' in e.lower() or 'ia' in e.lower() for e in etiquetas):
                categoria = 'Inteligencia Artificial'
            elif any('marketing' in e.lower() for e in etiquetas):
                categoria = 'Marketing Digital'
            elif any('automatizacion' in e.lower() for e in etiquetas):
                categoria = 'Automatización'
            
            if categoria not in cursos_agrupados:
                cursos_agrupados[categoria] = []
            cursos_agrupados[categoria].append(contenido)
        
        # Generar respuesta por categoría
        for categoria, contenidos in cursos_agrupados.items():
            if categoria != 'General':
                respuesta += f"🔹 **{categoria}:**\n"
            
            for contenido in contenidos:
                # Limpiar y formatear contenido
                contenido_limpio = contenido.strip()
                if not contenido_limpio.startswith('•') and not contenido_limpio.startswith('-'):
                    respuesta += f"• {contenido_limpio}\n"
                else:
                    respuesta += f"{contenido_limpio}\n"
            respuesta += "\n"
        
        if incluir_precios:
            respuesta += "💰 Para información específica de precios y fechas, pregúntame sobre el curso que más te interese.\n"
        
        return respuesta.strip()
    
    def _generar_respuesta_completa_precios(self, bloques_precios: List[Dict]) -> str:
        """Genera respuesta completa con información de precios"""
        if not bloques_precios:
            return "No tengo información de precios disponible en este momento."
        
        respuesta = "💰 **Información de Precios:**\n\n"
        
        for bloque in bloques_precios:
            contenido = bloque.get('contenido', '').strip()
            respuesta += f"• {contenido}\n"
        
        return respuesta.strip()
    
    def _generar_respuesta_completa_ia(self, bloques_ia: List[Dict]) -> str:
        """Genera respuesta completa con información de IA"""
        if not bloques_ia:
            return "No tengo información sobre Inteligencia Artificial disponible en este momento."
        
        respuesta = "🤖 **Inteligencia Artificial:**\n\n"
        
        for bloque in bloques_ia:
            contenido = bloque.get('contenido', '').strip()
            respuesta += f"• {contenido}\n\n"
        
        return respuesta.strip()
    
    def _buscar_curso_especifico(self, conocimiento: List[Dict], curso_objetivo: str) -> Dict:
        """Busca un bloque específico de un curso determinado"""
        for bloque in conocimiento:
            etiquetas = bloque.get('etiquetas', [])
            for etiqueta in etiquetas:
                if curso_objetivo.lower() in etiqueta.lower():
                    return bloque
        return None
    
    def _generar_respuesta_curso_especifico(self, bloque: Dict, analisis: Dict, nombre_curso: str) -> str:
        """Genera respuesta específica para un curso determinado"""
        contenido = bloque.get('contenido', '')
        
        # Si pregunta precio específico, extraer solo el precio
        if analisis['es_pregunta_precio']:
            precio_info = self._extraer_informacion_especifica(contenido, ['precio', 'costo', '$', 'mxn', 'pago'])
            if precio_info:
                return f"💰 **Precio del Curso de {nombre_curso.title()}:**\n\n{precio_info}"
        
        # Si pregunta ubicación específica, extraer solo ubicación  
        elif analisis['es_pregunta_ubicacion']:
            ubicacion_info = self._extraer_informacion_especifica(contenido, ['ubicación', 'dirección', 'lugar', 'instalaciones', 'av.', 'calle'])
            if ubicacion_info:
                return f"📍 **Ubicación del Curso de {nombre_curso.title()}:**\n\n{ubicacion_info}"
        
        # Si pregunta horario específico, extraer solo horario
        elif analisis['es_pregunta_horario']:
            horario_info = self._extraer_informacion_especifica(contenido, ['horario', 'fecha', 'hora', 'lunes', 'martes', 'miércoles', 'jueves', 'viernes'])
            if horario_info:
                return f"🕒 **Horario del Curso de {nombre_curso.title()}:**\n\n{horario_info}"
        
        # Si pregunta sobre el curso en general, dar info completa
        else:
            return f"🎓 **Curso de {nombre_curso.title()}:**\n\n{contenido}"
        
        # Si no se encontró información específica, dar el contenido completo
        return f"🎓 **Curso de {nombre_curso.title()}:**\n\n{contenido}"
    
    def _extraer_informacion_especifica(self, contenido: str, palabras_clave: List[str]) -> str:
        """Extrae información específica del contenido basada en palabras clave"""
        lineas = contenido.split('\n')
        for linea in lineas:
            if any(palabra in linea.lower() for palabra in palabras_clave):
                return linea.strip()
        return None
    
    def _generar_menu_precios_cursos(self, bloques_cursos: List[Dict]) -> str:
        """Genera menú cuando pregunta precio de cursos pero no especifica cuál"""
        precios_encontrados = []
        
        for bloque in bloques_cursos:
            etiquetas = bloque.get('etiquetas', [])
            contenido = bloque.get('contenido', '')
            
            # Determinar nombre del curso
            nombre_curso = "Curso"
            if any('marketing' in e.lower() for e in etiquetas):
                nombre_curso = "Marketing Digital"
            elif any('inteligencia artificial' in e.lower() or 'ia' in e.lower() for e in etiquetas):
                nombre_curso = "Inteligencia Artificial"
            elif etiquetas:
                nombre_curso = etiquetas[0]
            
            # Extraer precio si existe
            precio_info = self._extraer_informacion_especifica(contenido, ['precio', 'costo', '$', 'mxn', 'pago'])
            if precio_info:
                precios_encontrados.append(f"• **{nombre_curso}:** {precio_info}")
        
        if precios_encontrados:
            return f"💰 **Precios de Cursos Disponibles:**\n\n" + '\n'.join(precios_encontrados)
        else:
            return "💰 Para información de precios, ¿te interesa algún curso en particular? Tengo información sobre cursos de Inteligencia Artificial, Marketing Digital y más."

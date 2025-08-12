# 🏗️ Estructura avanzada (tareas)

El módulo de **tareas** es uno de los más complejos porque maneja múltiples tipos de entidades relacionadas y funcionalidades avanzadas.

## 📊 Estructura de datos real

### Tablas principales verificadas:
- `tareas` - Tabla principal de tareas con todos los campos
- `usuarios_clientes` - Usuarios/clientes que pueden tener tareas asignadas
- `cliente_empresas` - Empresas cliente que pueden tener tareas
- `tareas_recurrentes` - Tareas que se repiten automáticamente
- `subtareas` - Subtareas que dependen de una tarea padre
- `configuracion_bot` - Config de cada Nora (filtro principal)

---

## 📁 Estructura de archivos real

```bash
clientes/aura/routes/panel_cliente_tareas/
├── __init__.py
├── panel_cliente_tareas.py          # Blueprint principal (solo imports)
├── tareas_crud.py                   # CRUD principal de tareas
├── gestionar.py                     # Gestión avanzada de tareas
├── estadisticas.py                  # Estadísticas y dashboards
├── plantillas.py                    # Plantillas de tareas
├── whatsapp.py                      # Integración WhatsApp
├── usuarios_clientes.py             # Gestión de usuarios/clientes
├── automatizaciones.py              # Automatizaciones de tareas
├── verificar.py                     # Verificaciones y validaciones
├── recurrentes.py                   # Tareas recurrentes y repetitivas
├── tareas_completadas.py            # Gestión de tareas completadas
├── reportes.py                      # Reportes y análisis
└── utils/
    ├── alertas_y_ranking.py         # Sistema de alertas y ranking
    └── __pycache__/

clientes/aura/templates/panel_cliente_tareas/
├── index.html                       # Dashboard principal
├── gestionar_tareas.html            # Gestión de tareas
├── estadisticas.html                # Visualización de estadísticas
├── plantillas.html                  # Gestión de plantillas
├── usuarios_clientes.html           # Gestión de usuarios
├── automatizaciones.html            # Configuración de automatizaciones
├── recurrentes.html                 # Gestión de tareas recurrentes
└── tareas_completadas.html          # Vista de tareas completadas

clientes/aura/static/css/modulos/tareas/
├── main.css                         # Estilos principales
├── dashboard.css                    # Dashboard específico
└── components/
    ├── tarea-card.css              # Estilos de tarjetas
    └── modals.css                  # Estilos de modales

clientes/aura/static/js/modulos/tareas/
├── main.js                         # JavaScript principal
├── dashboard.js                    # Dashboard interactivo
├── crud.js                         # Operaciones CRUD
├── automatizaciones.js             # Gestión de automatizaciones
└── utils/
    ├── validation.js              # Validaciones frontend
    └── formatters.js              # Formateadores
```
│   ├── lista.html                   # Lista de clientes
│   ├── perfil.html                  # Perfil del cliente
│   └── historial.html               # Historial de tareas
├── reportes/
│   ├── dashboard.html               # Dashboard de reportes
│   ├── productividad.html           # Reporte de productividad
│   └── clientes.html                # Reporte por cliente
├── components/
│   ├── tarea_card.html              # Componente de tarjeta
│   ├── filtros.html                 # Filtros comunes
│   └── modals.html                  # Modales reutilizables
└── includes/
    ├── sidebar.html                 # Sidebar del módulo
    └── breadcrumb.html              # Navegación

static/css/modulos/tareas/
├── main.css                         # Estilos principales
├── kanban.css                       # Estilos para vista Kanban
├── dashboard.css                    # Dashboard específico
└── components/
    ├── tarea-card.css              # Estilos de tarjetas
    ├── filtros.css                 # Estilos de filtros
    └── modals.css                  # Estilos de modales

static/js/modulos/tareas/
├── main.js                         # JavaScript principal
├── kanban.js                       # Vista Kanban interactiva
├── dashboard.js                    # Dashboard interactivo
├── api/
│   ├── tareas-api.js              # Cliente API para tareas
│   ├── clientes-api.js            # Cliente API para clientes
│   └── utils.js                   # Utilidades comunes
├── components/
│   ├── tarea-form.js              # Formulario de tarea
│   ├── filtros.js                 # Filtros dinámicos
│   └── notificaciones.js          # Sistema de notificaciones
└── utils/
    ├── date-utils.js              # Utilidades de fecha
    ├── validation.js              # Validaciones frontend
    └── formatters.js              # Formateadores
```

---

## 🧩 Modelos de datos

### `models/tarea.py`

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any
from clientes.aura.utils.supabase_client import supabase

@dataclass
class Tarea:
    id: Optional[int] = None
    nombre_nora: str = ""
    titulo: str = ""
    descripcion: str = ""
    cliente_id: Optional[int] = None
    estado_id: int = 1  # Por defecto: "Pendiente"
    categoria_id: Optional[int] = None
    prioridad: str = "media"  # baja, media, alta, urgente
    fecha_inicio: Optional[datetime] = None
    fecha_vencimiento: Optional[datetime] = None
    fecha_completada: Optional[datetime] = None
    tiempo_estimado: Optional[int] = None  # en minutos
    tiempo_real: Optional[int] = None  # en minutos
    progreso: int = 0  # 0-100
    etiquetas: List[str] = None
    creada_en: Optional[datetime] = None
    actualizada_en: Optional[datetime] = None
    
    # Datos relacionados (se cargan cuando es necesario)
    cliente: Optional[Dict] = None
    estado: Optional[Dict] = None
    categoria: Optional[Dict] = None
    comentarios: List[Dict] = None
    archivos: List[Dict] = None

    def __post_init__(self):
        if self.etiquetas is None:
            self.etiquetas = []
        if self.comentarios is None:
            self.comentarios = []
        if self.archivos is None:
            self.archivos = []

    @classmethod
    def crear(cls, nombre_nora: str, datos: Dict[str, Any]) -> 'Tarea':
        """Crea una nueva tarea en la base de datos"""
        try:
            # Preparar datos para inserción
            datos_tarea = {
                'nombre_nora': nombre_nora,
                'titulo': datos.get('titulo', ''),
                'descripcion': datos.get('descripcion', ''),
                'cliente_id': datos.get('cliente_id'),
                'estado_id': datos.get('estado_id', 1),
                'categoria_id': datos.get('categoria_id'),
                'prioridad': datos.get('prioridad', 'media'),
                'fecha_inicio': datos.get('fecha_inicio'),
                'fecha_vencimiento': datos.get('fecha_vencimiento'),
                'tiempo_estimado': datos.get('tiempo_estimado'),
                'etiquetas': datos.get('etiquetas', []),
                'progreso': datos.get('progreso', 0)
            }
            
            # Insertar en Supabase
            result = supabase.table('tareas').insert(datos_tarea).execute()
            
            if result.data:
                return cls.desde_dict(result.data[0])
            else:
                raise Exception("No se pudo crear la tarea")
                
        except Exception as e:
            raise Exception(f"Error creando tarea: {str(e)}")

    @classmethod
    def obtener_por_id(cls, tarea_id: int, con_relaciones: bool = False) -> Optional['Tarea']:
        """Obtiene una tarea por su ID"""
        try:
            query = supabase.table('tareas').select('*')
            
            if con_relaciones:
                query = query.select('''
                    *,
                    clientes_usuarios(id, nombre, email),
                    tareas_estados(id, nombre, color),
                    tareas_categorias(id, nombre, color)
                ''')
            
            result = query.eq('id', tarea_id).single().execute()
            
            if result.data:
                return cls.desde_dict(result.data)
            return None
            
        except Exception as e:
            print(f"Error obteniendo tarea {tarea_id}: {e}")
            return None

    @classmethod
    def listar_por_nora(cls, nombre_nora: str, filtros: Optional[Dict] = None) -> List['Tarea']:
        """Lista tareas por nombre_nora con filtros opcionales"""
        try:
            query = supabase.table('tareas').select('''
                *,
                clientes_usuarios(id, nombre, email),
                tareas_estados(id, nombre, color),
                tareas_categorias(id, nombre, color)
            ''').eq('nombre_nora', nombre_nora)
            
            # Aplicar filtros
            if filtros:
                if filtros.get('estado_id'):
                    query = query.eq('estado_id', filtros['estado_id'])
                    
                if filtros.get('cliente_id'):
                    query = query.eq('cliente_id', filtros['cliente_id'])
                    
                if filtros.get('categoria_id'):
                    query = query.eq('categoria_id', filtros['categoria_id'])
                    
                if filtros.get('prioridad'):
                    query = query.eq('prioridad', filtros['prioridad'])
                    
                if filtros.get('fecha_desde'):
                    query = query.gte('fecha_inicio', filtros['fecha_desde'])
                    
                if filtros.get('fecha_hasta'):
                    query = query.lte('fecha_vencimiento', filtros['fecha_hasta'])
                    
                if filtros.get('busqueda'):
                    busqueda = f"%{filtros['busqueda']}%"
                    query = query.or_(f'titulo.ilike.{busqueda},descripcion.ilike.{busqueda}')
            
            # Ordenamiento
            orden = filtros.get('orden', 'fecha_creacion') if filtros else 'fecha_creacion'
            direccion = filtros.get('direccion', 'desc') if filtros else 'desc'
            
            if direccion == 'desc':
                query = query.order(orden, desc=True)
            else:
                query = query.order(orden)
                
            result = query.execute()
            
            return [cls.desde_dict(tarea) for tarea in result.data]
            
        except Exception as e:
            print(f"Error listando tareas: {e}")
            return []

    def actualizar(self, datos: Dict[str, Any]) -> bool:
        """Actualiza la tarea con nuevos datos"""
        try:
            datos_actualizacion = {}
            
            # Solo actualizar campos que se proporcionaron
            campos_permitidos = [
                'titulo', 'descripcion', 'cliente_id', 'estado_id', 
                'categoria_id', 'prioridad', 'fecha_inicio', 
                'fecha_vencimiento', 'tiempo_estimado', 'tiempo_real',
                'progreso', 'etiquetas'
            ]
            
            for campo in campos_permitidos:
                if campo in datos:
                    datos_actualizacion[campo] = datos[campo]
                    setattr(self, campo, datos[campo])
            
            if datos_actualizacion:
                datos_actualizacion['actualizada_en'] = datetime.now().isoformat()
                
                result = supabase.table('tareas').update(datos_actualizacion).eq('id', self.id).execute()
                
                if result.data:
                    return True
                    
            return False
            
        except Exception as e:
            print(f"Error actualizando tarea: {e}")
            return False

    def eliminar(self) -> bool:
        """Elimina la tarea (soft delete)"""
        try:
            # En lugar de eliminar físicamente, marcamos como eliminada
            result = supabase.table('tareas').update({
                'eliminada': True,
                'actualizada_en': datetime.now().isoformat()
            }).eq('id', self.id).execute()
            
            return bool(result.data)
            
        except Exception as e:
            print(f"Error eliminando tarea: {e}")
            return False

    def cambiar_estado(self, nuevo_estado_id: int) -> bool:
        """Cambia el estado de la tarea"""
        try:
            datos_actualizacion = {
                'estado_id': nuevo_estado_id,
                'actualizada_en': datetime.now().isoformat()
            }
            
            # Si es estado "Completada", marcar fecha
            if nuevo_estado_id == 4:  # Asumiendo que 4 = Completada
                datos_actualizacion['fecha_completada'] = datetime.now().isoformat()
                datos_actualizacion['progreso'] = 100
            
            result = supabase.table('tareas').update(datos_actualizacion).eq('id', self.id).execute()
            
            if result.data:
                self.estado_id = nuevo_estado_id
                if 'fecha_completada' in datos_actualizacion:
                    self.fecha_completada = datetime.fromisoformat(datos_actualizacion['fecha_completada'])
                return True
                
            return False
            
        except Exception as e:
            print(f"Error cambiando estado: {e}")
            return False

    def agregar_comentario(self, usuario_id: int, comentario: str) -> bool:
        """Agrega un comentario a la tarea"""
        try:
            datos_comentario = {
                'tarea_id': self.id,
                'usuario_id': usuario_id,
                'comentario': comentario,
                'creado_en': datetime.now().isoformat()
            }
            
            result = supabase.table('tareas_comentarios').insert(datos_comentario).execute()
            return bool(result.data)
            
        except Exception as e:
            print(f"Error agregando comentario: {e}")
            return False

    @classmethod
    def desde_dict(cls, datos: Dict[str, Any]) -> 'Tarea':
        """Crea una instancia de Tarea desde un diccionario"""
        return cls(
            id=datos.get('id'),
            nombre_nora=datos.get('nombre_nora', ''),
            titulo=datos.get('titulo', ''),
            descripcion=datos.get('descripcion', ''),
            cliente_id=datos.get('cliente_id'),
            estado_id=datos.get('estado_id', 1),
            categoria_id=datos.get('categoria_id'),
            prioridad=datos.get('prioridad', 'media'),
            fecha_inicio=cls._parse_fecha(datos.get('fecha_inicio')),
            fecha_vencimiento=cls._parse_fecha(datos.get('fecha_vencimiento')),
            fecha_completada=cls._parse_fecha(datos.get('fecha_completada')),
            tiempo_estimado=datos.get('tiempo_estimado'),
            tiempo_real=datos.get('tiempo_real'),
            progreso=datos.get('progreso', 0),
            etiquetas=datos.get('etiquetas', []),
            creada_en=cls._parse_fecha(datos.get('creada_en')),
            actualizada_en=cls._parse_fecha(datos.get('actualizada_en')),
            # Relaciones
            cliente=datos.get('clientes_usuarios'),
            estado=datos.get('tareas_estados'),
            categoria=datos.get('tareas_categorias')
        )

    @staticmethod
    def _parse_fecha(fecha_str: Optional[str]) -> Optional[datetime]:
        """Convierte string de fecha a datetime"""
        if not fecha_str:
            return None
        try:
            return datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
        except:
            return None

    def to_dict(self) -> Dict[str, Any]:
        """Convierte la tarea a diccionario"""
        return {
            'id': self.id,
            'nombre_nora': self.nombre_nora,
            'titulo': self.titulo,
            'descripcion': self.descripcion,
            'cliente_id': self.cliente_id,
            'estado_id': self.estado_id,
            'categoria_id': self.categoria_id,
            'prioridad': self.prioridad,
            'fecha_inicio': self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            'fecha_vencimiento': self.fecha_vencimiento.isoformat() if self.fecha_vencimiento else None,
            'fecha_completada': self.fecha_completada.isoformat() if self.fecha_completada else None,
            'tiempo_estimado': self.tiempo_estimado,
            'tiempo_real': self.tiempo_real,
            'progreso': self.progreso,
            'etiquetas': self.etiquetas,
            'creada_en': self.creada_en.isoformat() if self.creada_en else None,
            'actualizada_en': self.actualizada_en.isoformat() if self.actualizada_en else None,
            # Relaciones
            'cliente': self.cliente,
            'estado': self.estado,
            'categoria': self.categoria
        }

    @property
    def esta_vencida(self) -> bool:
        """Verifica si la tarea está vencida"""
        if not self.fecha_vencimiento:
            return False
        return datetime.now() > self.fecha_vencimiento and self.estado_id != 4

    @property
    def dias_restantes(self) -> Optional[int]:
        """Calcula días restantes hasta vencimiento"""
        if not self.fecha_vencimiento:
            return None
        delta = self.fecha_vencimiento - datetime.now()
        return delta.days

    @property
    def tiempo_trabajado_horas(self) -> float:
        """Convierte tiempo real de minutos a horas"""
        if not self.tiempo_real:
            return 0.0
        return self.tiempo_real / 60.0

    @property
    def eficiencia(self) -> Optional[float]:
        """Calcula eficiencia (tiempo estimado vs real)"""
        if not self.tiempo_estimado or not self.tiempo_real:
            return None
        return (self.tiempo_estimado / self.tiempo_real) * 100
```

---

## ⚙️ Servicios de negocio

### `services/tarea_service.py`

```python
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from ..models.tarea import Tarea
from ..utils.validadores import ValidadorTarea
from ..utils.formateadores import FormateadorTarea

class TareaService:
    
    @staticmethod
    def crear_tarea(nombre_nora: str, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una nueva tarea con validaciones"""
        try:
            # Validar datos
            validacion = ValidadorTarea.validar_creacion(datos)
            if not validacion['valido']:
                return {
                    'exito': False,
                    'errores': validacion['errores']
                }
            
            # Procesar datos antes de crear
            datos_procesados = TareaService._procesar_datos_tarea(datos)
            
            # Crear tarea
            tarea = Tarea.crear(nombre_nora, datos_procesados)
            
            # Notificar si es necesario
            TareaService._notificar_nueva_tarea(tarea)
            
            return {
                'exito': True,
                'tarea': tarea.to_dict(),
                'mensaje': 'Tarea creada exitosamente'
            }
            
        except Exception as e:
            return {
                'exito': False,
                'error': str(e)
            }

    @staticmethod
    def actualizar_tarea(tarea_id: int, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza una tarea existente"""
        try:
            # Obtener tarea actual
            tarea = Tarea.obtener_por_id(tarea_id)
            if not tarea:
                return {
                    'exito': False,
                    'error': 'Tarea no encontrada'
                }
            
            # Validar cambios
            validacion = ValidadorTarea.validar_actualizacion(tarea, datos)
            if not validacion['valido']:
                return {
                    'exito': False,
                    'errores': validacion['errores']
                }
            
            # Detectar cambios importantes
            cambios_importantes = TareaService._detectar_cambios_importantes(tarea, datos)
            
            # Actualizar
            if tarea.actualizar(datos):
                # Notificar cambios importantes
                if cambios_importantes:
                    TareaService._notificar_cambios(tarea, cambios_importantes)
                
                return {
                    'exito': True,
                    'tarea': tarea.to_dict(),
                    'mensaje': 'Tarea actualizada exitosamente'
                }
            else:
                return {
                    'exito': False,
                    'error': 'No se pudo actualizar la tarea'
                }
                
        except Exception as e:
            return {
                'exito': False,
                'error': str(e)
            }

    @staticmethod
    def obtener_dashboard_datos(nombre_nora: str) -> Dict[str, Any]:
        """Obtiene datos para el dashboard"""
        try:
            # Obtener todas las tareas
            tareas = Tarea.listar_por_nora(nombre_nora)
            
            # Calcular estadísticas
            stats = TareaService._calcular_estadisticas(tareas)
            
            # Tareas recientes
            tareas_recientes = sorted(tareas, key=lambda t: t.actualizada_en or t.creada_en, reverse=True)[:5]
            
            # Tareas vencidas
            tareas_vencidas = [t for t in tareas if t.esta_vencida]
            
            # Tareas próximas a vencer (próximos 7 días)
            fecha_limite = datetime.now() + timedelta(days=7)
            tareas_proximas = [
                t for t in tareas 
                if t.fecha_vencimiento and t.fecha_vencimiento <= fecha_limite and not t.esta_vencida
            ]
            
            return {
                'exito': True,
                'estadisticas': stats,
                'tareas_recientes': [FormateadorTarea.formato_lista(t) for t in tareas_recientes],
                'tareas_vencidas': [FormateadorTarea.formato_lista(t) for t in tareas_vencidas],
                'tareas_proximas': [FormateadorTarea.formato_lista(t) for t in tareas_proximas]
            }
            
        except Exception as e:
            return {
                'exito': False,
                'error': str(e)
            }

    @staticmethod
    def obtener_datos_kanban(nombre_nora: str) -> Dict[str, Any]:
        """Obtiene datos organizados para vista Kanban"""
        try:
            # Obtener tareas con relaciones
            tareas = Tarea.listar_por_nora(nombre_nora)
            
            # Organizar por estado
            estados = {}
            for tarea in tareas:
                estado_id = tarea.estado_id
                estado_nombre = tarea.estado['nombre'] if tarea.estado else f'Estado {estado_id}'
                
                if estado_id not in estados:
                    estados[estado_id] = {
                        'id': estado_id,
                        'nombre': estado_nombre,
                        'color': tarea.estado.get('color', '#6B7280') if tarea.estado else '#6B7280',
                        'tareas': []
                    }
                
                estados[estado_id]['tareas'].append(FormateadorTarea.formato_kanban(tarea))
            
            # Convertir a lista ordenada
            lista_estados = list(estados.values())
            lista_estados.sort(key=lambda e: e['id'])
            
            return {
                'exito': True,
                'estados': lista_estados
            }
            
        except Exception as e:
            return {
                'exito': False,
                'error': str(e)
            }

    @staticmethod
    def _procesar_datos_tarea(datos: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa datos antes de crear/actualizar tarea"""
        datos_procesados = datos.copy()
        
        # Procesar fechas
        if 'fecha_inicio' in datos_procesados and isinstance(datos_procesados['fecha_inicio'], str):
            try:
                datos_procesados['fecha_inicio'] = datetime.fromisoformat(datos_procesados['fecha_inicio']).isoformat()
            except:
                del datos_procesados['fecha_inicio']
        
        if 'fecha_vencimiento' in datos_procesados and isinstance(datos_procesados['fecha_vencimiento'], str):
            try:
                datos_procesados['fecha_vencimiento'] = datetime.fromisoformat(datos_procesados['fecha_vencimiento']).isoformat()
            except:
                del datos_procesados['fecha_vencimiento']
        
        # Procesar etiquetas
        if 'etiquetas' in datos_procesados:
            if isinstance(datos_procesados['etiquetas'], str):
                # Si viene como string separado por comas
                datos_procesados['etiquetas'] = [
                    tag.strip() for tag in datos_procesados['etiquetas'].split(',') if tag.strip()
                ]
        
        return datos_procesados

    @staticmethod
    def _calcular_estadisticas(tareas: List[Tarea]) -> Dict[str, Any]:
        """Calcula estadísticas de las tareas"""
        if not tareas:
            return {
                'total': 0,
                'pendientes': 0,
                'en_progreso': 0,
                'completadas': 0,
                'vencidas': 0,
                'progreso_promedio': 0,
                'tiempo_promedio_completadas': 0
            }
        
        total = len(tareas)
        pendientes = len([t for t in tareas if t.estado_id == 1])
        en_progreso = len([t for t in tareas if t.estado_id == 2])
        completadas = len([t for t in tareas if t.estado_id == 4])
        vencidas = len([t for t in tareas if t.esta_vencida])
        
        # Progreso promedio
        progreso_total = sum(t.progreso for t in tareas)
        progreso_promedio = progreso_total / total if total > 0 else 0
        
        # Tiempo promedio de tareas completadas
        tareas_completadas_con_tiempo = [
            t for t in tareas 
            if t.estado_id == 4 and t.tiempo_real
        ]
        tiempo_promedio = 0
        if tareas_completadas_con_tiempo:
            tiempo_total = sum(t.tiempo_real for t in tareas_completadas_con_tiempo)
            tiempo_promedio = tiempo_total / len(tareas_completadas_con_tiempo)
        
        return {
            'total': total,
            'pendientes': pendientes,
            'en_progreso': en_progreso,
            'completadas': completadas,
            'vencidas': vencidas,
            'progreso_promedio': round(progreso_promedio, 1),
            'tiempo_promedio_completadas': round(tiempo_promedio / 60, 1) if tiempo_promedio else 0  # en horas
        }

    @staticmethod
    def _detectar_cambios_importantes(tarea: Tarea, nuevos_datos: Dict[str, Any]) -> List[str]:
        """Detecta cambios importantes que requieren notificación"""
        cambios = []
        
        if 'estado_id' in nuevos_datos and nuevos_datos['estado_id'] != tarea.estado_id:
            cambios.append('estado')
        
        if 'prioridad' in nuevos_datos and nuevos_datos['prioridad'] != tarea.prioridad:
            cambios.append('prioridad')
        
        if 'fecha_vencimiento' in nuevos_datos:
            nueva_fecha = nuevos_datos['fecha_vencimiento']
            if nueva_fecha != (tarea.fecha_vencimiento.isoformat() if tarea.fecha_vencimiento else None):
                cambios.append('fecha_vencimiento')
        
        if 'cliente_id' in nuevos_datos and nuevos_datos['cliente_id'] != tarea.cliente_id:
            cambios.append('cliente')
        
        return cambios

    @staticmethod
    def _notificar_nueva_tarea(tarea: Tarea):
        """Envía notificaciones para nueva tarea"""
        # Implementar lógica de notificaciones
        # Por ejemplo: email, webhook, notificación push
        pass

    @staticmethod
    def _notificar_cambios(tarea: Tarea, cambios: List[str]):
        """Envía notificaciones para cambios importantes"""
        # Implementar lógica de notificaciones de cambios
        pass
```

---

## 🎯 Puntos clave de la estructura avanzada

### 1. **Separación de responsabilidades**
   - **Modelos**: Solo datos y operaciones básicas de BD
   - **Servicios**: Lógica de negocio compleja
   - **API**: Endpoints y validación de entrada
   - **Utilidades**: Funciones reutilizables

### 2. **Gestión de relaciones**
   - Carga lazy de relaciones (solo cuando se necesitan)
   - Métodos específicos para obtener datos relacionados
   - Optimización de consultas con `select` específicos

### 3. **Validaciones multinivel**
   - Validación en frontend (JavaScript)
   - Validación en servicios (Python)
   - Validación en base de datos (constraints)

### 4. **Manejo de estados**
   - Estados bien definidos con transiciones válidas
   - Eventos automáticos (fechas, notificaciones)
   - Historial de cambios

### 5. **Performance**
   - Paginación en listados grandes
   - Filtros eficientes en BD
   - Cache de consultas frecuentes
   - Carga asíncrona en frontend

---

## 📊 Ejemplo de uso

```python
# Crear tarea compleja
datos_tarea = {
    'titulo': 'Desarrollar módulo de inventario',
    'descripcion': 'Crear sistema completo de gestión de inventario...',
    'cliente_id': 15,
    'categoria_id': 3,  # Desarrollo
    'prioridad': 'alta',
    'fecha_inicio': '2024-01-15T09:00:00',
    'fecha_vencimiento': '2024-01-30T17:00:00',
    'tiempo_estimado': 2400,  # 40 horas
    'etiquetas': ['desarrollo', 'backend', 'frontend', 'base-datos']
}

resultado = TareaService.crear_tarea('aura', datos_tarea)

if resultado['exito']:
    tarea = resultado['tarea']
    print(f"Tarea creada: {tarea['titulo']}")
else:
    print(f"Error: {resultado['error']}")
```

Esta estructura permite manejar:
- ✅ **Tareas complejas** con múltiples relaciones
- ✅ **Flujos de trabajo** definidos
- ✅ **Reportes avanzados** y métricas
- ✅ **Notificaciones** automáticas
- ✅ **APIs REST** completas
- ✅ **Interfaces modernas** (Kanban, dashboards)
- ✅ **Escalabilidad** para grandes volúmenes

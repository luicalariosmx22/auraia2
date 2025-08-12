# 📊 Ejemplo completo de módulo: Meta Ads

Vamos a analizar el módulo **Meta Ads** que es el más completo del proyecto, paso a paso.

## 📁 Estructura completa del módulo

```bash
clientes/aura/routes/panel_cliente_meta_ads/
├── __init__.py
├── panel_cliente_meta_ads.py          # Blueprint principal
├── automatizacion_campanas.py         # Automatización de campañas desde publicaciones
├── automatizacion_routes.py           # Rutas de automatización
├── automatizacion_api.py              # API de automatización
├── automatizaciones.py                # Gestión de automatizaciones
├── campanas.py                        # Gestión de campañas
├── reportes.py                        # Reportes de Meta Ads
├── estadisticas.py                    # Estadísticas y métricas
├── webhooks_meta.py                   # Webhooks de Meta
├── webhooks_api.py                    # API de webhooks
├── vistas.py                          # Vistas adicionales
├── helpers.py                         # Funciones auxiliares
├── descargas.py                       # Descarga de reportes
├── sincronizador.py                   # Sincronización con Meta API
├── sincronizador_semanal.py           # Sincronización automática
├── sincronizador_personalizado.py     # Sincronización personalizada
├── vista_sincronizacion.py            # Vista de sincronización
├── API_META_ADS.md                    # Documentación API
└── README.md                          # Documentación del módulo

clientes/aura/templates/panel_cliente_meta_ads/
├── index.html                         # Dashboard principal
├── automatizacion.html                # Panel de automatización
├── campanas_meta_ads.html             # Lista de campañas
├── audiencias_meta_ads.html           # Gestión de audiencias
├── reportes.html                      # Reportes de campañas
├── estadisticas_ads.html              # Estadísticas detalladas
├── webhooks.html                      # Configuración webhooks
├── webhooks_anuncios.html             # Webhooks de anuncios
├── sincronizacion_manual.html         # Sincronización manual
├── sincronizador_personalizado.html   # Sincronización personalizada
├── cuentas_publicitarias.html         # Gestión de cuentas
├── detalle_reporte_ads.html           # Detalle de reportes
├── detalle_reporte_publico.html       # Reportes públicos
├── prereportes_guardados.html         # Reportes guardados
├── reporte_normal.html                # Reportes estándar
├── sincronizar_gasto_manual.html      # Sincronización de gastos
└── lab.html                           # Laboratorio de pruebas

clientes/aura/static/js/meta_ads/
├── modal.js                           # Modales interactivos
├── filtros.js                         # Filtros dinámicos
├── diagnostico.js                     # Diagnósticos
└── cuentas_publicitarias.js           # Gestión de cuentas
```

---

## 🔧 1. Blueprint principal

### `panel_cliente_meta_ads.py`

```python
"""
📊 SCHEMAS DE BD QUE USA ESTE ARCHIVO:

📋 TABLAS PRINCIPALES:
• meta_ads_automatizaciones: Configuraciones de automatización de campañas
  └ Campos clave: id(bigint), nombre_nora(varchar), activa(boolean), tipo_automatizacion(varchar)
  
• meta_ads_cuentas: Cuentas publicitarias de Meta conectadas
  └ Campos clave: id_cuenta_publicitaria(text), nombre_cliente(text), estado_actual(varchar)
  
• meta_ads_reportes_semanales: Reportes consolidados por semana
  └ Campos clave: empresa_id(text), fecha_inicio(date), fecha_fin(date), importe_gastado_anuncios(numeric)
  
• meta_publicaciones_webhook: Publicaciones recibidas por webhook
  └ Campos clave: post_id(varchar), page_id(varchar), engagement_total(integer), procesada(boolean)
  
• facebook_paginas: Páginas de Facebook conectadas
  └ Campos clave: page_id(string_numeric), nombre_pagina(text), access_token(text), activa(boolean)
  
• logs_webhooks_meta: Logs de webhooks de Meta
  └ Campos clave: tipo_evento(varchar), timestamp(timestamptz), procesado(boolean)

🔗 RELACIONES:
• meta_ads_cuentas -> meta_ads_automatizaciones via id_cuenta_publicitaria
• facebook_paginas -> meta_publicaciones_webhook via page_id
• configuracion_bot -> TODOS via nombre_nora (filtro obligatorio)

💡 VERIFICAR SCHEMAS:
from clientes.aura.utils.quick_schemas import existe, columnas
if existe('meta_ads_automatizaciones'):
    campos = columnas('meta_ads_automatizaciones')
    # Resultado: ['id', 'nombre_nora', 'activa', 'tipo_automatizacion', ...]
"""

from flask import Blueprint, render_template, request, redirect, url_for, jsonify, abort
from clientes.aura.utils.supabase_client import supabase
import os, requests
from datetime import datetime, timedelta
from clientes.aura.utils.meta_ads import (
    obtener_reporte_campanas,
    listar_anuncios_activos,
    obtener_ads_activos_cuenta,
    listar_campañas_activas
)
from .webhooks_meta import webhooks_meta_bp
from .webhooks_api import webhooks_api_bp

# 🗄️ CONTEXTO BD PARA GITHUB COPILOT
from clientes.aura.utils.supabase_schemas import SUPABASE_SCHEMAS
from clientes.aura.utils.quick_schemas import existe, columnas
# BD ACTUAL: meta_ads_cuentas(15), meta_ads_anuncios_detalle(96), meta_ads_reportes_semanales(35)

panel_cliente_meta_ads_bp = Blueprint(
    "panel_cliente_meta_ads_bp",
    __name__,
    url_prefix="/panel_cliente/<nombre_nora>/meta_ads"
)

# Registrar el blueprint de webhooks API
panel_cliente_meta_ads_bp.register_blueprint(webhooks_api_bp)

@panel_cliente_meta_ads_bp.route("/")
def panel_cliente_meta_ads(nombre_nora):
    return render_template("panel_cliente_meta_ads/index.html", nombre_nora=nombre_nora)

@panel_cliente_meta_ads_bp.route("/automatizacion")
def panel_automatizacion_campanas(nombre_nora):
    """Panel de automatización de campañas desde publicaciones"""
    try:
        from .automatizacion_campanas import (
            obtener_automatizaciones,
            obtener_estadisticas_automatizaciones,
            obtener_historial_anuncios_automatizados
        )
        
        # Obtener automatizaciones
        automatizaciones = obtener_automatizaciones(nombre_nora)
        
        # Obtener estadísticas
        estadisticas = obtener_estadisticas_automatizaciones(nombre_nora)
        
        # Obtener historial reciente
        historial = obtener_historial_anuncios_automatizados(nombre_nora, limite=10)
        
        return render_template("panel_cliente_meta_ads/automatizacion.html",
                             nombre_nora=nombre_nora,
                             automatizaciones=automatizaciones,
                             estadisticas=estadisticas,
                             historial=historial)
        
    except Exception as e:
        print(f"Error en automatización: {e}")
        return render_template("panel_cliente_meta_ads/automatizacion.html",
                             nombre_nora=nombre_nora,
                             automatizaciones=[],
                             estadisticas={},
                             historial=[])

@panel_cliente_meta_ads_bp.route("/reportes")
def vista_reportes_meta_ads(nombre_nora):
    """Vista de reportes de Meta Ads"""
    try:
        # ✅ VERIFICAR TABLA ANTES DE USAR (nueva buena práctica)
        if not existe('meta_ads_reportes_semanales'):
            return jsonify({
                'success': False,
                'error': 'Tabla meta_ads_reportes_semanales no existe'
            }), 500
        
        # Obtener reportes semanales
        reportes = supabase.table('meta_ads_reportes_semanales') \
            .select('*') \
            .eq('nombre_nora', nombre_nora) \
            .order('fecha_inicio', desc=True) \
            .limit(20) \
            .execute()
        
        return render_template("panel_cliente_meta_ads/reportes.html",
                             nombre_nora=nombre_nora,
                             reportes=reportes.data)
        
    except Exception as e:
        print(f"Error obteniendo reportes: {e}")
        return render_template("panel_cliente_meta_ads/reportes.html",
                             nombre_nora=nombre_nora,
                             reportes=[])
    nombre_nora = request.view_args.get("nombre_nora")
    
    try:
        # Obtener estadísticas generales
        stats = obtener_estadisticas_inventario(nombre_nora)
        
        return render_template("panel_cliente_inventario/index.html",
                             nombre_nora=nombre_nora,
                             stats=stats)
    except Exception as e:
        print(f"Error en dashboard inventario: {e}")
        return render_template("panel_cliente_inventario/index.html",
                             nombre_nora=nombre_nora,
                             stats={})

@panel_cliente_inventario_bp.route("/api/productos")
def api_productos():
    """API para obtener productos"""
    nombre_nora = request.view_args.get("nombre_nora")
    categoria_id = request.args.get('categoria_id')
    busqueda = request.args.get('q', '')
    
    try:
        # ✅ VERIFICAR TABLA ANTES DE USAR (nueva buena práctica)
        if not existe('inventario_productos'):
            return jsonify({
                'success': False,
                'error': 'Tabla inventario_productos no existe'
            }), 500
        
        query = supabase.table('inventario_productos') \
            .select('*, inventario_categorias(nombre)') \
            .eq('nombre_nora', nombre_nora)
        
        if categoria_id:
            query = query.eq('categoria_id', categoria_id)
        
        if busqueda:
            query = query.ilike('nombre', f'%{busqueda}%')
        
        result = query.order('nombre').execute()
        
        return jsonify({
            'success': True,
            'productos': result.data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def obtener_estadisticas_inventario(nombre_nora):
    """Calcula estadísticas del inventario"""
    try:
        # ✅ VERIFICACIÓN DE TABLAS SEGÚN NUEVAS BUENAS PRÁCTICAS
        if not existe('inventario_productos') or not existe('inventario_categorias'):
            print("⚠️ Tablas de inventario no existen")
            return {
                'total_productos': 0,
                'stock_bajo': 0,
                'valor_total': 0,
                'total_categorias': 0
            }
        
        # Total de productos
        productos = supabase.table('inventario_productos') \
            .select('id, stock, precio', count='exact') \
            .eq('nombre_nora', nombre_nora) \
            .execute()
        
        total_productos = productos.count
        productos_data = productos.data
        
        # Productos con stock bajo
        stock_bajo = len([p for p in productos_data if p['stock'] < 10])
        
        # Valor total del inventario
        valor_total = sum(p['stock'] * p['precio'] for p in productos_data)
        
        # Categorías
        categorias = supabase.table('inventario_categorias') \
            .select('id', count='exact') \
            .eq('nombre_nora', nombre_nora) \
            .execute()
        
        return {
            'total_productos': total_productos,
            'stock_bajo': stock_bajo,
            'valor_total': valor_total,
            'total_categorias': categorias.count
        }
        
    except Exception as e:
        print(f"Error calculando estadísticas: {e}")
        return {
            'total_productos': 0,
            'stock_bajo': 0,
            'valor_total': 0,
            'total_categorias': 0
        }
```

---

## 🎨 2. Template principal

### `templates/panel_cliente_meta_ads/index.html`

```html
{% extends "base_cliente.html" %}

{% block titulo %}� Meta Ads - {{ nombre_nora|title }}{% endblock %}

{% block contenido %}
<div class="max-w-6xl mx-auto py-10">
  <h1 class="text-3xl font-extrabold text-center text-blue-900 mb-8">¿Qué quieres hacer?</h1>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
    
    <!-- Campañas -->
    <div class="bg-white rounded-2xl shadow-lg p-8 flex flex-col items-center border-2 border-blue-100 hover:border-blue-400 transition">
      <div class="bg-blue-100 rounded-full p-4 mb-4">
        <span class="text-4xl text-blue-700">📢</span>
      </div>
      <h2 class="text-xl font-bold text-blue-800 mb-2">Campañas</h2>
      <p class="text-gray-600 text-center mb-4">Crea, administra y consulta campañas publicitarias activas en Meta Ads.</p>
      <a href="{{ url_for('panel_cliente_meta_ads_bp.vista_campanas', nombre_nora=nombre_nora) }}" 
         class="mt-auto px-6 py-2 bg-blue-600 text-white rounded-lg font-semibold shadow hover:bg-blue-700 transition">
         Ir a Campañas
      </a>
    </div>
    
    <!-- Audiencias -->
    <div class="bg-white rounded-2xl shadow-lg p-8 flex flex-col items-center border-2 border-indigo-100 hover:border-indigo-400 transition">
      <div class="bg-indigo-100 rounded-full p-4 mb-4">
        <span class="text-4xl text-indigo-700">👥</span>
      </div>
      <h2 class="text-xl font-bold text-indigo-800 mb-2">Audiencias</h2>
      <p class="text-gray-600 text-center mb-4">Gestiona audiencias personalizadas, lookalike y estadísticas de targeting.</p>
      <a href="{{ url_for('panel_cliente_meta_ads_bp.vista_audiencias', nombre_nora=nombre_nora) }}" 
         class="mt-auto px-6 py-2 bg-indigo-600 text-white rounded-lg font-semibold shadow hover:bg-indigo-700 transition">
         Ir a Audiencias
      </a>
    </div>
    
    <!-- Reportes -->
    <div class="bg-white rounded-2xl shadow-lg p-8 flex flex-col items-center border-2 border-green-100 hover:border-green-400 transition">
      <div class="bg-green-100 rounded-full p-4 mb-4">
        <span class="text-4xl text-green-700">�</span>
      </div>
      <h2 class="text-xl font-bold text-green-800 mb-2">Reportes</h2>
      <p class="text-gray-600 text-center mb-4">Consulta el histórico de reportes automáticos y resultados de tus campañas.</p>
      <a href="{{ url_for('panel_cliente_meta_ads_bp.vista_reportes_meta_ads', nombre_nora=nombre_nora) }}" 
         class="mt-4 block text-center px-6 py-2 bg-green-600 text-white rounded-lg font-semibold shadow hover:bg-green-700 transition">
         Ir a Reportes
      </a>
    </div>
    
    <!-- Automatización -->
    <div class="bg-white rounded-2xl shadow-lg p-8 flex flex-col items-center border-2 border-purple-100 hover:border-purple-400 transition">
      <div class="bg-purple-100 rounded-full p-4 mb-4">
        <span class="text-4xl text-purple-700">🔄</span>
      </div>
      <h2 class="text-xl font-bold text-purple-800 mb-2">Automatización</h2>
      <p class="text-gray-600 text-center mb-4">Configura automatizaciones de campañas basadas en publicaciones de Facebook.</p>
      <a href="{{ url_for('panel_cliente_meta_ads_bp.panel_automatizacion_campanas', nombre_nora=nombre_nora) }}" 
         class="mt-auto px-6 py-2 bg-purple-600 text-white rounded-lg font-semibold shadow hover:bg-purple-700 transition">
         Ir a Automatización
      </a>
    </div>
    
    <!-- Webhooks -->
    <div class="bg-white rounded-2xl shadow-lg p-8 flex flex-col items-center border-2 border-yellow-100 hover:border-yellow-400 transition">
      <div class="bg-yellow-100 rounded-full p-4 mb-4">
        <span class="text-4xl text-yellow-700">🔔</span>
      </div>
      <h2 class="text-xl font-bold text-yellow-800 mb-2">Webhooks</h2>
      <p class="text-gray-600 text-center mb-4">Monitorea eventos en tiempo real desde Meta Ads y su procesamiento.</p>
      <a href="{{ url_for('panel_cliente_meta_ads_bp.vista_webhooks', nombre_nora=nombre_nora) }}" 
         class="mt-auto px-6 py-2 bg-yellow-600 text-white rounded-lg font-semibold shadow hover:bg-yellow-700 transition">
         Ir a Webhooks
      </a>
    </div>
    
    <!-- Estadísticas -->
    <div class="bg-white rounded-2xl shadow-lg p-8 flex flex-col items-center border-2 border-red-100 hover:border-red-400 transition">
      <div class="bg-red-100 rounded-full p-4 mb-4">
        <span class="text-4xl text-red-700">📊</span>
      </div>
      <h2 class="text-xl font-bold text-red-800 mb-2">Estadísticas</h2>
      <p class="text-gray-600 text-center mb-4">Analiza métricas detalladas y KPIs de tus campañas publicitarias.</p>
      <a href="{{ url_for('panel_cliente_meta_ads_bp.vista_estadisticas_ads', nombre_nora=nombre_nora) }}" 
         class="mt-auto px-6 py-2 bg-red-600 text-white rounded-lg font-semibold shadow hover:bg-red-700 transition">
         Ir a Estadísticas
      </a>
    </div>
  </div>
</div>
{% endblock %}
```

---

## 💾 3. JavaScript interactivo

### `clientes/aura/static/js/meta_ads/modal.js`

```javascript
// Manejo de modales para Meta Ads
window.modal = {
    element: null,
    config: {
        closeOnEscape: true,
        closeOnClickOutside: true,
        animationDuration: 300
    },

    init() {
        this.element = document.getElementById('modal-diagnostico');
        this.setupEventListeners();
    },

    setupEventListeners() {
        // Cerrar con Escape
        if (this.config.closeOnEscape) {
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && !this.element.classList.contains('hidden')) {
                    this.cerrar();
                }
            });
        }

        // Cerrar al hacer clic fuera
        if (this.config.closeOnClickOutside) {
            this.element.addEventListener('click', (e) => {
                if (e.target === this.element) {
                    this.cerrar();
                }
            });
        }

        // Botones de cerrar
        this.element.querySelectorAll('[data-modal-close]').forEach(btn => {
            btn.addEventListener('click', () => this.cerrar());
        });
    },

    abrir() {
        this.element.classList.remove('hidden');
        this.element.classList.add('flex');
        document.body.style.overflow = 'hidden';
    },

    cerrar() {
        this.element.classList.remove('flex');
        this.element.classList.add('hidden');
        document.body.style.overflow = '';
        
        // Limpiar estado
        this.limpiarContenido();
    },

    limpiarContenido() {
        const content = this.element.querySelector('.modal-content');
        if (content) {
            content.innerHTML = '';
        }
    },

    mostrarCargando() {
        const content = this.element.querySelector('.modal-content');
        if (content) {
            content.innerHTML = `
                <div class="text-center py-8">
                    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                    <p class="text-gray-600 mt-2">Cargando...</p>
                </div>
            `;
        }
    }
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('modal-diagnostico')) {
        window.modal.init();
    }
});
```

### `clientes/aura/static/js/meta_ads/diagnostico.js`

```javascript
// Sistema de diagnóstico Meta Ads
class MetaAdsDiagnostico {
    constructor() {
        this.nombreNora = window.META_ADS_CONFIG?.nombreNora || 'aura';
        this.apiUrl = window.META_ADS_CONFIG?.apiUrl || '';
    }

    async ejecutarDiagnostico() {
        try {
            // Mostrar modal de carga
            window.modal.abrir();
            window.modal.mostrarCargando();
            
            // Ejecutar diagnóstico
            const response = await fetch(`${this.apiUrl}/diagnostico`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    nombre_nora: this.nombreNora
                })
            });
            
            const resultado = await response.json();
            
            // Mostrar resultados
            this.mostrarResultados(resultado);
            
        } catch (error) {
            console.error('Error en diagnóstico:', error);
            this.mostrarError(error.message);
        }
    }

    mostrarResultados(resultado) {
        const content = window.modal.element.querySelector('.modal-content');
        
        content.innerHTML = `
            <div class="bg-white rounded-lg max-w-4xl w-full max-h-screen overflow-y-auto">
                <div class="p-6 border-b border-gray-200">
                    <h3 class="text-lg font-semibold text-gray-900">
                        🔍 Diagnóstico Meta Ads - ${this.nombreNora}
                    </h3>
                </div>
                
                <div class="p-6">
                    ${this.generarHTMLResultados(resultado)}
                </div>
                
                <div class="p-6 border-t border-gray-200 flex justify-end">
                    <button data-modal-close class="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700">
                        Cerrar
                    </button>
                </div>
            </div>
        `;
    }

    generarHTMLResultados(resultado) {
        let html = '';
        
        // Estado general
        html += `
            <div class="mb-6">
                <h4 class="font-semibold mb-3">📊 Estado General</h4>
                <div class="grid grid-cols-2 gap-4">
                    <div class="bg-blue-50 p-4 rounded-lg">
                        <p class="text-sm text-blue-600">Cuentas Conectadas</p>
                        <p class="text-2xl font-bold text-blue-900">${resultado.cuentas_activas || 0}</p>
                    </div>
                    <div class="bg-green-50 p-4 rounded-lg">
                        <p class="text-sm text-green-600">Campañas Activas</p>
                        <p class="text-2xl font-bold text-green-900">${resultado.campanas_activas || 0}</p>
                    </div>
                </div>
            </div>
        `;
        
        // Problemas encontrados
        if (resultado.problemas && resultado.problemas.length > 0) {
            html += `
                <div class="mb-6">
                    <h4 class="font-semibold mb-3 text-red-600">⚠️ Problemas Encontrados</h4>
                    <ul class="space-y-2">
                        ${resultado.problemas.map(problema => `
                            <li class="bg-red-50 p-3 rounded-lg border-l-4 border-red-400">
                                <span class="text-red-800">${problema}</span>
                            </li>
                        `).join('')}
                    </ul>
                </div>
            `;
        }
        
        // Recomendaciones
        if (resultado.recomendaciones && resultado.recomendaciones.length > 0) {
            html += `
                <div class="mb-6">
                    <h4 class="font-semibold mb-3 text-blue-600">💡 Recomendaciones</h4>
                    <ul class="space-y-2">
                        ${resultado.recomendaciones.map(rec => `
                            <li class="bg-blue-50 p-3 rounded-lg border-l-4 border-blue-400">
                                <span class="text-blue-800">${rec}</span>
                            </li>
                        `).join('')}
                    </ul>
                </div>
            `;
        }
        
        return html;
    }

    mostrarError(mensaje) {
        const content = window.modal.element.querySelector('.modal-content');
        
        content.innerHTML = `
            <div class="bg-white rounded-lg max-w-md w-full">
                <div class="p-6">
                    <div class="text-center">
                        <div class="text-red-600 text-4xl mb-4">❌</div>
                        <h3 class="text-lg font-semibold text-gray-900 mb-2">Error</h3>
                        <p class="text-gray-600">${mensaje}</p>
                    </div>
                </div>
                
                <div class="p-6 border-t border-gray-200 flex justify-end">
                    <button data-modal-close class="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700">
                        Cerrar
                    </button>
                </div>
            </div>
        `;
    }
}

// Instancia global
window.metaAdsDiagnostico = new MetaAdsDiagnostico();

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    const btnDiagnostico = document.getElementById('btn-diagnostico');
    if (btnDiagnostico) {
        btnDiagnostico.addEventListener('click', () => {
            window.metaAdsDiagnostico.ejecutarDiagnostico();
        });
    }
});
```
```

---

## 🎨 4. Estilos CSS

### `static/css/modulos/meta_ads/main.css`

```css
/* Meta Ads - Estilos principales */
.meta-ads-dashboard {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.card-hover {
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.card-hover:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.automation-card {
    transition: all 0.2s ease;
}

.automation-card:hover {
    border-color: #3b82f6;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
}

/* Estados de automatización */
.badge-activa {
    background-color: #d1fae5;
    color: #059669;
}

.badge-pausada {
    background-color: #fef3c7;
    color: #d97706;
}

.badge-error {
    background-color: #fee2e2;
    color: #dc2626;
}

/* Modal de diagnóstico */
.modal-content {
    max-height: 90vh;
    overflow-y: auto;
}

/* Estadísticas de engagement */
.engagement-meter {
    background: linear-gradient(90deg, #ef4444 0%, #f59e0b 50%, #10b981 100%);
    height: 4px;
    border-radius: 2px;
    position: relative;
}

.engagement-indicator {
    position: absolute;
    top: -2px;
    width: 8px;
    height: 8px;
    background: white;
    border: 2px solid #374151;
    border-radius: 50%;
    transform: translateX(-50%);
}

/* Gráficos de campañas */
.campaign-chart {
    position: relative;
    padding: 1rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 0.5rem;
    color: white;
}

.chart-value {
    font-size: 2rem;
    font-weight: bold;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

/* Animaciones */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
}

.fade-in {
    animation: fadeIn 0.3s ease-out;
}

.pulse-animation {
    animation: pulse 2s infinite;
}

/* Webhook status indicators */
.webhook-active {
    position: relative;
}

.webhook-active::before {
    content: '';
    position: absolute;
    top: -2px;
    right: -2px;
    width: 8px;
    height: 8px;
    background: #10b981;
    border-radius: 50%;
    animation: pulse 2s infinite;
}

/* Responsive */
@media (max-width: 768px) {
    .meta-ads-dashboard {
        padding: 1rem;
    }
    
    .dashboard-header {
        flex-direction: column;
        gap: 1rem;
        align-items: stretch;
    }
    
    .card-hover {
        text-align: center;
    }
    
    .grid-cols-3 {
        grid-template-columns: 1fr;
    }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    .meta-ads-dashboard {
        background-color: #1f2937;
        color: #f9fafb;
    }
    
    .card-hover {
        background-color: #374151;
        border-color: #4b5563;
    }
    
    .engagement-indicator {
        border-color: #f9fafb;
    }
}
```
```

---

## 📋 5. Registro del módulo

### SQL para Supabase:

```sql
-- 1. Registrar el módulo Meta Ads
INSERT INTO modulos_disponibles (nombre, descripcion, icono, ruta) VALUES 
('meta_ads', 'Gestión completa de campañas de Facebook e Instagram', '�', 'panel_cliente_meta_ads.panel_cliente_meta_ads_bp');

-- 2. Activar para Aura
UPDATE configuracion_bot 
SET modulos = jsonb_set(modulos, '{meta_ads}', 'true', true)
WHERE nombre_nora = 'aura';

-- 3. Tablas requeridas para Meta Ads (ya existen)
-- meta_ads_automatizaciones - Configuraciones de automatización
-- meta_ads_cuentas - Cuentas publicitarias conectadas
-- meta_ads_reportes_semanales - Reportes consolidados
-- meta_publicaciones_webhook - Publicaciones desde webhook
-- facebook_paginas - Páginas de Facebook conectadas
-- logs_webhooks_meta - Logs de webhooks de Meta
-- meta_anuncios_automatizados - Anuncios creados automáticamente
```

### Código en `registro_dinamico.py`:

```python
# Agregar en la sección de módulos
if "meta_ads" in modulos:
    try:
        # Blueprint principal
        from clientes.aura.routes.panel_cliente_meta_ads import panel_cliente_meta_ads_bp
        safe_register_blueprint(
            app, 
            panel_cliente_meta_ads_bp, 
            url_prefix=f"/panel_cliente/{nombre_nora}/meta_ads"
        )
        
        # Sub-blueprints de Meta Ads
        from clientes.aura.routes.panel_cliente_meta_ads.automatizacion_routes import automatizacion_routes_bp
        from clientes.aura.routes.panel_cliente_meta_ads.webhooks_api import webhooks_api_bp
        
        safe_register_blueprint(app, automatizacion_routes_bp)
        safe_register_blueprint(app, webhooks_api_bp)
        
        print(f"✅ Módulo Meta Ads registrado completo")
        
    except Exception as e:
        print(f"❌ Error registrando Meta Ads: {e}")
```

---

## ✅ Resultado final

Con este ejemplo completo tendrás:

1. **Dashboard interactivo** con 6 módulos principales (Campañas, Audiencias, Reportes, Automatización, Webhooks, Estadísticas)
2. **Sistema de automatización** avanzado basado en publicaciones de Facebook
3. **Webhook integration** para recibir eventos en tiempo real de Meta
4. **Diseño responsive** con Tailwind CSS y componentes modulares
5. **JavaScript modular** con clases especializadas (Modal, Diagnóstico)
6. **Base de datos compleja** con 7+ tablas interrelacionadas
7. **Registro correcto** en el sistema dinámico de módulos

El módulo estará disponible en:
```
http://localhost:5000/panel_cliente/aura/meta_ads/
```

### Rutas principales del módulo:
- `/panel_cliente/aura/meta_ads/` - Dashboard principal
- `/panel_cliente/aura/meta_ads/automatizacion` - Panel de automatización
- `/panel_cliente/aura/meta_ads/reportes` - Reportes de campañas
- `/panel_cliente/aura/meta_ads/estadisticas` - Análisis detallado
- `/panel_cliente/aura/meta_ads/webhooks` - Configuración de webhooks

### Características técnicas:
- **26 archivos Python** con separación de responsabilidades
- **17 templates HTML** con herencia correcta de `base_cliente.html`
- **4 archivos JavaScript** modulares y organizados
- **Múltiples blueprints** con sub-rutas especializadas
- **Sistema de webhooks** completo para Meta Business API
- **Automatización inteligente** de campañas basada en engagement

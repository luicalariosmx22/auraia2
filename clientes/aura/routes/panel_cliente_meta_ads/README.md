# Módulo: meta_ads

## Descripción
Consulta y recibe reportes automáticos de tus campañas en Meta Ads.

## Estado del Módulo
| Componente | Estado |
|------------|---------|
| HTTP Status | ✅ 200 |
| Backend | ✅ |
| Blueprint | ✅ panel_cliente_meta_ads_bp |
| Templates | ✅ |
| Supabase | ✅ |

## Endpoints
| Ruta | Función | Blueprint |
|------|----------|-----------|
| /config | guardar_config_reportes | panel_cliente_meta_ads_bp |
| /reportes/<uuid> | descargar_reporte_semanal_panel | panel_cliente_meta_ads_bp |
| /estadisticas | vista_estadisticas_ads | panel_cliente_meta_ads_bp |
| / | panel_cliente_meta_ads | panel_cliente_meta_ads_bp |
| /reportes-interno | vista_reportes_meta_ads_interno | panel_cliente_meta_ads_bp |
| /reportes/<reporte_id> | detalle_reporte_ads | panel_cliente_meta_ads_bp |
| /cuentas_publicitarias | vista_cuentas_publicitarias | panel_cliente_meta_ads_bp |
| /cuentas_publicitarias/importar_desde_meta | importar_cuentas_desde_meta | panel_cliente_meta_ads_bp |
| /campañas_activas | campañas_activas | panel_cliente_meta_ads_bp |
| /lab | vista_lab_meta_ads | panel_cliente_meta_ads_bp |
| /agregar_cuenta | agregar_cuenta | panel_cliente_meta_ads_bp |
| /campanas | vista_campanas | panel_cliente_meta_ads_bp |
| /campanas_activas_meta_ads | campanas_activas_meta_ads | panel_cliente_meta_ads_bp |
| /cuentas_publicitarias/actualizar | actualizar_cuentas_publicitarias | panel_cliente_meta_ads_bp |
| /meta_ads/anuncios_activos_json | anuncios_activos_json | panel_cliente_meta_ads_bp |
| /cuentas_publicitarias/<cuenta_id>/vincular_empresa | vincular_empresa_a_cuenta | panel_cliente_meta_ads_bp |
| /cuentas_publicitarias/<cuenta_id>/ads_activos | obtener_ads_activos_endpoint | panel_cliente_meta_ads_bp |
| /cuenta/<cuenta_id> | ficha_cuenta_publicitaria | panel_cliente_meta_ads_bp |
| /cuentas_publicitarias/<cuenta_id>/test_conexion | test_conexion_cuenta | panel_cliente_meta_ads_bp |
| /reportes | vista_reportes_meta_ads | panel_cliente_meta_ads_bp |
| /prereportes/eliminar | eliminar_prereporte | panel_cliente_meta_ads_bp |
| /sincronizar-semanal | vista_sincronizacion_semanal | panel_cliente_meta_ads_bp |
| /reportes/reporte/<uuid> | ver_reporte_meta_ads | panel_cliente_meta_ads_bp |
| /dashboard | vista_meta_ads | panel_cliente_meta_ads_bp |
| /vista_sincronizacion | vista_sincronizacion | vista_sincronizacion_bp |
| /obtener_estado | obtener_estado | vista_sincronizacion_bp |
| /ultimas_sincronizaciones | ultimas_sincronizaciones | vista_sincronizacion_bp |

## Templates
| Template | Existe |
|----------|---------|
| panel_cliente_meta_ads/index.html | ✅ |
| panel_cliente_meta_ads/reportes.html | ✅ |
| panel_cliente_meta_ads/detalle_reporte_ads.html | ✅ |
| panel_cliente_meta_ads/cuentas_publicitarias.html | ✅ |
| panel_cliente_meta_ads/lab.html | ✅ |
| campanas_meta_ads.html | ✅ |
| campanas_activas_meta_ads.html | ✅ |
| vincular_empresa_cuenta.html | ✅ |
| vincular_empresa_cuenta.html | ✅ |

## Variables Template
| Variable | Tipo |
|----------|------|
| anuncios | Custom |
| campanas | Custom |
| conjuntos | Custom |
| cuenta | Custom |
| cuenta_id | Custom |
| cuentas | Custom |
| empresas | Custom |
| error | Custom |
| nombre_nora | Sistema |
| reporte | Custom |
| reportes | Custom |

## Tablas Supabase
| Tabla | Columnas |
|-------|----------|
| cliente_empresas | id, nombre_nora, nombre_empresa, giro, razon_social... |
| meta_ads_anuncios_detalle | id, ad_id, nombre_anuncio, importe_gastado, id_cuenta_publicitaria... |
| meta_ads_campañas |  |
| meta_ads_conjuntos_anuncios |  |
| meta_ads_cuentas | id, id_cuenta_publicitaria, nombre_cliente, nombre_visible, conectada... |
| meta_ads_reportes_semanales | id, empresa_id, id_cuenta_publicitaria, fecha_inicio, fecha_fin... |
| meta_ads_sync_log | ❌ Error al consultar |

## Buenas Prácticas
✅ Implementa nombre_nora en rutas
✅ Manejo de excepciones implementado

---
Archivo generado automáticamente por diagnostico_modulo.py (versión Sayayin)
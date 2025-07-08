-- Datos de ejemplo para las asociaciones de cuentas de Google Ads con empresas
-- Este script asume que ya existen las empresas en la tabla cliente_empresas

-- Verificar si las empresas existen (puedes ejecutar esto primero para verificar)
-- SELECT id, nombre_nora, nombre_empresa FROM cliente_empresas WHERE nombre_nora = 'aura';

-- Insertar asociaciones de las 7 cuentas principales
-- NOTA: Reemplaza los UUIDs de empresa_id con los IDs reales de tu tabla cliente_empresas

INSERT INTO google_ads_cuentas_empresas (
    customer_id, 
    empresa_id, 
    nombre_cuenta, 
    activa, 
    moneda, 
    zona_horaria, 
    es_test, 
    accesible, 
    problema
) VALUES 
-- LaReina Pasteleria
('3700518858', 
 (SELECT id FROM cliente_empresas WHERE nombre_empresa = 'LaReina Pasteleria' AND nombre_nora = 'aura' LIMIT 1), 
 'LaReinaPasteleria', 
 true, 
 'MXN', 
 'America/Mexico_City', 
 false, 
 true, 
 NULL),

-- Musicando
('1785583613', 
 (SELECT id FROM cliente_empresas WHERE nombre_empresa = 'Musicando' AND nombre_nora = 'aura' LIMIT 1), 
 'Musicando', 
 true, 
 'MXN', 
 'America/Mexico_City', 
 false, 
 true, 
 NULL),

-- RIMS 2
('4890270350', 
 (SELECT id FROM cliente_empresas WHERE nombre_empresa = 'RIMS 2' AND nombre_nora = 'aura' LIMIT 1), 
 'RIMS 2', 
 true, 
 'MXN', 
 'America/Mexico_City', 
 false, 
 true, 
 NULL),

-- SAL DE JADE
('9737121597', 
 (SELECT id FROM cliente_empresas WHERE nombre_empresa = 'SAL DE JADE' AND nombre_nora = 'aura' LIMIT 1), 
 'SAL DE JADE', 
 true, 
 'MXN', 
 'America/Mexico_City', 
 false, 
 true, 
 NULL),

-- Suspiros Cakes
('7605115009', 
 (SELECT id FROM cliente_empresas WHERE nombre_empresa = 'Suspiros Cakes' AND nombre_nora = 'aura' LIMIT 1), 
 'Suspiros Cakes', 
 true, 
 'MXN', 
 'America/Mexico_City', 
 false, 
 true, 
 NULL),

-- Suspiros Pastelerías
('1554994188', 
 (SELECT id FROM cliente_empresas WHERE nombre_empresa = 'Suspiros Pastelerías' AND nombre_nora = 'aura' LIMIT 1), 
 'Suspiros Pastelerías', 
 true, 
 'MXN', 
 'America/Mexico_City', 
 false, 
 true, 
 NULL),

-- Vetervan
('5291123262', 
 (SELECT id FROM cliente_empresas WHERE nombre_empresa = 'Vetervan' AND nombre_nora = 'aura' LIMIT 1), 
 'Vetervan', 
 true, 
 'MXN', 
 'America/Mexico_City', 
 false, 
 true, 
 NULL)

ON CONFLICT (customer_id) DO UPDATE SET
    empresa_id = EXCLUDED.empresa_id,
    nombre_cuenta = EXCLUDED.nombre_cuenta,
    fecha_ultima_actualizacion = NOW(),
    updated_at = NOW();

-- Verificar las inserciones
SELECT 
    gace.customer_id,
    gace.nombre_cuenta,
    ce.nombre_empresa,
    ce.nombre_nora,
    gace.accesible,
    gace.problema
FROM google_ads_cuentas_empresas gace
JOIN cliente_empresas ce ON gace.empresa_id = ce.id
WHERE ce.nombre_nora = 'aura'
ORDER BY gace.nombre_cuenta;

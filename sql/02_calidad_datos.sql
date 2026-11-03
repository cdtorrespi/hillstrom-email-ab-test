-- Revisiones de calidad antes de cualquier análisis.

-- 1. Total de filas y nulos en columnas clave (deben ser 64,000 y 0)
SELECT
    COUNT(*)                                        AS filas,
    SUM(CASE WHEN recency    IS NULL THEN 1 ELSE 0 END) AS nulos_recency,
    SUM(CASE WHEN history    IS NULL THEN 1 ELSE 0 END) AS nulos_history,
    SUM(CASE WHEN segment    IS NULL THEN 1 ELSE 0 END) AS nulos_segment,
    SUM(CASE WHEN spend      IS NULL THEN 1 ELSE 0 END) AS nulos_spend
FROM clientes;

-- 2. Valores distintos de las variables categóricas
SELECT 'zip_code' AS variable, zip_code AS valor, COUNT(*) AS clientes FROM clientes GROUP BY zip_code
UNION ALL
SELECT 'channel', channel, COUNT(*) FROM clientes GROUP BY channel
UNION ALL
SELECT 'segment', segment, COUNT(*) FROM clientes GROUP BY segment
ORDER BY variable, clientes DESC;

-- 3. Consistencia del embudo: no puede haber compra sin visita ni gasto sin compra
SELECT
    SUM(CASE WHEN conversion = 1 AND visit = 0      THEN 1 ELSE 0 END) AS compra_sin_visita,
    SUM(CASE WHEN spend > 0      AND conversion = 0 THEN 1 ELSE 0 END) AS gasto_sin_compra,
    SUM(CASE WHEN conversion = 1 AND spend = 0      THEN 1 ELSE 0 END) AS compra_sin_gasto
FROM clientes;

-- 4. Clientes que no compraron ni de hombre ni de mujer en el último año
SELECT COUNT(*) AS sin_categoria
FROM clientes
WHERE mens = 0 AND womens = 0;

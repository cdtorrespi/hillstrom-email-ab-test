-- Exploración inicial por grupo del experimento.

-- 1. Tamaño de cada grupo y su participación (se espera ~1/3 cada uno)
SELECT
    grupo,
    COUNT(*)                                                    AS clientes,
    ROUND(CAST(COUNT(*) * 1.0 / SUM(COUNT(*)) OVER () AS NUMERIC), 4) AS participacion
FROM clientes
GROUP BY grupo
ORDER BY grupo;

-- 2. Métricas de resultado por grupo
SELECT
    grupo,
    COUNT(*)                                             AS clientes,
    ROUND(CAST(AVG(visit)      AS NUMERIC), 4)           AS tasa_visita,
    ROUND(CAST(AVG(conversion) AS NUMERIC), 4)           AS tasa_conversion,
    ROUND(CAST(AVG(spend)      AS NUMERIC), 3)           AS ingreso_por_cliente,
    ROUND(CAST(SUM(spend)      AS NUMERIC), 2)           AS ingreso_total
FROM clientes
GROUP BY grupo
ORDER BY grupo;

-- 3. Ticket promedio entre quienes compraron (descriptivo: es un grupo posterior al tratamiento)
SELECT
    grupo,
    COUNT(*)                                  AS compradores,
    ROUND(CAST(AVG(spend) AS NUMERIC), 2)     AS ticket_promedio,
    ROUND(CAST(MAX(spend) AS NUMERIC), 2)     AS ticket_maximo
FROM clientes
WHERE conversion = 1
GROUP BY grupo
ORDER BY grupo;

-- 4. Balance de covariables previas al experimento por grupo
SELECT
    grupo,
    ROUND(CAST(AVG(recency) AS NUMERIC), 3)                                   AS recency_prom,
    ROUND(CAST(AVG(history) AS NUMERIC), 2)                                   AS history_prom,
    ROUND(CAST(AVG(mens)    AS NUMERIC), 4)                                   AS pct_mens,
    ROUND(CAST(AVG(womens)  AS NUMERIC), 4)                                   AS pct_womens,
    ROUND(CAST(AVG(newbie)  AS NUMERIC), 4)                                   AS pct_newbie,
    ROUND(CAST(AVG(CASE WHEN channel = 'Web'   THEN 1 ELSE 0 END) AS NUMERIC), 4) AS pct_web,
    ROUND(CAST(AVG(CASE WHEN zip_code = 'Urban' THEN 1 ELSE 0 END) AS NUMERIC), 4) AS pct_urban
FROM clientes
GROUP BY grupo
ORDER BY grupo;

-- 5. Ingreso por cliente por grupo y canal de compra (primer vistazo a segmentos)
SELECT
    channel,
    grupo,
    COUNT(*)                                   AS clientes,
    ROUND(CAST(AVG(spend) AS NUMERIC), 3)      AS ingreso_por_cliente
FROM clientes
GROUP BY channel, grupo
ORDER BY channel, grupo;

-- 6. Distribución del gasto entre compradores (percentiles con percentile_cont)
SELECT
    grupo,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY spend) AS p50,
    PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY spend) AS p90,
    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY spend) AS p99
FROM clientes
WHERE conversion = 1
GROUP BY grupo
ORDER BY grupo;

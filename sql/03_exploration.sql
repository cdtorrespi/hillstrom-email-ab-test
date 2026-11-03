-- First look at the data by experiment group.

-- 1. Size and share of each group (about 1/3 each is expected)
SELECT
    grp,
    COUNT(*)                                                    AS customers,
    ROUND(CAST(COUNT(*) * 1.0 / SUM(COUNT(*)) OVER () AS NUMERIC), 4) AS share
FROM customers
GROUP BY grp
ORDER BY grp;

-- 2. Outcome metrics by group
SELECT
    grp,
    COUNT(*)                                             AS customers,
    ROUND(CAST(AVG(visit)      AS NUMERIC), 4)           AS visit_rate,
    ROUND(CAST(AVG(conversion) AS NUMERIC), 4)           AS conversion_rate,
    ROUND(CAST(AVG(spend)      AS NUMERIC), 3)           AS revenue_per_customer,
    ROUND(CAST(SUM(spend)      AS NUMERIC), 2)           AS total_revenue
FROM customers
GROUP BY grp
ORDER BY grp;

-- 3. Average order value among buyers (descriptive: buyers are a post-treatment group)
SELECT
    grp,
    COUNT(*)                                  AS buyers,
    ROUND(CAST(AVG(spend) AS NUMERIC), 2)     AS avg_order_value,
    ROUND(CAST(MAX(spend) AS NUMERIC), 2)     AS max_order_value
FROM customers
WHERE conversion = 1
GROUP BY grp
ORDER BY grp;

-- 4. Balance of pre-experiment covariates by group
SELECT
    grp,
    ROUND(CAST(AVG(recency) AS NUMERIC), 3)                                   AS avg_recency,
    ROUND(CAST(AVG(history) AS NUMERIC), 2)                                   AS avg_history,
    ROUND(CAST(AVG(mens)    AS NUMERIC), 4)                                   AS pct_mens,
    ROUND(CAST(AVG(womens)  AS NUMERIC), 4)                                   AS pct_womens,
    ROUND(CAST(AVG(newbie)  AS NUMERIC), 4)                                   AS pct_newbie,
    ROUND(CAST(AVG(CASE WHEN channel = 'Web'   THEN 1 ELSE 0 END) AS NUMERIC), 4) AS pct_web,
    ROUND(CAST(AVG(CASE WHEN zip_code = 'Urban' THEN 1 ELSE 0 END) AS NUMERIC), 4) AS pct_urban
FROM customers
GROUP BY grp
ORDER BY grp;

-- 5. Revenue per customer by group and purchase channel (first look at segments)
SELECT
    channel,
    grp,
    COUNT(*)                                   AS customers,
    ROUND(CAST(AVG(spend) AS NUMERIC), 3)      AS revenue_per_customer
FROM customers
GROUP BY channel, grp
ORDER BY channel, grp;

-- 6. Spend distribution among buyers (percentiles with percentile_cont)
SELECT
    grp,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY spend) AS p50,
    PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY spend) AS p90,
    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY spend) AS p99
FROM customers
WHERE conversion = 1
GROUP BY grp
ORDER BY grp;

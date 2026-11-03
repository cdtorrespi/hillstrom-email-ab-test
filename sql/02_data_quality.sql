-- Quality checks before any analysis.

-- 1. Row count and nulls in key columns (should be 64,000 and 0)
SELECT
    COUNT(*)                                            AS row_count,
    SUM(CASE WHEN recency    IS NULL THEN 1 ELSE 0 END) AS null_recency,
    SUM(CASE WHEN history    IS NULL THEN 1 ELSE 0 END) AS null_history,
    SUM(CASE WHEN segment    IS NULL THEN 1 ELSE 0 END) AS null_segment,
    SUM(CASE WHEN spend      IS NULL THEN 1 ELSE 0 END) AS null_spend
FROM customers;

-- 2. Distinct values of the categorical variables
SELECT 'zip_code' AS variable, zip_code AS value, COUNT(*) AS customers FROM customers GROUP BY zip_code
UNION ALL
SELECT 'channel', channel, COUNT(*) FROM customers GROUP BY channel
UNION ALL
SELECT 'segment', segment, COUNT(*) FROM customers GROUP BY segment
ORDER BY variable, customers DESC;

-- 3. Funnel consistency: no purchase without a visit and no spend without a purchase
SELECT
    SUM(CASE WHEN conversion = 1 AND visit = 0      THEN 1 ELSE 0 END) AS purchase_without_visit,
    SUM(CASE WHEN spend > 0      AND conversion = 0 THEN 1 ELSE 0 END) AS spend_without_purchase,
    SUM(CASE WHEN conversion = 1 AND spend = 0      THEN 1 ELSE 0 END) AS purchase_without_spend
FROM customers;

-- 4. Customers who bought neither men's nor women's merchandise in the past year
SELECT COUNT(*) AS no_category
FROM customers
WHERE mens = 0 AND womens = 0;

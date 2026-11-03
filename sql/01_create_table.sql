-- Schema and load of the Hillstrom dataset in PostgreSQL.
-- Usage (from the repo root):
--   psql -d hillstrom -f sql/01_create_table.sql

DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id      SERIAL PRIMARY KEY,
    recency          SMALLINT     NOT NULL CHECK (recency BETWEEN 1 AND 12),  -- months since last purchase
    history_segment  VARCHAR(20)  NOT NULL,                                   -- spend bracket in the past year
    history          NUMERIC(8,2) NOT NULL CHECK (history >= 0),              -- spend in the past year (USD)
    mens             SMALLINT     NOT NULL CHECK (mens IN (0, 1)),            -- bought men's merchandise
    womens           SMALLINT     NOT NULL CHECK (womens IN (0, 1)),          -- bought women's merchandise
    zip_code         VARCHAR(10)  NOT NULL,                                   -- Urban / Surburban / Rural
    newbie           SMALLINT     NOT NULL CHECK (newbie IN (0, 1)),          -- new customer in the past 12 months
    channel          VARCHAR(15)  NOT NULL,                                   -- Phone / Web / Multichannel
    segment          VARCHAR(15)  NOT NULL,                                   -- group assigned in the experiment
    visit            SMALLINT     NOT NULL CHECK (visit IN (0, 1)),
    conversion       SMALLINT     NOT NULL CHECK (conversion IN (0, 1)),
    spend            NUMERIC(8,2) NOT NULL CHECK (spend >= 0)
);

\copy customers (recency, history_segment, history, mens, womens, zip_code, newbie, channel, segment, visit, conversion, spend) FROM 'data/raw/hillstrom.csv' WITH (FORMAT csv, HEADER true)

-- Shorter group names for the analysis
ALTER TABLE customers ADD COLUMN grp VARCHAR(10);
UPDATE customers
SET grp = CASE segment
              WHEN 'No E-Mail'     THEN 'Control'
              WHEN 'Mens E-Mail'   THEN 'Mens'
              WHEN 'Womens E-Mail' THEN 'Womens'
          END;
ALTER TABLE customers ALTER COLUMN grp SET NOT NULL;

CREATE INDEX idx_customers_grp ON customers (grp);

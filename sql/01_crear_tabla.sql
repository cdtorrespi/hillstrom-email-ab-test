-- Esquema y carga del dataset de Hillstrom en PostgreSQL.
-- Uso (desde la raíz del repo):
--   psql -d hillstrom -f sql/01_crear_tabla.sql

DROP TABLE IF EXISTS clientes;

CREATE TABLE clientes (
    cliente_id       SERIAL PRIMARY KEY,
    recency          SMALLINT     NOT NULL CHECK (recency BETWEEN 1 AND 12),  -- meses desde la última compra
    history_segment  VARCHAR(20)  NOT NULL,                                   -- rango de gasto del último año
    history          NUMERIC(8,2) NOT NULL CHECK (history >= 0),              -- gasto del último año (USD)
    mens             SMALLINT     NOT NULL CHECK (mens IN (0, 1)),            -- compró mercancía de hombre
    womens           SMALLINT     NOT NULL CHECK (womens IN (0, 1)),          -- compró mercancía de mujer
    zip_code         VARCHAR(10)  NOT NULL,                                   -- Urban / Surburban / Rural
    newbie           SMALLINT     NOT NULL CHECK (newbie IN (0, 1)),          -- cliente nuevo en los últimos 12 meses
    channel          VARCHAR(15)  NOT NULL,                                   -- Phone / Web / Multichannel
    segment          VARCHAR(15)  NOT NULL,                                   -- grupo asignado en el experimento
    visit            SMALLINT     NOT NULL CHECK (visit IN (0, 1)),
    conversion       SMALLINT     NOT NULL CHECK (conversion IN (0, 1)),
    spend            NUMERIC(8,2) NOT NULL CHECK (spend >= 0)
);

\copy clientes (recency, history_segment, history, mens, womens, zip_code, newbie, channel, segment, visit, conversion, spend) FROM 'data/raw/hillstrom.csv' WITH (FORMAT csv, HEADER true)

-- Nombres de grupo más cortos para el análisis
ALTER TABLE clientes ADD COLUMN grupo VARCHAR(10);
UPDATE clientes
SET grupo = CASE segment
                WHEN 'No E-Mail'     THEN 'Control'
                WHEN 'Mens E-Mail'   THEN 'Hombre'
                WHEN 'Womens E-Mail' THEN 'Mujer'
            END;
ALTER TABLE clientes ALTER COLUMN grupo SET NOT NULL;

CREATE INDEX idx_clientes_grupo ON clientes (grupo);

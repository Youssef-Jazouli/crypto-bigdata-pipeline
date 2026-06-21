-- 1. Création de la Base de Données et du Schéma
CREATE OR REPLACE DATABASE CRYPTO_DB;
CREATE OR REPLACE SCHEMA CRYPTO_DB.GOLD_LAYER;

-- 2. Création de la table de Dimension (DIM_CRYPTO)
CREATE OR REPLACE TABLE CRYPTO_DB.GOLD_LAYER.DIM_CRYPTO (
    id VARCHAR(100) PRIMARY KEY,
    symbol VARCHAR(20),
    name VARCHAR(100),
    market_cap_rank INT
);

-- 3. Création de la table de Faits (FACT_METRICS)
CREATE OR REPLACE TABLE CRYPTO_DB.GOLD_LAYER.FACT_METRICS (
    id VARCHAR(100),
    current_price NUMBER(38, 8),
    market_cap NUMBER(38, 2),
    total_volume NUMBER(38, 2),
    high_24h NUMBER(38, 8),
    low_24h NUMBER(38, 8),
    price_change_24h NUMBER(38, 8),
    price_change_percentage_24h NUMBER(38, 5),
    last_updated TIMESTAMP_NTZ,
    processed_at TIMESTAMP_NTZ
);
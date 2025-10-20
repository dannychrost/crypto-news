-- -------------------------------------------------------------
-- Crypto Panic News
-- -------------------------------------------------------------

-- Main table for storing crypto news data
CREATE TABLE IF NOT EXISTS news_items (
    id SERIAL PRIMARY KEY,
    external_id INTEGER UNIQUE NOT NULL,  -- API 'id' field
    slug VARCHAR(255),
    title TEXT NOT NULL,
    description TEXT,
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE,
    kind VARCHAR(50)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_news_external_id ON news_items(external_id);
CREATE INDEX IF NOT EXISTS idx_news_published_at ON news_items(published_at);
CREATE INDEX IF NOT EXISTS idx_news_created_at ON news_items(created_at);
CREATE INDEX IF NOT EXISTS idx_news_kind ON news_items(kind);

-- Create a simple view for easy querying
CREATE OR REPLACE VIEW recent_news AS
SELECT 
    id,
    external_id,
    slug,
    title,
    description,
    published_at,
    created_at,
    kind
FROM news_items
ORDER BY published_at DESC;

-- -------------------------------------------------------------
-- CoinMarketCap Fear and Greed Index
-- -------------------------------------------------------------

-- Create ENUM type for classification if it doesn't already exist
DO $$ BEGIN
    CREATE TYPE fng_classification AS ENUM (
        'Extreme Fear',
        'Fear',
        'Neutral',
        'Greed',
        'Extreme Greed'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

-- Main table for storing daily Fear & Greed Index values
CREATE TABLE IF NOT EXISTS fear_and_greed_index (
    id SERIAL PRIMARY KEY,
    timestamp_utc TIMESTAMP WITH TIME ZONE NOT NULL,         -- 00:00 UTC daily timestamp from API
    value SMALLINT NOT NULL CHECK (value BETWEEN 0 AND 100), -- Fear & Greed numeric score (0–100)
    value_classification fng_classification NOT NULL         -- Category derived from value range
);

-- Prevent duplicate entries for the same day
CREATE UNIQUE INDEX IF NOT EXISTS idx_fng_timestamp_utc
ON fear_and_greed_index(timestamp_utc);

-- Optional view for quickly checking recent values
CREATE OR REPLACE VIEW recent_fear_and_greed AS
SELECT 
    timestamp_utc,
    value,
    value_classification
FROM fear_and_greed_index
ORDER BY timestamp_utc DESC;
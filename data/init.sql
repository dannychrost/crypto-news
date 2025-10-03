-- Initialize database for crypto news bot (Free Tier)
-- Schema matches ONLY the fields present in API response

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

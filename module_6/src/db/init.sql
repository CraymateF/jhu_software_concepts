-- Schema initialization for GradCafe database
-- This file is automatically run by PostgreSQL on first start

CREATE TABLE IF NOT EXISTS gradcafe_main (
    p_id                    SERIAL PRIMARY KEY,
    program                 TEXT,
    comments                TEXT,
    date_added              DATE,
    url                     TEXT UNIQUE,
    status                  TEXT,
    term                    TEXT,
    us_or_international     TEXT,
    gpa                     FLOAT,
    gre                     FLOAT,
    gre_v                   FLOAT,
    gre_aw                  FLOAT,
    degree                  TEXT,
    llm_generated_program   TEXT,
    llm_generated_university TEXT,
    raw_data                JSONB
);

-- Watermark table for idempotent incremental scraping
CREATE TABLE IF NOT EXISTS ingestion_watermarks (
    source      TEXT PRIMARY KEY,
    last_seen   TEXT,
    updated_at  TIMESTAMPTZ DEFAULT now()
);

-- Index for efficient URL-based duplicate checks
CREATE INDEX IF NOT EXISTS idx_gradcafe_url ON gradcafe_main (url);
-- Index for date-based watermark queries
CREATE INDEX IF NOT EXISTS idx_gradcafe_date ON gradcafe_main (date_added);

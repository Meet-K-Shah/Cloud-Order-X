-- CloudOrderX — PostgreSQL initialization script
-- This runs automatically when the postgres container first starts.

-- Create analytics schema for ETL service
CREATE SCHEMA IF NOT EXISTS analytics;

-- Ensure the app user has access
GRANT ALL PRIVILEGES ON DATABASE cloudorderx TO cloudorderx;
GRANT ALL PRIVILEGES ON SCHEMA public    TO cloudorderx;
GRANT ALL PRIVILEGES ON SCHEMA analytics TO cloudorderx;

-- Useful extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

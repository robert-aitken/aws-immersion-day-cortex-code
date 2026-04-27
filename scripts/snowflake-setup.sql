-- =============================================================================
-- Snowflake Setup Script — CoCo Workshop
-- =============================================================================
-- Creates all Snowflake objects required for the AI-Accelerated Data
-- Engineering Immersion Day. This script is idempotent (safe to re-run).
--
-- Prerequisites:
--   - You must be connected as a user with ACCOUNTADMIN or SYSADMIN + SECURITYADMIN
--   - Run via: snow sql -c DEMO -f scripts/snowflake-setup.sql
--         or: cortex -c DEMO  →  "Run the setup script at scripts/snowflake-setup.sql"
-- =============================================================================

-- Use a role with sufficient privileges to create objects
USE ROLE ACCOUNTADMIN;

-- -------------------------------------------------------------------------
-- 1. Role
-- -------------------------------------------------------------------------
CREATE ROLE IF NOT EXISTS COCO_WORKSHOP_ROLE
  COMMENT = 'Workshop role for the CoCo AI-Accelerated Data Engineering lab';

-- Grant the role to the current user so they can switch to it
BEGIN
  LET usr VARCHAR := CURRENT_USER();
  EXECUTE IMMEDIATE 'GRANT ROLE COCO_WORKSHOP_ROLE TO USER ' || :usr;
END;

-- -------------------------------------------------------------------------
-- 2. Warehouse
-- -------------------------------------------------------------------------
CREATE WAREHOUSE IF NOT EXISTS COCO_WORKSHOP_WH
  WAREHOUSE_SIZE = 'X-SMALL'
  AUTO_SUSPEND   = 120
  AUTO_RESUME    = TRUE
  INITIALLY_SUSPENDED = TRUE
  COMMENT = 'CoCo Workshop warehouse';

GRANT USAGE ON WAREHOUSE COCO_WORKSHOP_WH TO ROLE COCO_WORKSHOP_ROLE;
GRANT OPERATE ON WAREHOUSE COCO_WORKSHOP_WH TO ROLE COCO_WORKSHOP_ROLE;

-- -------------------------------------------------------------------------
-- 3. Database
-- -------------------------------------------------------------------------
CREATE DATABASE IF NOT EXISTS COCO_WORKSHOP
  COMMENT = 'CoCo Workshop - AI-Accelerated Data Engineering';

GRANT OWNERSHIP ON DATABASE COCO_WORKSHOP TO ROLE COCO_WORKSHOP_ROLE
  COPY CURRENT GRANTS;

-- -------------------------------------------------------------------------
-- 4. Switch to the workshop role (database owner) for all remaining setup
-- -------------------------------------------------------------------------
USE ROLE COCO_WORKSHOP_ROLE;
USE WAREHOUSE COCO_WORKSHOP_WH;
USE DATABASE COCO_WORKSHOP;

-- -------------------------------------------------------------------------
-- 5. Schemas
-- -------------------------------------------------------------------------
CREATE SCHEMA IF NOT EXISTS SOURCE_DATA
  COMMENT = 'Raw source tables loaded from Parquet seed files';

CREATE SCHEMA IF NOT EXISTS STAGING
  COMMENT = 'Cleaned staging views created by dbt';

CREATE SCHEMA IF NOT EXISTS MARTS
  COMMENT = 'Fact and dimension tables created by dbt';

-- -------------------------------------------------------------------------
-- 6. Source tables
-- -------------------------------------------------------------------------
USE SCHEMA SOURCE_DATA;

CREATE TABLE IF NOT EXISTS RAW_CUSTOMERS (
    customer_id   INT           NOT NULL,
    first_name    VARCHAR(100),
    last_name     VARCHAR(100),
    email         VARCHAR(255),
    region        VARCHAR(50),
    signup_date   VARCHAR(30)
)
COMMENT = 'Customer master data from the e-commerce platform';

CREATE TABLE IF NOT EXISTS RAW_PRODUCTS (
    product_id    INT           NOT NULL,
    product_name  VARCHAR(200),
    category      VARCHAR(100),
    unit_price    DECIMAL(10,2)
)
COMMENT = 'Product catalog';

CREATE TABLE IF NOT EXISTS RAW_ORDERS (
    order_id      INT           NOT NULL,
    customer_id   INT,
    order_date    VARCHAR(30),
    status        VARCHAR(50),
    total_amount  DECIMAL(12,2),
    created_at    VARCHAR(50)
)
COMMENT = 'Order headers from the e-commerce platform';

CREATE TABLE IF NOT EXISTS RAW_ORDER_ITEMS (
    order_item_id INT           NOT NULL,
    order_id      INT,
    product_id    INT,
    quantity      INT,
    line_total    DECIMAL(12,2)
)
COMMENT = 'Line-level order items';

-- -------------------------------------------------------------------------
-- 7. File format and internal stage for seed data
-- -------------------------------------------------------------------------
CREATE FILE FORMAT IF NOT EXISTS parquet_format
  TYPE = PARQUET;

CREATE STAGE IF NOT EXISTS seed_stage
  FILE_FORMAT = parquet_format
  COMMENT = 'Internal stage for uploading seed Parquet files';

-- -------------------------------------------------------------------------
-- 8. Done — display summary
-- -------------------------------------------------------------------------
SELECT 'Setup complete' AS status,
       CURRENT_ACCOUNT() AS account,
       CURRENT_USER() AS "user",
       CURRENT_ROLE() AS role,
       CURRENT_WAREHOUSE() AS warehouse,
       CURRENT_DATABASE() AS database;

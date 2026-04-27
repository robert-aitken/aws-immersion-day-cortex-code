#!/bin/bash
# =============================================================================
# load-seed-data.sh — Upload Parquet seed files and load into Snowflake
# =============================================================================
# Uploads the local Parquet files to a Snowflake internal stage, then
# copies them into the source tables created by snowflake-setup.sql.
#
# Prerequisites:
#   - snowflake-setup.sql has been run (tables and stage exist)
#   - Snowflake CLI (snow) is installed and configured
#   - Run from the workshop repo root: ./scripts/load-seed-data.sh
# =============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
SEED_DIR="$REPO_DIR/data/seed"
CONN="${SNOW_CONNECTION:-DEMO}"

echo "=== Loading seed data into Snowflake ==="
echo "Connection: $CONN"
echo "Seed dir:   $SEED_DIR"

# Verify seed files exist
for f in raw_customers.parquet raw_products.parquet raw_orders.parquet raw_order_items.parquet; do
    if [ ! -f "$SEED_DIR/$f" ]; then
        echo "ERROR: Missing seed file: $SEED_DIR/$f"
        exit 1
    fi
done

# Upload Parquet files to the internal stage
echo ""
echo "--- Uploading Parquet files to @COCO_WORKSHOP.SOURCE_DATA.seed_stage ---"
snow sql -c "$CONN" -q "
  PUT file://$SEED_DIR/raw_customers.parquet   @COCO_WORKSHOP.SOURCE_DATA.seed_stage/customers/   AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
  PUT file://$SEED_DIR/raw_products.parquet     @COCO_WORKSHOP.SOURCE_DATA.seed_stage/products/     AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
  PUT file://$SEED_DIR/raw_orders.parquet       @COCO_WORKSHOP.SOURCE_DATA.seed_stage/orders/       AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
  PUT file://$SEED_DIR/raw_order_items.parquet  @COCO_WORKSHOP.SOURCE_DATA.seed_stage/order_items/  AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
"

# Load data from stage into tables
echo ""
echo "--- Loading data into source tables ---"
snow sql -c "$CONN" -q "
  USE ROLE COCO_WORKSHOP_ROLE;
  USE WAREHOUSE COCO_WORKSHOP_WH;
  USE SCHEMA COCO_WORKSHOP.SOURCE_DATA;

  -- Truncate before loading (idempotent)
  TRUNCATE TABLE IF EXISTS RAW_CUSTOMERS;
  TRUNCATE TABLE IF EXISTS RAW_PRODUCTS;
  TRUNCATE TABLE IF EXISTS RAW_ORDERS;
  TRUNCATE TABLE IF EXISTS RAW_ORDER_ITEMS;

  COPY INTO RAW_CUSTOMERS
  FROM (
    SELECT \$1:customer_id::INT,
           \$1:first_name::VARCHAR,
           \$1:last_name::VARCHAR,
           \$1:email::VARCHAR,
           \$1:region::VARCHAR,
           \$1:signup_date::VARCHAR
    FROM @seed_stage/customers/
  )
  FILE_FORMAT = (TYPE = PARQUET)
  PURGE = FALSE;

  COPY INTO RAW_PRODUCTS
  FROM (
    SELECT \$1:product_id::INT,
           \$1:product_name::VARCHAR,
           \$1:category::VARCHAR,
           \$1:unit_price::DECIMAL(10,2)
    FROM @seed_stage/products/
  )
  FILE_FORMAT = (TYPE = PARQUET)
  PURGE = FALSE;

  COPY INTO RAW_ORDERS
  FROM (
    SELECT \$1:order_id::INT,
           \$1:customer_id::INT,
           \$1:order_date::VARCHAR,
           \$1:status::VARCHAR,
           \$1:total_amount::DECIMAL(12,2),
           \$1:created_at::VARCHAR
    FROM @seed_stage/orders/
  )
  FILE_FORMAT = (TYPE = PARQUET)
  PURGE = FALSE;

  COPY INTO RAW_ORDER_ITEMS
  FROM (
    SELECT \$1:order_item_id::INT,
           \$1:order_id::INT,
           \$1:product_id::INT,
           \$1:quantity::INT,
           \$1:line_total::DECIMAL(12,2)
    FROM @seed_stage/order_items/
  )
  FILE_FORMAT = (TYPE = PARQUET)
  PURGE = FALSE;
"

# Verify row counts
echo ""
echo "--- Verifying row counts ---"
snow sql -c "$CONN" -q "
  USE ROLE COCO_WORKSHOP_ROLE;
  USE SCHEMA COCO_WORKSHOP.SOURCE_DATA;
  SELECT 'RAW_CUSTOMERS'   AS table_name, COUNT(*) AS row_count FROM RAW_CUSTOMERS
  UNION ALL
  SELECT 'RAW_PRODUCTS',   COUNT(*) FROM RAW_PRODUCTS
  UNION ALL
  SELECT 'RAW_ORDERS',     COUNT(*) FROM RAW_ORDERS
  UNION ALL
  SELECT 'RAW_ORDER_ITEMS', COUNT(*) FROM RAW_ORDER_ITEMS
  ORDER BY table_name;
"

echo ""
echo "=== Seed data loaded successfully ==="

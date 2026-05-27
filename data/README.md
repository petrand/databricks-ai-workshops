# Synthetic Data Generation for Workshop

This folder contains scripts and source documents to generate all the data required for the QSIC workshop. It produces two types of data in Unity Catalog:

1. **Structured retail data** — synthetic customers, products, stores, transactions, and payments
2. **Chunked policy documents** — markdown policy docs split into overlapping text chunks for vector search

## Folder Structure

```
data/
├── README.md
├── policy_docs/                           # Source markdown policy documents (7 files)
│   ├── customer_service_guidelines.md
│   ├── delivery_pickup_procedures.md
│   ├── membership_loyalty_program.md
│   ├── privacy_policy.md
│   ├── product_safety_recalls.md
│   ├── return_refund_policy.md
│   └── store_operating_procedures.md
├── local_cli_setup_script/                # Scripts that run from your local machine
│   ├── execute_sql.py                     # Generate structured tables via SQL REST API
│   ├── execute_chunking.py                # Chunk policy docs via SQL REST API
│   ├── run_sql_generation.py              # Generate structured tables via Databricks CLI
│   └── create_resources.py                # Create Vector Search + Genie Space resources
└── workspace_setup_script/                # Databricks notebook (does everything on-cluster)
    └── 01_quickstart_setup.py
```

## Scripts Overview

There are **three tasks**:

### Task 1: Generate Structured Retail Data

Creates 6 tables: `customers` (200 rows), `products` (~500), `stores` (10), `transactions` (2000), `transaction_items` (~8000+), `payment_history` (400).

| Script | Runs On | Method |
|--------|---------|--------|
| `local_cli_setup_script/execute_sql.py` | Local machine | SQL via REST API (`urllib`) |
| `local_cli_setup_script/run_sql_generation.py` | Local machine | SQL via `databricks api` CLI |
| `workspace_setup_script/create_structured_data.py` | Databricks cluster | PySpark DataFrames |

### Task 2: Chunk Policy Documents for Vector Search

Reads the 7 markdown files from `policy_docs/`, splits them into overlapping chunks (1000 chars, 200 overlap), and writes to a `policy_docs_chunked` table.

| Script | Runs On | Method |
|--------|---------|--------|
| `local_cli_setup_script/execute_chunking.py` | Local machine | SQL via REST API (`urllib`) |
| `workspace_setup_script/create_chunked_docs.py` | Databricks cluster | PySpark + UC Volumes |

### Task 3: Create Resources (Vector Search + Genie Space)

Creates a Vector Search endpoint + index and a Genie Space with all 6 tables. Run this **after** tasks 1 and 2.

| Script | Runs On | Method |
|--------|---------|--------|
| `local_cli_setup_script/create_resources.py` | Local machine | REST API (`urllib`) |

## Quick Start (Local)

Run all three tasks from your local machine:

```bash
cd data/local_cli_setup_script

# 1. Generate tables
python execute_sql.py --profile DEFAULT --warehouse-id <WAREHOUSE-ID> --catalog <CATALOG> --schema <SCHEMA>

# 2. Chunk policy docs
python execute_chunking.py --profile DEFAULT --warehouse-id <WAREHOUSE-ID> --catalog <CATALOG> --schema <SCHEMA>

# 3. Create Vector Search + Genie Space
python create_resources.py --profile DEFAULT --warehouse-id <WAREHOUSE-ID> --catalog <CATALOG> --schema <SCHEMA>
```

The `create_resources.py` script will print the `VECTOR_SEARCH_INDEX` and `GENIE_SPACE_ID` values to add to your `advanced/.env` file.

## Configuration

### Local CLI scripts (`local_cli_setup_script/`)

All local scripts accept `--catalog` and `--schema` as CLI arguments — no need to edit source code:

| Argument | Description | Example |
|----------|-------------|---------|
| `--profile` | Databricks CLI profile (default: DEFAULT) | `DEFAULT` |
| `--warehouse-id` | SQL warehouse ID | `9a7b09e77b8a8994` |
| `--catalog` | Unity Catalog name | `my_catalog` |
| `--schema` | Schema name | `retail_agent` |

### Workspace scripts (`workspace_setup_script/`)

These run on a Databricks cluster. Edit the `CATALOG` and `SCHEMA` constants at the top of each file:

Files to update:
- [ ] `workspace_setup_script/create_structured_data.py` — lines with `CATALOG` and `SCHEMA`
- [ ] `workspace_setup_script/create_chunked_docs.py` — lines with `CATALOG` and `SCHEMA`

## Prerequisites

- [ ] Databricks CLI installed and configured (`databricks auth login --profile DEFAULT`)
- [ ] A running SQL warehouse (note the warehouse ID)
- [ ] Unity Catalog access (permission to create tables in target catalog/schema)
- [ ] Create the target catalog and schema before running:
  ```sql
  CREATE CATALOG IF NOT EXISTS <CATALOG>;
  CREATE SCHEMA IF NOT EXISTS <CATALOG>.<SCHEMA>;
  ```

## Notes

- All scripts use `random.seed(42)` for reproducibility — data will be identical across runs
- The workspace needs a Foundation Model API endpoint (`databricks-gte-large-en`) for embedding generation
- `create_resources.py` is idempotent — safe to re-run if interrupted

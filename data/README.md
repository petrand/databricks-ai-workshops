# Workshop synthetic data

Pick an **industry** in [`01_quickstart_setup.py`](01_quickstart_setup.py) (widget: `retail`, `education`, or `financial_services`). The notebook generates tables and chunks markdown from each vertical’s `docs/` folder.

## Layout

```
data/
├── 00-utils.ipynb              # optional: MLflow artifacts on UC Volume (restricted networks)
├── 01_quickstart_setup.py      # main workshop setup notebook
├── lib/
│   ├── generate.py             # dispatches to verticals/registry.py
│   ├── chunking.py             # writes chunked docs table (name depends on industry)
│   └── demo_names.py
├── verticals/
│   ├── registry.py             # lists onboarded industries
│   ├── retail/
│   │   ├── workshop.py         # brand, Genie/VS names, optional UC function
│   │   ├── tables.py
│   │   └── docs/               # source markdown for Vector Search
│   ├── education/
│   │   ├── workshop.py
│   │   ├── tables.py
│   │   └── docs/
│   └── financial_services/
│       ├── workshop.py
│       ├── tables.py
│       └── docs/
└── scripts/
    └── generate_structured_data.py
```

## Industries

| Industry | Brand | Tables | Docs |
|----------|-------|--------|------|
| `education` (default) | EduPath Academy | 6 retail-shaped table names, school semantics | `verticals/education/docs/` |
| `retail` | FreshMart | Same 6 tables, grocery semantics | `verticals/retail/docs/` |
| `financial_services` | Meridian Capital Partners | `{catalog}.{schema}`: clients, accounts, portfolio_holdings, dailyprice, company_profile | 13 AAPL/TSLA market-shock news articles in `verticals/financial_services/docs/` |

## Local CLI (optional)

```bash
cd data
python scripts/generate_structured_data.py --industry retail --catalog CATALOG --schema SCHEMA
```

`local_cli_setup_script/*` is a legacy path and remains retail-centric; prefer `scripts/generate_structured_data.py` and notebook flow for multi-industry runs.

## Financial services market data

For `financial_services`, **all workshop tables** (including market data) live in `{catalog}.{schema}` from the setup widgets.

Real market data ships with the repo as static CSVs in `verticals/financial_services/market_data/` (`dailyprice.csv.gz`: 151,702 rows of daily prices for 29 tickers, 1999–2023; `company_profile.csv`: 29 rows). It is a one-time export of the Databricks Marketplace [Sample Market Data - Daily Price Data](https://marketplace.databricks.com/details/0f7c65e3-875a-40e2-bd58-5c8bcadbdc2b) listing, and setup loads it into `{catalog}.{schema}` automatically — **no Marketplace or Delta Sharing access required** on the target workspace.

Other verticals (`education`, `retail`) use fully synthetic data in `{catalog}.{schema}` only.

Agents and lab guides written for education/retail still expect the 6-table names. For `financial_services`, combine **Vector Search** on `market_news_index` (historical shock narratives) with **Genie/SQL** on `dailyprice` (price context around shock dates). Re-run setup only when you add or remove markdown in `docs/` or need to refresh the index.

The FSI optional UC function is `weekly_close_spread(ticker_symbol)`. It returns weekly volatility as the standard deviation of day-over-day close returns (%) over the latest 7 trading days for that ticker.

Structured tables now receive Unity Catalog table descriptions automatically during generation for all verticals.

Chunking and embeddings use the same generic path across industries. The flow is `lib/chunking.py` `chunk_markdown_docs_to_table` → chunk table → Vector Search index. Naming is dynamic by use case:
- `education`, `retail`: `policy_docs_chunked` → `policy_docs_index`
- `financial_services`: `market_news_chunked` → `market_news_index`

Vector Search endpoint names use an industry code pattern: `{industry_code}-vs-{schema}`. Current codes are `education`, `retail`, and `fsi` (for `financial_services`), so examples are `education-vs-my-schema`, `retail-vs-my-schema`, and `fsi-vs-my-schema`.

## Onboarding a new industry

1. Add `verticals/<industry>/` with `tables.py`, `docs/`, and `workshop.py` (see an existing vertical).
2. Register it in `verticals/registry.py` (`_REGISTRY` and import).
3. If the vertical needs real reference data, bundle it as static files in the vertical folder (like `financial_services/market_data/`) so setup has no external dependencies.

UC functions live in each vertical’s `workshop.py` (`udf_sql` / `udf_name`), not in `lib/generate.py`.

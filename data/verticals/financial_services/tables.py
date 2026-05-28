"""Meridian Capital Partners — financial services tables for workshop demo.

Paths match 01_quickstart_setup.py widgets (Catalog + Schema):
  - 1st party (writable): {catalog}.{schema}.clients, accounts, portfolio_holdings
  - 3rd party (read-only source): {catalog}.market_data.dailyprice, company_profile
  - 3rd party (Genie/SQL in workshop schema): views at {catalog}.{schema}.dailyprice, company_profile
"""

import json
import random
from datetime import datetime, timedelta

from lib.demo_names import CITIES_STATES, FIRST_NAMES, LAST_NAMES

# Databricks Marketplace: Sample Market Data - Daily Price Data (Delta Sharing)
# https://e2-demo-field-eng.cloud.databricks.com/marketplace/consumer/listings/0f7c65e3-875a-40e2-bd58-5c8bcadbdc2b
# Install the listing into the same catalog as the setup notebook Catalog widget.
MARKET_DATA_SCHEMA = "market_data"
DAILY_PRICE_TABLE = "dailyprice"
COMPANY_PROFILE_TABLE = "company_profile"

FIRST_PARTY_TABLES = ["clients", "accounts", "portfolio_holdings"]
MARKET_DATA_VIEW_TABLES = [DAILY_PRICE_TABLE, COMPANY_PROFILE_TABLE]
TABLES = FIRST_PARTY_TABLES + MARKET_DATA_VIEW_TABLES


def _phone():
    return f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"


def _email(first, last):
    domain = random.choice(["meridiancapital.com", "investor.com", "familyoffice.com"])
    return f"{first.lower()}.{last.lower()}@{domain}"


def _save(spark, catalog: str, schema: str, table, rows):
    fqn = f"{catalog}.{schema}.{table}"
    spark.createDataFrame(rows).write.mode("overwrite").saveAsTable(fqn)
    print(f"Created {fqn} — {len(rows)} rows")


def _market_data_fqn(catalog: str, table: str) -> str:
    return f"`{catalog}`.`{MARKET_DATA_SCHEMA}`.`{table}`"


def _resolve_locations(
    full_schema: str,
    catalog: str | None,
    schema: str | None,
    market_data_catalog: str | None,
) -> tuple[str, str, str]:
    """Align with notebook: CATALOG, SCHEMA, and market data at CATALOG.market_data."""
    if catalog and schema:
        workshop_catalog, workshop_schema = catalog, schema
    else:
        parts = full_schema.split(".", 1)
        if len(parts) != 2 or not parts[0] or not parts[1]:
            raise ValueError(f"full_schema must be catalog.schema, got '{full_schema}'")
        workshop_catalog, workshop_schema = parts

    share_catalog = market_data_catalog or workshop_catalog
    return workshop_catalog, workshop_schema, share_catalog


def _verify_market_data(spark, share_catalog: str) -> None:
    daily = _market_data_fqn(share_catalog, DAILY_PRICE_TABLE)
    count = spark.sql(f"SELECT COUNT(*) AS n FROM {daily}").collect()[0]["n"]
    if count == 0:
        raise ValueError(
            f"No rows in {share_catalog}.{MARKET_DATA_SCHEMA}.{DAILY_PRICE_TABLE}. "
            "Install the Marketplace listing into the Catalog widget name."
        )
    print(
        f"Market data source: {share_catalog}.{MARKET_DATA_SCHEMA} "
        f"({count:,} daily price rows — not copied, exposed via views in workshop schema)"
    )


def _symbols_from_market_data(spark, share_catalog: str, limit: int = 400) -> list[str]:
    daily = _market_data_fqn(share_catalog, DAILY_PRICE_TABLE)
    rows = spark.sql(
        f"""
        SELECT ticker
        FROM (
          SELECT DISTINCT ticker
          FROM {daily}
          WHERE ticker IS NOT NULL AND ticker NOT IN ('NaN', 'nan', '')
        )
        ORDER BY ticker
        LIMIT {int(limit)}
        """
    ).collect()
    symbols = [r["ticker"] for r in rows]
    if not symbols:
        raise ValueError(
            f"No tickers in {share_catalog}.{MARKET_DATA_SCHEMA}.{DAILY_PRICE_TABLE}. "
            "Install the Marketplace listing into the Catalog widget name."
        )
    return symbols


def _create_market_data_views(spark, workshop_catalog: str, workshop_schema: str, share_catalog: str) -> None:
    """Views in {catalog}.{schema} pointing at {catalog}.market_data.* (no data copy)."""
    for table in MARKET_DATA_VIEW_TABLES:
        source = _market_data_fqn(share_catalog, table)
        target = f"{workshop_catalog}.{workshop_schema}.{table}"
        spark.sql(f"CREATE OR REPLACE VIEW {target} AS SELECT * FROM {source}")
        print(f"Created view {target} -> {share_catalog}.{MARKET_DATA_SCHEMA}.{table}")


def generate(
    spark,
    full_schema: str,
    seed: int = 42,
    catalog: str | None = None,
    schema: str | None = None,
    market_data_catalog: str | None = None,
) -> list[str]:
    workshop_catalog, workshop_schema, share_catalog = _resolve_locations(
        full_schema, catalog, schema, market_data_catalog
    )
    random.seed(seed)

    _verify_market_data(spark, share_catalog)
    symbols = _symbols_from_market_data(spark, share_catalog)
    as_of_date = datetime.utcnow().strftime("%Y-%m-%d")

    clients = []
    for i in range(1, 101):
        first, last = random.choice(FIRST_NAMES), random.choice(LAST_NAMES)
        city, state = random.choice(CITIES_STATES)
        clients.append({
            "client_id": f"CLT-{i:04d}",
            "first_name": first,
            "last_name": last,
            "email": _email(first, last),
            "phone": _phone(),
            "city": city,
            "state": state,
            "country": "US" if len(state) == 2 else state,
            "kyc_tier": random.choices(["Standard", "Enhanced", "PEP"], weights=[70, 25, 5])[0],
            "risk_rating": random.choices(["Low", "Medium", "High"], weights=[50, 35, 15])[0],
            "onboard_date": (datetime(2018, 1, 1) + timedelta(days=random.randint(0, 2200))).strftime("%Y-%m-%d"),
            "preferences": json.dumps({
                "asset_classes": random.sample(["Equity", "Fixed Income", "ETF"], k=random.randint(1, 2)),
                "esg_screen": random.choice([True, False]),
            }),
        })
    _save(spark, workshop_catalog, workshop_schema, "clients", clients)

    accounts = []
    for acc_id in range(1, 201):
        client = random.choice(clients)
        accounts.append({
            "account_id": f"ACC-{acc_id:05d}",
            "client_id": client["client_id"],
            "account_type": random.choice(["Brokerage", "Retirement", "Trust", "Institutional"]),
            "status": random.choices(["Active", "Restricted", "Closed"], weights=[90, 7, 3])[0],
            "open_date": (datetime(2019, 1, 1) + timedelta(days=random.randint(0, 1800))).strftime("%Y-%m-%d"),
            "cash_balance_usd": round(random.uniform(5_000, 500_000), 2),
        })
    _save(spark, workshop_catalog, workshop_schema, "accounts", accounts)

    holdings = []
    holding_id = 1
    for account in accounts:
        if account["status"] == "Closed":
            continue
        for _ in range(random.randint(3, 12)):
            symbol = random.choice(symbols)
            qty = round(random.uniform(10, 5000), 2)
            cost_basis = round(random.uniform(15, 800), 4)
            holdings.append({
                "holding_id": f"HLD-{holding_id:06d}",
                "account_id": account["account_id"],
                "symbol": symbol,
                "quantity": qty,
                "cost_basis_usd": cost_basis,
                "as_of_date": as_of_date,
            })
            holding_id += 1
    _save(spark, workshop_catalog, workshop_schema, "portfolio_holdings", holdings)

    _create_market_data_views(spark, workshop_catalog, workshop_schema, share_catalog)

    ws = f"{workshop_catalog}.{workshop_schema}"
    print(
        f"Example join (all tables in workshop schema {ws}):\n"
        f"  SELECT h.*, d.close, c.industry\n"
        f"  FROM {ws}.portfolio_holdings h\n"
        f"  JOIN {ws}.company_profile c ON h.symbol = c.ticker\n"
        f"  JOIN {ws}.dailyprice d ON h.symbol = d.ticker"
    )
    return TABLES

"""Meridian Capital Partners workshop metadata and UC function."""

from verticals.base import WorkshopVertical
from verticals.financial_services import tables


def _genie_title(schema: str) -> str:
    return f"Meridian_Capital_Data_({schema})"


def _vs_prefix(schema: str) -> str:
    return f"meridian-vs-{schema.strip().replace('_', '-')}"


def _udf_sql(full_schema: str) -> str:
    return f"""
CREATE OR REPLACE FUNCTION {full_schema}.portfolio_forecast(current_aum DOUBLE, monthly_growth_pct DOUBLE)
RETURNS ARRAY<DOUBLE>
LANGUAGE PYTHON
AS $$
def f(current_aum: float, monthly_growth_pct: float = 0.5) -> list:
    return [round(current_aum * (1 + monthly_growth_pct / 100) ** i, 2) for i in range(1, 7)]
return f(current_aum, monthly_growth_pct)
$$"""


def _generate_tables(spark, full_schema: str, seed: int = 42, market_data_catalog: str | None = None):
    catalog = market_data_catalog or full_schema.split(".", 1)[0]
    return tables.generate(
        spark, full_schema, seed, market_data_catalog=catalog
    )


VERTICAL = WorkshopVertical(
    id="financial_services",
    brand="Meridian Capital Partners",
    genie_title=_genie_title,
    genie_description=(
        "Explore Meridian Capital Partners wealth-management and trading activity—client relationships, "
        "portfolio exposure, branch performance, and settlement flows—in plain English."
    ),
    vs_endpoint_prefix=_vs_prefix,
    mlflow_experiment_suffix="meridian-agent-workshop",
    generate_tables=_generate_tables,
    udf_name="portfolio_forecast",
    udf_sql=_udf_sql,
)

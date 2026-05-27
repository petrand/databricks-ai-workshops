"""
Generate workshop data for an industry vertical.

Called from data/01_quickstart_setup.py with the Industry widget value.
"""

import os
from types import SimpleNamespace

from verticals.registry import INDUSTRIES, get_vertical  # noqa: F401 — re-exported for CLI/scripts

DATA_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

__all__ = ["INDUSTRIES", "generate_workshop_data"]


def _docs_dir(industry: str) -> str:
    return os.path.join(DATA_ROOT, "verticals", industry, "docs")


def generate_workshop_data(
    industry: str,
    catalog: str,
    schema: str,
    spark,
    seed: int = 42,
    market_data_catalog: str | None = None,
):
    vertical = get_vertical(industry)
    full_schema = f"{catalog}.{schema}"

    print(f"Generating {vertical.brand} data in {full_schema}...")

    gen_kwargs: dict = {"seed": seed}
    if vertical.id == "financial_services":
        gen_kwargs["market_data_catalog"] = market_data_catalog
    tables = vertical.generate_tables(spark, full_schema, **gen_kwargs)

    udf_sql = vertical.udf_sql(full_schema) if vertical.udf_sql else None

    return SimpleNamespace(
        industry=vertical.id,
        catalog=catalog,
        schema=schema,
        full_schema=full_schema,
        tables=tables,
        docs_dir=_docs_dir(vertical.id),
        brand_name=vertical.brand,
        genie_title=vertical.genie_title(schema),
        genie_description=vertical.genie_description,
        vs_endpoint_prefix=vertical.vs_endpoint_prefix(schema),
        mlflow_experiment_suffix=vertical.mlflow_experiment_suffix,
        optional_udf_sql=udf_sql,
        optional_udf_name=vertical.udf_name,
    )

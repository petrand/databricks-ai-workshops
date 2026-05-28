"""
Generate workshop data for an industry vertical.

Called from data/01_quickstart_setup.py with the Industry widget value.
"""

import os
from types import SimpleNamespace

from verticals.base import vs_endpoint_name
from verticals.registry import INDUSTRIES, get_vertical  # noqa: F401 — re-exported for CLI/scripts

DATA_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

__all__ = ["INDUSTRIES", "generate_workshop_data"]


def _docs_dir(industry: str) -> str:
    return os.path.join(DATA_ROOT, "verticals", industry, "docs")


def _apply_table_descriptions(
    spark,
    full_schema: str,
    tables: list[str],
    descriptions: dict[str, str] | None,
) -> None:
    if not descriptions:
        print("No table descriptions configured for this industry; skipping COMMENT ON TABLE.")
        return

    for table in tables:
        description = descriptions.get(table)
        if not description:
            print(f"WARNING: No table description configured for {full_schema}.{table}; skipping.")
            continue

        escaped = description.replace("'", "''")
        spark.sql(f"COMMENT ON TABLE {full_schema}.{table} IS '{escaped}'")
        print(f"  Added table description: {full_schema}.{table}")


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
    if vertical.generate_extra_kwargs:
        gen_kwargs.update(vertical.generate_extra_kwargs(catalog, schema, market_data_catalog))
    tables = vertical.generate_tables(spark, full_schema, **gen_kwargs)
    _apply_table_descriptions(spark, full_schema, tables, vertical.table_descriptions)

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
        vs_endpoint_name=vs_endpoint_name(vertical.id, schema),
        chunk_table_name=vertical.chunk_table_name,
        doc_index_name=vertical.doc_index_name,
        mlflow_experiment_suffix=vertical.mlflow_experiment_suffix,
        optional_udf_sql=udf_sql,
        optional_udf_name=vertical.udf_name,
    )

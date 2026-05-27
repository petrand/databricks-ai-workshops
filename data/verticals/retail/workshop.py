"""FreshMart retail workshop metadata."""

from verticals.base import WorkshopVertical
from verticals.retail import tables


def _genie_title(schema: str) -> str:
    return f"FreshMart_Retail_Data_({schema})"


def _vs_prefix(schema: str) -> str:
    return f"freshmart-vs-{schema.strip().replace('_', '-')}"


VERTICAL = WorkshopVertical(
    id="retail",
    brand="FreshMart",
    genie_title=_genie_title,
    genie_description=(
        "Explore FreshMart grocery retail operations—shopper loyalty, product assortment, "
        "store performance, and purchase patterns—in plain English."
    ),
    vs_endpoint_prefix=_vs_prefix,
    mlflow_experiment_suffix="freshmart-agent-workshop",
    generate_tables=tables.generate,
)

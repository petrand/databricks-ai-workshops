"""Shared types for industry vertical workshop setup."""

from dataclasses import dataclass
from typing import Callable


# Short codes for Vector Search endpoint names: {code}-vs-{schema}
VS_ENDPOINT_SLUGS: dict[str, str] = {
    "retail": "retail",
    "education": "education",
    "financial_services": "fsi",
}


def vs_endpoint_name(vertical_id: str, schema: str) -> str:
    key = vertical_id.strip().lower().replace(" ", "_")
    try:
        slug = VS_ENDPOINT_SLUGS[key]
    except KeyError:
        known = ", ".join(sorted(VS_ENDPOINT_SLUGS))
        raise ValueError(
            f"Unknown industry '{vertical_id}'. Add it to VS_ENDPOINT_SLUGS or use: {known}"
        ) from None
    schema_slug = schema.strip().replace("_", "-")
    return f"{slug}-vs-{schema_slug}"


@dataclass(frozen=True)
class WorkshopVertical:
    """Metadata and generators for one workshop industry."""

    id: str
    brand: str
    genie_title: Callable[[str], str]
    genie_description: str
    mlflow_experiment_suffix: str
    generate_tables: Callable[..., list[str]]
    table_descriptions: dict[str, str] | None = None
    chunk_table_name: str = "policy_docs_chunked"
    doc_index_name: str = "policy_docs_index"
    udf_name: str | None = None
    udf_sql: Callable[[str], str] | None = None

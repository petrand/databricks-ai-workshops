"""Shared types for industry vertical workshop setup."""

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class WorkshopVertical:
    """Metadata and generators for one workshop industry."""

    id: str
    brand: str
    genie_title: Callable[[str], str]
    genie_description: str
    vs_endpoint_prefix: Callable[[str], str]
    mlflow_experiment_suffix: str
    generate_tables: Callable[..., list[str]]
    udf_name: str | None = None
    udf_sql: Callable[[str], str] | None = None

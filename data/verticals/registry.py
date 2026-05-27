"""Register workshop verticals. Add new industries here when onboarding."""

from verticals.base import WorkshopVertical
from verticals.education.workshop import VERTICAL as education
from verticals.financial_services.workshop import VERTICAL as financial_services
from verticals.retail.workshop import VERTICAL as retail

_REGISTRY: dict[str, WorkshopVertical] = {
    v.id: v
    for v in (retail, education, financial_services)
}

INDUSTRIES = tuple(_REGISTRY.keys())


def get_vertical(industry: str) -> WorkshopVertical:
    key = industry.strip().lower().replace(" ", "_")
    try:
        return _REGISTRY[key]
    except KeyError:
        raise ValueError(
            f"Unknown industry '{industry}'. Use: {', '.join(INDUSTRIES)}"
        ) from None

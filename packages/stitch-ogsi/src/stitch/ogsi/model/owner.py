from pydantic import BaseModel, ConfigDict

from stitch.models.types import Percentage


class Owner(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True)

    name: str
    """Name of the company."""

    stake: Percentage
    """Ownership percentage (0–100)."""

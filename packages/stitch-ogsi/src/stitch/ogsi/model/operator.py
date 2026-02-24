from pydantic import BaseModel, ConfigDict

from stitch.models.types import Percentage


class Operator(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True)

    name: str
    """Name of the operating company."""

    stake: Percentage
    """Operating stake percentage (0–100)."""

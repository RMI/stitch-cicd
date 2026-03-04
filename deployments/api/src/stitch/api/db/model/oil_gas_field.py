from __future__ import annotations

from typing import ClassVar

from pydantic import ConfigDict
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from stitch.ogsi.model.og_field import OilGasFieldBase

from .common import Base
from .mixins import PayloadMixin, TimestampMixin, UserAuditMixin


class OilGasFieldModel(
    TimestampMixin, UserAuditMixin, PayloadMixin[OilGasFieldBase], Base
):
    """Domain wrapper for an OG field, 1:1 with a Resource."""

    __tablename__ = "oil_gas_fields"

    # Use resource_id as both PK and FK: keeps ids consistent across /resources and /oil_gas_fields
    resource_id: Mapped[int] = mapped_column(
        ForeignKey("resources.id"), primary_key=True
    )

    # Tell PayloadMixin what type to validate/serialize
    payload_type: ClassVar[type[OilGasFieldBase]] = OilGasFieldBase

    # Domain-agnostic: payloads don’t have to have `source`
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)

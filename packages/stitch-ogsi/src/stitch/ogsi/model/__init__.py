from pydantic import Field
from typing import Annotated
from stitch.models.source import SourceBase, SourcePayload, SourceRef, SourceCollection
from stitch.models.resource import ConstituentProvenance, Resource
from .og_field import OilAndGasFieldSourceData
from .owner import Owner
from .operator import Operator

from .types import (
    LLM_SRC,
    GEM_SRC,
    RMI_SRC,
    WM_SRC,
    FieldStatus,
    LocationType,
    OGSISourceKey,
    PrimaryHydrocarbonGroup,
    ProductionConventionality,
)

__all__ = [
    "OGSIResource",
    "OGSIProvenance",
    "OGSISrcRef",
    "OGSISource",
    "LLMSource",
    "RMISource",
    "WoodMacSource",
    "GemSource",
    "OilAndGasFieldSourceData",
    "OGSISourceKey",
    "ProductionConventionality",
    "PrimaryHydrocarbonGroup",
    "LocationType",
    "FieldStatus",
    "Owner",
    "Operator",
]


GEM = "gem"
WM = "wm"
RMI = "rmi"
LLM = "llm"


class OilAndGasFieldSource[TSrcKey: OGSISourceKey](
    SourceBase[int, TSrcKey], OilAndGasFieldSourceData
):
    """Persisted OGSI field source = SourceBase (id, source) + data fields."""


class GemSource(OilAndGasFieldSource[GEM_SRC]):
    source: GEM_SRC = GEM


class WoodMacSource(OilAndGasFieldSource[WM_SRC]):
    source: WM_SRC = WM


class RMISource(OilAndGasFieldSource[RMI_SRC]):
    source: RMI_SRC = RMI


class LLMSource(OilAndGasFieldSource[LLM_SRC]):
    source: LLM_SRC = LLM


OGSISource = Annotated[
    GemSource | WoodMacSource | RMISource | LLMSource,
    Field(discriminator="source"),
]


class OGSISourcePayload(SourcePayload):
    gem: SourceCollection[int, GemSource] = Field(default_factory=dict)
    wm: SourceCollection[int, WoodMacSource] = Field(default_factory=dict)
    rmi: SourceCollection[int, RMISource] = Field(default_factory=dict)
    cc: SourceCollection[int, LLMSource] = Field(default_factory=dict)


class OGSISrcRef(SourceRef[int, OGSISourceKey]): ...


class OGSIProvenance(ConstituentProvenance[OGSISrcRef]): ...


class OGSIResource(Resource[OGSISourcePayload, OGSIProvenance]): ...

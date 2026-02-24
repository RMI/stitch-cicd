from typing import Annotated, Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from stitch.models.common import CountryCode, Latitude, Longitude, Percentage, Year
from stitch.models.source import SourceBase, SourceCollection, SourcePayload


LocationType = Literal["Onshore", "Offshore", "Unknown"]


ProductionConventionality = Literal[
    "Conventional", "Unconventional", "Mixed", "Unknown"
]


PrimaryHydrocarbonGroup = Literal[
    "Ultra-Light Oil",
    "Light Oil",
    "Medium Oil",
    "Heavy Oil",
    "Extra-Heavy Oil",
    "Dry Gas",
    "Wet Gas",
    "Acid Gas",
    "Condensate",
    "Mixed",
    "Unknown",
]

FieldStatus = Literal["Producing", "Non-Producing", "Abandoned", "Planned"]


class Owner(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True)

    name: str
    """Name of the company."""
    stake: Percentage
    """Ownership percentage (0–100)."""


class Operator(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True)

    name: str
    """Name of the operating company."""
    stake: Percentage
    """Operating stake percentage (0–100)."""


class OilAndGasFieldSourceData(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True)

    name: str | None = Field(min_length=1)
    """Primary name of the resource."""
    country: CountryCode | None
    """ISO 3166-1 alpha-3 country code."""
    latitude: Latitude | None = None
    """Latitude in WGS84 coordinate system."""
    longitude: Longitude | None = None
    """Longitude in WGS84 coordinate system."""
    last_updated: AwareDatetime | None = None
    """ISO 8601 timestamp of most recent source data update."""
    name_local: str | None = None
    """Name in local script if different from primary name."""
    state_province: str | None = None
    """State or province where the resource is located."""
    region: str | None = None
    """Geographic or administrative region."""
    basin: str | None = None
    """Geological basin name."""
    owners: list[Owner] | None = None
    """List of owners and their ownership stakes."""
    operators: list[Operator] | None = None
    """List of operators and their operating stakes."""
    location_type: LocationType | None = None
    """Whether the resource is onshore or offshore."""
    production_conventionality: ProductionConventionality | None = None
    """Production conventionality classification."""
    primary_hydrocarbon_group: PrimaryHydrocarbonGroup | None = None
    """Primary hydrocarbon type aligned with OGSI nomenclature."""
    reservoir_formation: str | None = None
    """Name or description of the reservoir formation."""
    discovery_year: Year | None = None
    """Year of discovery."""
    production_start_year: Year | None = None
    """Actual or planned year of first production."""
    fid_year: Year | None = None
    """Year of final investment decision."""
    field_status: FieldStatus | None = None
    """Current status of the field."""


GEM_SRC = Literal["gem"]
WM_SRC = Literal["wm"]
RMI_SRC = Literal["rmi"]
CC_SRC = Literal["cc"]
OGSISourceKey = GEM_SRC | WM_SRC | RMI_SRC | CC_SRC


class OilAndGasFieldSource[TSrcKey: OGSISourceKey](
    SourceBase[int, TSrcKey], OilAndGasFieldSourceData
):
    """Persisted OGSI field source = SourceBase (id, source) + data fields."""


class GemOGSISource(OilAndGasFieldSource[GEM_SRC]):
    source: GEM_SRC = "gem"


class WMOGSISource(OilAndGasFieldSource[WM_SRC]):
    source: WM_SRC = "wm"


class RMIOGSISource(OilAndGasFieldSource[RMI_SRC]):
    source: RMI_SRC = "rmi"


class CCOGSISource(OilAndGasFieldSource[CC_SRC]):
    source: CC_SRC = "cc"


OGSISource = Annotated[
    GemOGSISource | WMOGSISource | RMIOGSISource | CCOGSISource,
    Field(discriminator="source"),
]


class OGSISourcePayload(SourcePayload):
    gem: SourceCollection[int, GemOGSISource] = Field(default_factory=dict)
    wm: SourceCollection[int, WMOGSISource] = Field(default_factory=dict)
    rmi: SourceCollection[int, RMIOGSISource] = Field(default_factory=dict)
    cc: SourceCollection[int, CCOGSISource] = Field(default_factory=dict)

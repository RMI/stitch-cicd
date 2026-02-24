from typing import Literal

GEM_SRC = Literal["gem"]
WM_SRC = Literal["wm"]
RMI_SRC = Literal["rmi"]
LLM_SRC = Literal["llm"]

OGSISourceKey = GEM_SRC | WM_SRC | RMI_SRC | LLM_SRC

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

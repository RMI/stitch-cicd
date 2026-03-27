"""Source priority lookup table for coalescing field values."""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .common import Base


class OGFieldSourcePriority(Base):
    __tablename__ = "og_field_source_priority"

    source: Mapped[str] = mapped_column(String(10), primary_key=True)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)


DEFAULT_PRIORITIES = [
    {"source": "rmi", "priority": 1},
    {"source": "gem", "priority": 2},
    {"source": "wm", "priority": 3},
    {"source": "llm", "priority": 4},
]

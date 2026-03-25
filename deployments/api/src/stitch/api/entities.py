from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class Timestamped(BaseModel):
    created: datetime = Field(default_factory=datetime.now)
    updated: datetime = Field(default_factory=datetime.now)


# The sources will come in and be initially stored in a raw table.
# That raw table will be an append-only table.
# We'll translate that data into one of the below structures, so each source will have a `UUID` or similar that
# references their id in the "raw" table.
# When pulling into the internal "sources" table, each will get a new unique id which is what the memberships will reference


class User(BaseModel):
    id: int = Field(...)
    sub: str = Field(...)
    role: str | None = None
    email: EmailStr
    name: str


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(50, ge=1, le=200)


class PaginatedResponse[T](BaseModel):
    items: list[T]
    total_count: int
    page: int
    page_size: int

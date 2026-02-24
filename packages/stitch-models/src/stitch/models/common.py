from pydantic import BaseModel
from uuid import UUID

IdType = int | str | UUID


class Identified(BaseModel):
    id: IdType

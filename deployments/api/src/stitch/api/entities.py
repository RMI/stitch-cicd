from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    id: int = Field(...)
    sub: str = Field(...)
    role: str | None = None
    email: EmailStr
    name: str

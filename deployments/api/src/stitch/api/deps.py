from collections.abc import Generator
from typing import Annotated
from fastapi import Depends
from pydantic import EmailStr
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from stitch.api.entities import User


_engine = create_engine("sqlite://", echo=True)
SessionLocal = sessionmaker(create_engine(""))


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]


def get_current_user():
    return User(id=111, role="admin", email="admin@stitch.com", name="Stitch Admin")


CurrentUser = Annotated[User, Depends(get_current_user)]

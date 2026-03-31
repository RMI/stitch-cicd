from enum import StrEnum
from functools import lru_cache
from typing import Annotated, ClassVar

from pydantic import AfterValidator, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

class Environment(StrEnum):
    DEV = "dev"
    TEST = "test"
    PROD = "prod"


def _validate_origin(url: HttpUrl):
    if url.path and url.path != "/":
        raise ValueError("URL must be an origin with no path")
    if url.query:
        raise ValueError("URL must be an origin with no query string")
    if url.fragment:
        raise ValueError("URL must be an origin with no fragment")
    return url


OriginUrl = Annotated[HttpUrl, AfterValidator(_validate_origin)]


class Settings(BaseSettings):
    environment: Environment = Environment.DEV
    frontend_origin_url: OriginUrl = HttpUrl("http://localhost:3000")
    auth_disabled: bool = False

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()


SettingsDep = Annotated[Settings, get_settings]

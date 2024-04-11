from typing import ClassVar
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    default_localhost: ClassVar = '0.0.0.0'

    SOURCE1_HOST: str = default_localhost
    SOURCE1_PORT: int
    SOURCE2_HOST: str = default_localhost
    SOURCE2_PORT: int
    SOURCE3_HOST: str = default_localhost
    SOURCE3_PORT: int
    MARKET_HOST: str = default_localhost
    MARKET_PORT: int
    DELAY_SECONDS: int


settings = Settings()

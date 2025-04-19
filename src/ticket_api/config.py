from typing import ClassVar
from pydantic import PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config: ClassVar = SettingsConfigDict(
        env_file=".env",
    )

    # Database settings
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    @computed_field
    @property
    def DB_URL(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            path=self.DB_NAME,
        )

    # Auth settings
    PASSWORD_SPECIAL_CHARS: str = "!@#$%^&*?"
    SECRET_KEY: str


settings = Settings()

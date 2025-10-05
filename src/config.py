import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    )

    def get_refresh_token_expire_days(self):
        return self.REFRESH_TOKEN_EXPIRE_DAYS

    def get_algorithm(self):
        return f"{self.ALGORITHM}"

    def get_access_token_expire_minutes(self):
        return self.ACCESS_TOKEN_EXPIRE_MINUTES

    def get_secret_key(self):
        return f"{self.SECRET_KEY}"

    def get_db_url(self):
        return (f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@"
                f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")


settings = Settings()

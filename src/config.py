import os

import cloudinary
from fastapi_mail import ConnectionConfig
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
    SMTP_PROVIDER: str
    GMAIL_APP_PASSWORD: str
    GMAIL_USERNAME: str
    URL: str
    CLOUDINARY_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    )

    def config_cloudinary(self):
        cloudinary.config(
            cloud_name=self.CLOUDINARY_NAME,
            api_key=self.CLOUDINARY_API_KEY,
            api_secret=self.CLOUDINARY_API_SECRET,
            secure=True
        )

    def config_smtp_provider(self):
        if self.SMTP_PROVIDER == "gmail":
            conf = ConnectionConfig(
                MAIL_USERNAME=f"{self.GMAIL_USERNAME}",
                MAIL_PASSWORD=f"{self.GMAIL_APP_PASSWORD}",  # см. ниже
                MAIL_FROM=f"{self.GMAIL_USERNAME}",
                MAIL_PORT=587,
                MAIL_SERVER="smtp.gmail.com",
                MAIL_STARTTLS=True,
                MAIL_SSL_TLS=False,
                USE_CREDENTIALS=True,
                VALIDATE_CERTS=True
            )
            return conf


    def get_URL(self):
        return self.URL


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

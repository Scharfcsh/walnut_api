from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    app_name: str = "Walnut API"
    env: str = "development"

    database_url: str
    redis_url: str

    secret_key: str
    access_token_expire_minutes: int = Field(default=30)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

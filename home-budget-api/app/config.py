from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SECRET_KEY: str = "change-me-in-.env"
    DATABASE_URL: str = "sqlite:///./budget.db"
    INITIAL_BALANCE: float = 1000.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
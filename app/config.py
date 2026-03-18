from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "inventory"
    mongodb_collection: str = "products"

    # Used by /convert if you want to pin a specific endpoint later
    fx_base_url: str = "https://api.frankfurter.app"


settings = Settings()


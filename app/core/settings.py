from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8', extra='ignore'
    )

    ALGORITHM: str
    REDIS_HOST: str
    REDIS_PORT: int
    SECRET_KEY: str
    DATABASE_URL: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REDIS_CACHE_TTL_SECONDS: int = 3600
    REDIS_POKEMON_CATALOG_TTL_SECONDS: int = 86400
    REDIS_POKEMON_ITEM_TTL_SECONDS: int = 21600
    REDIS_POKEMON_SYNC_CHECK_SECONDS: int = 600

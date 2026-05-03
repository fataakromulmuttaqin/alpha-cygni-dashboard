from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:3000"

    CACHE_TTL_SECONDS: int = 300
    USE_REDIS: bool = False
    REDIS_URL: str = "redis://localhost:6379"

    ALPHA_VANTAGE_KEY: str = ""
    TWELVE_DATA_KEY: str = ""
    DATA_REFRESH_INTERVAL: int = 300

    # FRED API - US Macro data (DXY, Treasury Yields, dll)
    FRED_API_KEY: str = "3a95b92cd2469899902a2727767c032d"
    FRED_BASE_URL: str = "https://api.stlouisfed.org/fred"

    # BLS API - Economic data (CPI, NFP, unemployment)
    BLS_API_KEY: str = ""
    BLS_BASE_URL: str = "https://api.bls.gov/publicAPI/v2"

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()

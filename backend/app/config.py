from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/macrosentiment"
    fred_api_key: str = ""
    ibkr_host: str = "127.0.0.1"
    ibkr_port: int = 4001
    ibkr_client_id: int = 78
    ibkr_timeout_sec: int = 10
    backend_host: str = "0.0.0.0"
    backend_port: int = 8002

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()

from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    database_url: str

    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]
    secret_key: str = "my-secret-key"
    algorithm: str = "HS256"
    class Config:
        env_file = ".env"
settings = Settings()
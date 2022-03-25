from pydantic import BaseSettings

class AppSettings(BaseSettings):
    HOST: str
    USER: str
    PASSWORD: str
    PORT: int
    DB: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    JWT_EXPIRATION_IN_MINUTES: int

    class Config:
        env_file = ".env"

settings = AppSettings()
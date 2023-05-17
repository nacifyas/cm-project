from pydantic import BaseSettings, RedisDsn


class Settings(BaseSettings):
    redis_url: RedisDsn
    encoding: str = "UTF-8"
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int = 120

    class Config:
        env_file = ".env"

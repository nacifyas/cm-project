from pydantic import BaseSettings


class Settings(BaseSettings):
    redis_url: str
    encoding: str = "UTF-8"

    class Config:
        env_file = ".env"

from dotenv import load_dotenv
from pydantic import BaseSettings


class Settings(BaseSettings):
    time_out: int


load_dotenv(".env")
settings = Settings()

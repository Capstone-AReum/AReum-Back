import os
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv()

class Settings():
    DB_USER = os.environ.get("DB_USER")
    DB_URL = os.environ.get("DB_URL")
    DB_PASS = os.environ.get("DB_PASS")
    DB_NAME = os.environ.get("DB_NAME")
    DB_PORT = int(os.environ.get("DB_PORT"))

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # target vector DB (ultimate_advisor)
    APP_PG_HOST = os.getenv("APP_PG_HOST", "localhost")
    APP_PG_USER = os.getenv("APP_PG_USER", "postgres")
    APP_PG_PASSWORD = os.getenv("APP_PG_PASSWORD", "postgres")
    APP_PG_DATABASE = os.getenv("APP_PG_DATABASE", "ultimate_advisor")
    APP_PG_PORT = int(os.getenv("APP_PG_PORT", "5432"))

    # origin DB (PTHSP)
    ORIGIN_DB_HOST = os.getenv("ORIGIN_DB_HOST", "localhost")
    ORIGIN_DB_PORT = int(os.getenv("ORIGIN_DB_PORT", "5432"))
    ORIGIN_DB_NAME = os.getenv("ORIGIN_DB_NAME", "PTHSP")
    ORIGIN_DB_USER = os.getenv("ORIGIN_DB_USER", "postgres")
    ORIGIN_DB_PASSWORD = os.getenv("ORIGIN_DB_PASSWORD", "postgres")

    # embedding model
    APP_EMBEDDING_MODEL = os.getenv("APP_EMBEDDING_MODEL", "qwen3-embedding:latest")

    # ollama
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434")


settings = Settings()
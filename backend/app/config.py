from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from functools import lru_cache

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    neo4j_uri: str
    neo4j_user: str
    neo4j_password: SecretStr

    ollama_base_url: str
    ollama_chat_model: str = "qwen3:8b"
    ollama_embed_model: str = "bge-m3"

    dart_api_key: SecretStr
@lru_cache
def get_settings() -> Settings:
    return Settings()
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from dotenv import load_dotenv
import os
load_dotenv(override=True)
DOTENV = os.path.join(os.path.dirname(__file__), ".env")
class Settings(BaseSettings):
    token: SecretStr
    connection_string: SecretStr
    redis_storage: SecretStr
    provider_token: SecretStr
    model_config = SettingsConfigDict(env_file=DOTENV, env_file_encoding='utf-8')
config = Settings()
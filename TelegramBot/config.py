from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
class Settings(BaseSettings):
    token: SecretStr
    connection_string: SecretStr
    model_config = SettingsConfigDict(env_file='/home/yalublushreka/PycharmProjects/megafon_analytics/TelegramBot/.env', env_file_encoding='utf-8')
config = Settings()
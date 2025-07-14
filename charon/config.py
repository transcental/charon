from pydantic import PostgresDsn
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class SlackConfig(BaseSettings):
    bot_token: str
    signing_secret: str
    app_token: str | None
    xoxc_token: str
    xoxd_token: str
    heartbeat_channel: str | None = None
    applications_channel: str


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_nested_delimiter="__")
    slack: SlackConfig
    database_url: PostgresDsn
    environment: str = "development"
    port: int = 3000
    secret_key: str


config = Config()  # type: ignore

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class VisitSchedulerSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="VISIT_SCHEDULER_", env_file=".env", env_file_encoding="utf-8")

    LOG_LEVEL: str = "INFO"
    ROOT_PATH: str = ""


kafka_authentication_scheme_t = Literal["oauth", "none"]


class KafkaSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="KAFKA_", env_file=".env", env_file_encoding="utf-8")

    TOPIC: str
    BOOTSTRAP_URL: str
    AUTHENTICATION_SCHEME: kafka_authentication_scheme_t = "none"


class ElasticsearchSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ES_", env_file=".env", env_file_encoding="utf-8")

    HOST: str
    LOGIN: str
    PASS: str
    CACERT_PATH: str | None = None

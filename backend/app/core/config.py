from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "development"
    app_debug: bool = False
    app_port: int = 8000

    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "app_db"
    database_user: str = "postgres"
    database_password: str = "changeme"

    azure_ad_tenant_id: str = ""
    azure_ad_client_id: str = ""
    azure_ad_client_secret: str = ""

    auth_dev_bypass: bool = False
    auth_dev_token: str = ""

    applicationinsights_connection_string: str = ""

    feature_flags_enabled: bool = False

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


settings = Settings()

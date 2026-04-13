from pydantic_settings import BaseSettings, SettingsConfigDict


class SecuritySettings(BaseSettings):
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str
    jwt_secret: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 1 week

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


security_settings = SecuritySettings()

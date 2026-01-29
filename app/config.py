"""Configuration management for the MySQL Analytical Agent."""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # MySQL Configuration
    mysql_host: str = Field(default="", description="MySQL host")
    mysql_port: int = Field(default="", description="MySQL port")
    mysql_user: str = Field(default="", description="MySQL username")
    mysql_password: str = Field(default="", description="MySQL password")
    mysql_database: str = Field(default="", description="MySQL database name")

    # OpenAI Configuration
    # openai_api_key: str = Field(description="OpenAI API key")
    # openai_model: str = Field(
    #     default="gpt-4-turbo-preview", description="OpenAI model to use")

    # Azure OpenAI (PRIMARY)
    azure_ai_endpoint: str = Field(
        default="", description="Azure OpenAI endpoint")
    azure_ai_api_key: str = Field(
        default="", description="Azure OpenAI API key")
    azure_openai_deployment: str = Field(
        default="", description="Azure OpenAI deployment name")
    azure_ai_api_version: str = Field(
        default="", description="Azure OpenAI API version")

    # Application Configuration
    app_host: str = Field(default="", description="Application host")
    app_port: int = Field(default="", description="Application port")
    app_debug: bool = Field(default=False, description="Debug mode")

    # JWT Configuration
    jwt_secret_key: str = Field(
        default="change-me-in-prod", description="JWT secret key for signing tokens")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")

    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: str = Field(default="logs/app.log", description="Log file path")

    # CORS Configuration
    cors_allow_origins: str = Field(
        default="",
        description="Comma-separated list of allowed origins for CORS"
    )
    cors_allow_credentials: bool = Field(
        default=True,
        description="Allow credentials in CORS requests"
    )
    cors_allow_methods: str = Field(
        default="*",
        description="Allowed HTTP methods for CORS"
    )
    cors_allow_headers: str = Field(
        default="*",
        description="Allowed headers for CORS requests"
    )

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()

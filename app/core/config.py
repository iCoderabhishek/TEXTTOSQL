from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    GOOGLE_API_KEY: str
    GEMINI_MODEL: str = "gemini-3.6-flash"
    GROQ_API_KEY: str
    GROQ_MODEL: str = "qwen/qwen3.6-27b"
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION_NAME: str = "us-east-1"
    BEDROCK_MODEL_ID: str = "us.meta.llama3-3-70b-instruct-v1:0"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

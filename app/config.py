from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLM_MODEL: str = "llama3.2:3b"
    EMBED_MODEL: str = "nomic-embed-text"
    CHROMA_DIR: str = "./chroma_db"

    # LLM failover: providers are tried in this order
    LLM_PROVIDERS: str = "ollama"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4.1-mini"
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.5-flash"
    # optional: a Groq vision-capable model name (leave empty to skip Groq for images)
    GROQ_VISION_MODEL: str = ""
    MAX_UPLOAD_MB: int = 5

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
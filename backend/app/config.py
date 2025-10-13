from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # Database
    DATABASE_URL: str = "mysql+aiomysql://searchuser:searchpass@localhost:3306/searchpilot"
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    # Application
    APP_NAME: str = "SearchPilot"
    APP_VERSION: str = "1.0.0"
    LOG_LEVEL: str = "INFO"
    
    # Search
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    AUTOCOMPLETE_LIMIT: int = 10
    SUGGESTIONS_LIMIT: int = 5
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


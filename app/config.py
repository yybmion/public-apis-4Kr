"""
Configuration Management System
Stock Intelligence System
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application Settings"""

    # Application
    APP_ENV: str = Field(default="development", description="Application environment")
    DEBUG: bool = Field(default=True, description="Debug mode")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    # API Server
    API_HOST: str = Field(default="0.0.0.0", description="API host")
    API_PORT: int = Field(default=8000, description="API port")
    DASHBOARD_PORT: int = Field(default=8501, description="Dashboard port")

    # Database - Supabase (PostgreSQL)
    SUPABASE_URL: str = Field(
        default="https://your-project.supabase.co",
        description="Supabase project URL"
    )
    SUPABASE_KEY: str = Field(
        default="",
        description="Supabase anon/service key"
    )
    SUPABASE_DB_URL: str = Field(
        default="postgresql://postgres:password@db.your-project.supabase.co:5432/postgres",
        description="Supabase PostgreSQL direct connection URL"
    )
    # Legacy support - falls back to Supabase URL
    DATABASE_URL: Optional[str] = Field(
        default=None,
        description="PostgreSQL connection URL (legacy, use SUPABASE_DB_URL)"
    )
    DB_POOL_SIZE: int = Field(default=5, description="Database connection pool size")
    DB_MAX_OVERFLOW: int = Field(default=10, description="Database max overflow")

    # Redis Cache
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    REDIS_TTL: int = Field(default=3600, description="Redis cache TTL in seconds")

    # 한국투자증권 KIS API
    KIS_APP_KEY: str = Field(default="", description="KIS API App Key")
    KIS_APP_SECRET: str = Field(default="", description="KIS API App Secret")
    KIS_BASE_URL: str = Field(
        default="https://openapi.koreainvestment.com:9443",
        description="KIS API base URL"
    )

    # DART (전자공시시스템) API
    DART_API_KEY: str = Field(default="", description="DART API Key")
    DART_BASE_URL: str = Field(
        default="https://opendart.fss.or.kr/api",
        description="DART API base URL"
    )

    # 한국은행 ECOS API
    ECOS_API_KEY: str = Field(default="", description="ECOS API Key")
    ECOS_BASE_URL: str = Field(
        default="https://ecos.bok.or.kr/api",
        description="ECOS API base URL"
    )

    # Upstage Document AI (OCR)
    UPSTAGE_API_KEY: str = Field(default="", description="Upstage API Key")
    UPSTAGE_BASE_URL: str = Field(
        default="https://api.upstage.ai/v1",
        description="Upstage API base URL"
    )

    # CLOVA Studio API
    CLOVA_API_KEY: str = Field(default="", description="CLOVA API Key")
    CLOVA_API_GATEWAY: str = Field(default="", description="CLOVA API Gateway URL")

    # Kakao API (Notification)
    KAKAO_REST_API_KEY: str = Field(default="", description="Kakao REST API Key")
    KAKAO_ACCESS_TOKEN: str = Field(default="", description="Kakao Access Token")
    KAKAO_BASE_URL: str = Field(
        default="https://kapi.kakao.com",
        description="Kakao API base URL"
    )

    # BigKinds API (뉴스)
    BIGKINDS_API_KEY: str = Field(default="", description="BigKinds API Key")
    BIGKINDS_BASE_URL: str = Field(
        default="https://www.bigkinds.or.kr/api",
        description="BigKinds API base URL"
    )

    # LLM APIs - Multi-Agent System
    ANTHROPIC_API_KEY: str = Field(default="", description="Anthropic Claude API Key")
    OPENAI_API_KEY: str = Field(default="", description="OpenAI GPT-4 API Key")
    GOOGLE_API_KEY: str = Field(default="", description="Google Gemini API Key")
    XAI_API_KEY: str = Field(default="", description="xAI Grok API Key")

    # AWS Configuration
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, description="AWS Access Key ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, description="AWS Secret Access Key")
    AWS_REGION: str = Field(default="ap-northeast-2", description="AWS Region")
    S3_BUCKET_NAME: str = Field(default="stock-intel-charts", description="S3 bucket name")

    # Security
    SECRET_KEY: str = Field(
        default="your-secret-key-change-this-in-production",
        description="Secret key for JWT"
    )
    ENCRYPTION_KEY: str = Field(
        default="",
        description="Encryption key for sensitive data"
    )

    # Rate Limiting
    API_RATE_LIMIT: int = Field(default=1000, description="API rate limit per hour")
    DAILY_REQUEST_LIMIT: int = Field(default=10000, description="Daily request limit")

    # External API Limits
    UPSTAGE_MONTHLY_LIMIT: int = Field(default=300, description="Upstage monthly free tier limit")
    CLOVA_MONTHLY_LIMIT: int = Field(default=100, description="CLOVA monthly limit")

    # Data Collection
    REALTIME_COLLECTION_INTERVAL: int = Field(default=10, description="Real-time collection interval in seconds")
    MARKET_OPEN_HOUR: int = Field(default=9, description="Market open hour")
    MARKET_CLOSE_HOUR: int = Field(default=15, description="Market close hour")
    MARKET_CLOSE_MINUTE: int = Field(default=30, description="Market close minute")

    # Monitoring
    SENTRY_DSN: Optional[str] = Field(default=None, description="Sentry DSN for error tracking")

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


# Global settings instance
settings = Settings()


def get_database_url() -> str:
    """
    Get database URL with Supabase priority

    Returns:
        Database connection URL
    """
    # Priority: SUPABASE_DB_URL > DATABASE_URL > default
    if settings.SUPABASE_DB_URL and "your-project" not in settings.SUPABASE_DB_URL:
        return settings.SUPABASE_DB_URL
    elif settings.DATABASE_URL:
        return settings.DATABASE_URL
    else:
        # Fallback to default local PostgreSQL
        return "postgresql://stockuser:stockpass@localhost:5432/stockdb"


# Configuration validation
def validate_config():
    """Validate critical configuration"""
    errors = []

    if settings.APP_ENV == "production":
        if settings.SECRET_KEY == "your-secret-key-change-this-in-production":
            errors.append("SECRET_KEY must be changed in production")

        if not settings.KIS_APP_KEY:
            errors.append("KIS_APP_KEY is required")

        if not settings.KIS_APP_SECRET:
            errors.append("KIS_APP_SECRET is required")

    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")

    return True


# Helper functions
def is_production() -> bool:
    """Check if running in production"""
    return settings.APP_ENV == "production"


def is_development() -> bool:
    """Check if running in development"""
    return settings.APP_ENV == "development"


def is_market_hours() -> bool:
    """Check if within market trading hours"""
    from datetime import datetime
    import pytz

    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst)

    # Monday = 0, Friday = 4
    if now.weekday() > 4:  # Weekend
        return False

    market_open = now.replace(hour=settings.MARKET_OPEN_HOUR, minute=0, second=0)
    market_close = now.replace(hour=settings.MARKET_CLOSE_HOUR, minute=settings.MARKET_CLOSE_MINUTE, second=0)

    return market_open <= now <= market_close

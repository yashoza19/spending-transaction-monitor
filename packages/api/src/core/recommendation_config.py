"""Configuration for recommendation generation performance"""

from pydantic_settings import BaseSettings


class RecommendationConfig(BaseSettings):
    """Configuration for recommendation generation"""

    # Thread pool settings
    llm_thread_pool_workers: int = 4

    # Parallel processing settings
    max_concurrent_users: int = 10
    batch_size: int = 50

    # Rate limiting
    max_recommendations_per_minute: int = 100

    # Cache settings
    cache_duration_hours: int = 24

    # Scheduler settings
    scheduler_interval_hours: int = 6
    active_user_days: int = 7

    # Performance monitoring
    enable_performance_metrics: bool = True

    class Config:
        env_prefix = 'RECOMMENDATION_'
        case_sensitive = False


# Global configuration instance
recommendation_config = RecommendationConfig()

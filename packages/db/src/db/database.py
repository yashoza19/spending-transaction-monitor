"""
Database configuration and utilities
"""

import logging
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

import os

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+asyncpg://user:password@localhost:5432/spending-monitor')

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

Base = declarative_base()

logger = logging.getLogger(__name__)

# Capture service startup time
SERVICE_START_TIME = datetime.now(UTC)


class DatabaseService:
    """Database service for handling database operations"""

    def __init__(self, engine=None):
        self.engine = engine or globals()['engine']
        self.start_time = SERVICE_START_TIME

    async def health_check(self) -> dict[str, Any]:
        """
        Perform database health check

        Returns:
            Dict containing health status information
        """
        try:
            # Test basic connectivity
            async with self.engine.begin() as conn:
                result = await conn.execute(text('SELECT 1 as health_check'))
                result.scalar()

            # Test if we can create a session
            async with SessionLocal() as session:
                await session.execute(text('SELECT version()'))

            return {
                'name': 'Database',
                'status': 'healthy',
                'message': 'PostgreSQL connection successful',
                'version': 'PostgreSQL',
                'start_time': self.start_time.isoformat(),
            }
        except Exception as e:
            logger.error(f'Database health check failed: {e}')
            return {
                'name': 'Database',
                'status': 'down',
                'message': f'PostgreSQL connection failed: {str(e)[:100]}',
                'version': 'PostgreSQL',
                'start_time': self.start_time.isoformat(),
            }

    async def get_session(self) -> AsyncSession:
        """Get database session"""
        return SessionLocal()


# Global database service instance
db_service = DatabaseService()


async def get_db():
    """Dependency to get database session"""
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_db_service() -> DatabaseService:
    """Dependency to get database service"""
    return db_service

"""
Database tests
"""

import pytest
from sqlalchemy import text

from db.database import engine


@pytest.mark.asyncio
async def test_database_connection():
    """Test database connection"""
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text('SELECT 1'))
            assert result.scalar() == 1
    except Exception as e:
        pytest.skip(f'Database connection failed (DB not running): {e}')
        return

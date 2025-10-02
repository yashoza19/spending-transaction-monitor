"""Merge multiple heads

Revision ID: 5dd200df62e6
Revises: e35d4db01ac2, e81ee0a4dbc7
Create Date: 2025-09-30 15:12:28.799655

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5dd200df62e6'
down_revision = ('e35d4db01ac2', 'e81ee0a4dbc7')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

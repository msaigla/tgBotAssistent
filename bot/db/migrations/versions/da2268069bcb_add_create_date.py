"""add create_date

Revision ID: da2268069bcb
Revises: b2f8962fd6f0
Create Date: 2025-05-13 18:44:48.554248

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'da2268069bcb'
down_revision: Union[str, None] = 'b2f8962fd6f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('chat_histories', sa.Column('create_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False))
    op.create_unique_constraint(None, 'users', ['chat_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='unique')
    op.drop_column('chat_histories', 'create_at')
    # ### end Alembic commands ###

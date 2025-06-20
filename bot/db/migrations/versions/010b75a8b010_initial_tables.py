"""initial tables

Revision ID: 010b75a8b010
Revises: 
Create Date: 2025-05-30 23:52:54.722298

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '010b75a8b010'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('chat_histories',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('chat_id', sa.BigInteger(), nullable=True),
    sa.Column('role', sa.String(length=32), nullable=True),
    sa.Column('message', sa.String(), nullable=False),
    sa.Column('create_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc+3', now())"), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_permissions',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('login', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('chat_id', sa.BigInteger(), nullable=False),
    sa.Column('username', sa.String(length=32), nullable=True),
    sa.Column('gender', sa.String(length=32), nullable=False),
    sa.Column('city', sa.String(length=128), nullable=True),
    sa.Column('where_practicing', sa.String(length=128), nullable=True),
    sa.Column('were_clients', sa.String(length=128), nullable=True),
    sa.Column('massage_technique', sa.String(length=128), nullable=True),
    sa.Column('using_social', sa.String(length=128), nullable=True),
    sa.Column('lang', sa.String(length=32), nullable=False),
    sa.Column('row_sheet', sa.String(length=32), nullable=True),
    sa.Column('number_of_days', sa.Integer(), nullable=False),
    sa.Column('trial', sa.Integer(), nullable=False),
    sa.Column('premium', sa.Date(), server_default=sa.text("TIMEZONE('utc+3', now())"), nullable=False),
    sa.Column('create_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc+3', now())"), nullable=False),
    sa.Column('update_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc+3', now())"), nullable=False),
    sa.PrimaryKeyConstraint('chat_id'),
    sa.UniqueConstraint('chat_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    op.drop_table('user_permissions')
    op.drop_table('chat_histories')
    # ### end Alembic commands ###

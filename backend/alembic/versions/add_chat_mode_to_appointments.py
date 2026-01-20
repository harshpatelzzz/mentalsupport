"""add chat_mode to appointments

Revision ID: add_chat_mode
Revises: 
Create Date: 2026-01-20 12:25:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_chat_mode'
down_revision = None
depends_on = None


def upgrade():
    # Add chat_mode column to appointments table
    op.add_column('appointments', 
        sa.Column('chat_mode', 
            sa.Enum('BOT_ONLY', 'THERAPIST_JOINED', name='chatmode'), 
            nullable=False, 
            server_default='BOT_ONLY'
        )
    )


def downgrade():
    # Remove chat_mode column
    op.drop_column('appointments', 'chat_mode')
    # Drop the enum type
    op.execute('DROP TYPE chatmode')

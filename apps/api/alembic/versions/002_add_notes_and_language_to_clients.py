"""add_notes_and_language_to_clients

Revision ID: 002
Revises: 001
Create Date: 2025-10-03

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add notes and language columns to clients table"""
    op.add_column('clients', sa.Column('notes', sa.Text(), nullable=True))
    op.add_column('clients', sa.Column('language', sa.String(length=50), nullable=True))


def downgrade() -> None:
    """Remove notes and language columns from clients table"""
    op.drop_column('clients', 'language')
    op.drop_column('clients', 'notes')

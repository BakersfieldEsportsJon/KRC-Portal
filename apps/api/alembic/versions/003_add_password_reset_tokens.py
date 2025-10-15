"""Add password reset tokens table and user fields

Revision ID: 003
Revises: 002
Create Date: 2025-10-15

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # Create password_reset_tokens table
    op.create_table(
        'password_reset_tokens',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token', sa.String(255), nullable=False, unique=True),
        sa.Column('token_type', sa.String(20), nullable=False),  # 'setup' or 'reset'
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('used_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Index('idx_password_reset_tokens_token', 'token'),
        sa.Index('idx_password_reset_tokens_user_id', 'user_id'),
    )

    # Add password_setup_required field to users table
    op.add_column('users', sa.Column('password_setup_required', sa.Boolean(), nullable=False, server_default='false'))

    # Add last_password_change field to users table
    op.add_column('users', sa.Column('last_password_change', sa.DateTime(), nullable=True))


def downgrade():
    # Remove columns from users table
    op.drop_column('users', 'last_password_change')
    op.drop_column('users', 'password_setup_required')

    # Drop password_reset_tokens table
    op.drop_table('password_reset_tokens')

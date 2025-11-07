"""Add password_setup_required flag to users

Revision ID: 004
Revises: 003
Create Date: 2024-05-18

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column['name'] for column in inspector.get_columns('users')}

    if 'password_setup_required' not in columns:
        op.add_column(
            'users',
            sa.Column(
                'password_setup_required',
                sa.Boolean(),
                nullable=False,
                server_default=sa.true(),
            ),
        )
    else:
        op.alter_column(
            'users',
            'password_setup_required',
            existing_type=sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        )


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column['name'] for column in inspector.get_columns('users')}

    if 'password_setup_required' in columns:
        op.drop_column('users', 'password_setup_required')

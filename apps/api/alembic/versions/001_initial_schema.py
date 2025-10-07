"""Initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-01 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('mfa_secret', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_users')),
        sa.UniqueConstraint('email', name=op.f('uq_users_email'))
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)

    # Create clients table
    op.create_table('clients',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('external_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_clients'))
    )
    op.create_index(op.f('ix_clients_first_name'), 'clients', ['first_name'], unique=False)
    op.create_index(op.f('ix_clients_last_name'), 'clients', ['last_name'], unique=False)
    op.create_index(op.f('ix_clients_email'), 'clients', ['email'], unique=False)
    op.create_index(op.f('ix_clients_phone'), 'clients', ['phone'], unique=False)

    # Create tags table
    op.create_table('tags',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_tags')),
        sa.UniqueConstraint('name', name=op.f('uq_tags_name'))
    )
    op.create_index(op.f('ix_tags_name'), 'tags', ['name'], unique=False)

    # Create client_tags association table
    op.create_table('client_tags',
        sa.Column('client_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tag_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], name=op.f('fk_client_tags_client_id_clients')),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], name=op.f('fk_client_tags_tag_id_tags')),
        sa.PrimaryKeyConstraint('client_id', 'tag_id', name=op.f('pk_client_tags'))
    )

    # Create contact_methods table
    op.create_table('contact_methods',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('client_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.String(length=20), nullable=False),
        sa.Column('value', sa.String(length=255), nullable=False),
        sa.Column('verified', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], name=op.f('fk_contact_methods_client_id_clients')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_contact_methods'))
    )

    # Create consents table
    op.create_table('consents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('client_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('kind', sa.String(length=20), nullable=False),
        sa.Column('granted', sa.Boolean(), nullable=False),
        sa.Column('granted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('source', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], name=op.f('fk_consents_client_id_clients')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_consents'))
    )

    # Create memberships table
    op.create_table('memberships',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('client_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('plan_code', sa.String(length=50), nullable=False),
        sa.Column('starts_on', sa.Date(), nullable=False),
        sa.Column('ends_on', sa.Date(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], name=op.f('fk_memberships_client_id_clients')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_memberships'))
    )
    op.create_index(op.f('ix_memberships_plan_code'), 'memberships', ['plan_code'], unique=False)
    op.create_index(op.f('ix_memberships_ends_on'), 'memberships', ['ends_on'], unique=False)

    # Create check_ins table
    op.create_table('check_ins',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('client_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('method', sa.Enum('KIOSK', 'STAFF', name='checkinmethod'), nullable=False),
        sa.Column('station', sa.String(length=100), nullable=True),
        sa.Column('happened_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], name=op.f('fk_check_ins_client_id_clients')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_check_ins'))
    )
    op.create_index(op.f('ix_check_ins_happened_at'), 'check_ins', ['happened_at'], unique=False)

    # Create webhooks_out table
    op.create_table('webhooks_out',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event', sa.String(length=100), nullable=False),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('status', sa.Enum('QUEUED', 'SENT', 'FAILED', name='webhookstatus'), nullable=False),
        sa.Column('attempt_count', sa.Integer(), nullable=False),
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.Column('zap_run_id', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_webhooks_out'))
    )
    op.create_index(op.f('ix_webhooks_out_event'), 'webhooks_out', ['event'], unique=False)
    op.create_index(op.f('ix_webhooks_out_status'), 'webhooks_out', ['status'], unique=False)

    # Create ggleap_links table
    op.create_table('ggleap_links',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('client_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ggleap_user_id', sa.String(length=100), nullable=False),
        sa.Column('linked_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], name=op.f('fk_ggleap_links_client_id_clients')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_ggleap_links'))
    )
    op.create_index(op.f('ix_ggleap_links_ggleap_user_id'), 'ggleap_links', ['ggleap_user_id'], unique=False)

    # Create ggleap_groups table
    op.create_table('ggleap_groups',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('map_key', sa.Enum('ACTIVE', 'EXPIRED', name='ggleapgrouptype'), nullable=False),
        sa.Column('ggleap_group_id', sa.String(length=100), nullable=False),
        sa.Column('group_name', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_ggleap_groups')),
        sa.UniqueConstraint('map_key', name=op.f('uq_ggleap_groups_map_key'))
    )

    # Create audit_log table
    op.create_table('audit_log',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('actor_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('entity', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.String(length=100), nullable=False),
        sa.Column('diff', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['actor_user_id'], ['users.id'], name=op.f('fk_audit_log_actor_user_id_users')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_audit_log'))
    )
    op.create_index(op.f('ix_audit_log_action'), 'audit_log', ['action'], unique=False)
    op.create_index(op.f('ix_audit_log_entity'), 'audit_log', ['entity'], unique=False)
    op.create_index(op.f('ix_audit_log_entity_id'), 'audit_log', ['entity_id'], unique=False)
    op.create_index(op.f('ix_audit_log_at'), 'audit_log', ['at'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('audit_log')
    op.drop_table('ggleap_groups')
    op.drop_table('ggleap_links')
    op.drop_table('webhooks_out')
    op.drop_table('check_ins')
    op.drop_table('memberships')
    op.drop_table('consents')
    op.drop_table('contact_methods')
    op.drop_table('client_tags')
    op.drop_table('tags')
    op.drop_table('clients')
    op.drop_table('users')

    # Drop enums
    op.execute("DROP TYPE IF EXISTS ggleapgrouptype")
    op.execute("DROP TYPE IF EXISTS webhookstatus")
    op.execute("DROP TYPE IF EXISTS checkinmethod")
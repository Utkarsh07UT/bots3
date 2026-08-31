"""add notifications tables

Revision ID: b2c3d4e5f6a7
Revises: a8bc5c95cf75
Create Date: 2026-08-30 01:42:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'a8bc5c95cf75'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'notification_preferences',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('min_severity', sa.String(length=20), nullable=False, server_default='MEDIUM'),
        sa.Column('notify_critical', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('notify_high', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('notify_medium', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('notify_low', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('quiet_hours_enabled', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('quiet_hours_start_utc', sa.Integer(), nullable=False, server_default='22'),
        sa.Column('quiet_hours_end_utc', sa.Integer(), nullable=False, server_default='6'),
        sa.Column('rate_limit_per_hour', sa.Integer(), nullable=False, server_default='20'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    op.create_table(
        'notification_logs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('alert_id', sa.String(length=64), nullable=True),
        sa.Column('recipient', sa.String(length=255), nullable=False),
        sa.Column('channel', sa.String(length=32), nullable=False, server_default='email'),
        sa.Column('provider', sa.String(length=32), nullable=False, server_default='smtp'),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('subject', sa.String(length=255), nullable=True),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('notification_logs')
    op.drop_table('notification_preferences')

"""Alembic: organization API keys + events (JSONB, indexes, processing status)."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260520_0002"
down_revision: str | None = "20260520_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE event_processing_status_enum AS ENUM "
        "('pending', 'processing', 'completed', 'failed')"
    )

    status_type = postgresql.ENUM(
        "pending",
        "processing",
        "completed",
        "failed",
        name="event_processing_status_enum",
        create_type=False,
    )

    op.create_table(
        "organization_api_keys",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("key_hash", sa.String(length=64), nullable=False),
        sa.Column("key_prefix", sa.String(length=16), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="CASCADE",
            name="fk_organization_api_keys_organization_id_organizations",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_organization_api_keys"),
        sa.UniqueConstraint("key_hash", name="uq_organization_api_keys_key_hash"),
    )
    op.create_index(
        "ix_organization_api_keys_key_hash",
        "organization_api_keys",
        ["key_hash"],
        unique=False,
    )
    op.create_index(
        "ix_organization_api_keys_key_prefix",
        "organization_api_keys",
        ["key_prefix"],
        unique=False,
    )
    op.create_index(
        "ix_organization_api_keys_organization_id",
        "organization_api_keys",
        ["organization_id"],
        unique=False,
    )
    op.create_index(
        "ix_organization_api_keys_created_at",
        "organization_api_keys",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        "ix_organization_api_keys_updated_at",
        "organization_api_keys",
        ["updated_at"],
        unique=False,
    )

    op.create_table(
        "events",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_name", sa.String(length=255), nullable=False),
        sa.Column("event_type", sa.String(length=120), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("normalized_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source", sa.String(length=255), nullable=False),
        sa.Column(
            "processing_status",
            status_type,
            nullable=False,
            server_default=sa.text("'pending'::event_processing_status_enum"),
        ),
        sa.Column("celery_task_id", sa.String(length=255), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("processing_attempts", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="CASCADE",
            name="fk_events_organization_id_organizations",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_events"),
    )
    op.create_index("ix_events_organization_id", "events", ["organization_id"], unique=False)
    op.create_index("ix_events_event_type", "events", ["event_type"], unique=False)
    op.create_index("ix_events_timestamp", "events", ["timestamp"], unique=False)
    op.create_index("ix_events_celery_task_id", "events", ["celery_task_id"], unique=False)
    op.create_index(
        "ix_events_organization_id_timestamp",
        "events",
        ["organization_id", "timestamp"],
        unique=False,
    )
    op.create_index(
        "ix_events_organization_id_event_type",
        "events",
        ["organization_id", "event_type"],
        unique=False,
    )
    op.create_index("ix_events_created_at", "events", ["created_at"], unique=False)
    op.create_index("ix_events_updated_at", "events", ["updated_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_events_updated_at", table_name="events")
    op.drop_index("ix_events_created_at", table_name="events")
    op.drop_index("ix_events_organization_id_event_type", table_name="events")
    op.drop_index("ix_events_organization_id_timestamp", table_name="events")
    op.drop_index("ix_events_celery_task_id", table_name="events")
    op.drop_index("ix_events_timestamp", table_name="events")
    op.drop_index("ix_events_event_type", table_name="events")
    op.drop_index("ix_events_organization_id", table_name="events")
    op.drop_table("events")

    op.drop_index("ix_organization_api_keys_updated_at", table_name="organization_api_keys")
    op.drop_index("ix_organization_api_keys_created_at", table_name="organization_api_keys")
    op.drop_index("ix_organization_api_keys_organization_id", table_name="organization_api_keys")
    op.drop_index("ix_organization_api_keys_key_prefix", table_name="organization_api_keys")
    op.drop_index("ix_organization_api_keys_key_hash", table_name="organization_api_keys")
    op.drop_table("organization_api_keys")

    op.execute("DROP TYPE IF EXISTS event_processing_status_enum CASCADE")

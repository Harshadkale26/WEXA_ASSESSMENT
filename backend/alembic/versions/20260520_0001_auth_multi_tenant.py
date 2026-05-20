"""Initial schema: organizations, users, refresh_tokens — PostgreSQL, native role enum, JSONB.

Revision ID: 20260520_0001
Revises:
Create Date: 2026-05-20

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260520_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Native PostgreSQL ENUM for user roles (lowercase values match Python Role.value)
    op.execute("CREATE TYPE role_enum AS ENUM ('owner', 'admin', 'analyst', 'viewer')")

    role_column_type = postgresql.ENUM(
        "owner",
        "admin",
        "analyst",
        "viewer",
        name="role_enum",
        create_type=False,
    )

    op.create_table(
        "organizations",
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=140), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("settings", postgresql.JSONB(), nullable=True),
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
        sa.PrimaryKeyConstraint("id", name="pk_organizations"),
        sa.UniqueConstraint("slug", name="uq_organizations_slug"),
    )

    op.create_index(
        "ix_organizations_created_at",
        "organizations",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        "ix_organizations_updated_at",
        "organizations",
        ["updated_at"],
        unique=False,
    )

    op.create_table(
        "users",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", role_column_type, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
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
            name="fk_users_organization_id_organizations",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
        sa.UniqueConstraint("organization_id", "email", name="uq_users_organization_id_email"),
    )

    op.create_index("ix_users_created_at", "users", ["created_at"], unique=False)
    op.create_index("ix_users_updated_at", "users", ["updated_at"], unique=False)
    op.create_index("ix_users_email", "users", ["email"], unique=False)
    op.create_index("ix_users_organization_id", "users", ["organization_id"], unique=False)

    op.create_table(
        "refresh_tokens",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("jti", sa.String(length=64), nullable=False),
        sa.Column("token_hash", sa.String(length=255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
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
            name="fk_refresh_tokens_organization_id_organizations",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
            name="fk_refresh_tokens_user_id_users",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_refresh_tokens"),
        sa.UniqueConstraint("jti", name="uq_refresh_tokens_jti"),
    )

    op.create_index(
        "ix_refresh_tokens_created_at",
        "refresh_tokens",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        "ix_refresh_tokens_updated_at",
        "refresh_tokens",
        ["updated_at"],
        unique=False,
    )
    op.create_index("ix_refresh_tokens_jti", "refresh_tokens", ["jti"], unique=False)
    op.create_index(
        "ix_refresh_tokens_organization_id",
        "refresh_tokens",
        ["organization_id"],
        unique=False,
    )
    op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_refresh_tokens_user_id", table_name="refresh_tokens")
    op.drop_index("ix_refresh_tokens_organization_id", table_name="refresh_tokens")
    op.drop_index("ix_refresh_tokens_jti", table_name="refresh_tokens")
    op.drop_index("ix_refresh_tokens_updated_at", table_name="refresh_tokens")
    op.drop_index("ix_refresh_tokens_created_at", table_name="refresh_tokens")
    op.drop_table("refresh_tokens")

    op.drop_index("ix_users_organization_id", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_updated_at", table_name="users")
    op.drop_index("ix_users_created_at", table_name="users")
    op.drop_table("users")

    op.drop_index("ix_organizations_updated_at", table_name="organizations")
    op.drop_index("ix_organizations_created_at", table_name="organizations")
    op.drop_table("organizations")

    op.execute("DROP TYPE IF EXISTS role_enum CASCADE")

"""Dashboards and widgets with JSONB query_config.

Revision ID: 20260520_0003
Revises: 20260520_0002
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260520_0003"
down_revision: str | None = "20260520_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE widget_type_enum AS ENUM "
        "('line_chart', 'bar_chart', 'kpi_card', 'pie_chart')"
    )

    widget_type = postgresql.ENUM(
        "line_chart",
        "bar_chart",
        "kpi_card",
        "pie_chart",
        name="widget_type_enum",
        create_type=False,
    )

    op.create_table(
        "dashboards",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=True),
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
            ["created_by_id"],
            ["users.id"],
            ondelete="SET NULL",
            name="fk_dashboards_created_by_id_users",
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="CASCADE",
            name="fk_dashboards_organization_id_organizations",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_dashboards"),
        sa.UniqueConstraint("organization_id", "name", name="uq_dashboards_organization_id_name"),
    )
    op.create_index("ix_dashboards_organization_id", "dashboards", ["organization_id"], unique=False)
    op.create_index("ix_dashboards_created_at", "dashboards", ["created_at"], unique=False)
    op.create_index("ix_dashboards_updated_at", "dashboards", ["updated_at"], unique=False)

    op.create_table(
        "widgets",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dashboard_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("widget_type", widget_type, nullable=False),
        sa.Column("query_config", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("layout", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False),
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
            ["dashboard_id"],
            ["dashboards.id"],
            ondelete="CASCADE",
            name="fk_widgets_dashboard_id_dashboards",
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="CASCADE",
            name="fk_widgets_organization_id_organizations",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_widgets"),
    )
    op.create_index("ix_widgets_organization_id", "widgets", ["organization_id"], unique=False)
    op.create_index("ix_widgets_dashboard_id", "widgets", ["dashboard_id"], unique=False)
    op.create_index("ix_widgets_created_at", "widgets", ["created_at"], unique=False)
    op.create_index("ix_widgets_updated_at", "widgets", ["updated_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_widgets_updated_at", table_name="widgets")
    op.drop_index("ix_widgets_created_at", table_name="widgets")
    op.drop_index("ix_widgets_dashboard_id", table_name="widgets")
    op.drop_index("ix_widgets_organization_id", table_name="widgets")
    op.drop_table("widgets")
    op.drop_index("ix_dashboards_updated_at", table_name="dashboards")
    op.drop_index("ix_dashboards_created_at", table_name="dashboards")
    op.drop_index("ix_dashboards_organization_id", table_name="dashboards")
    op.drop_table("dashboards")
    op.execute("DROP TYPE IF EXISTS widget_type_enum CASCADE")

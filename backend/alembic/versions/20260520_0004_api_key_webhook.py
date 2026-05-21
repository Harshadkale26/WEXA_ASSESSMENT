"""API key webhook signing secret column."""

from alembic import op
import sqlalchemy as sa

revision = "20260520_0004"
down_revision = "20260520_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "organization_api_keys",
        sa.Column("webhook_signing_secret", sa.String(length=64), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("organization_api_keys", "webhook_signing_secret")

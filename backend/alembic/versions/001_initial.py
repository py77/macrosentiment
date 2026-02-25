"""Initial schema: indicators, indicator_values, regime_snapshots, fetch_log

Revision ID: 001
Revises:
Create Date: 2026-02-25
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "indicators",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("series_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("frequency", sa.String(), nullable=False, server_default="daily"),
        sa.Column("weight", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("higher_is_bullish", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("unit", sa.String(), server_default=""),
        sa.Column("description", sa.String(), server_default=""),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("series_id"),
    )
    op.create_index("ix_indicators_series_id", "indicators", ["series_id"])
    op.create_index("ix_indicators_category", "indicators", ["category"])

    op.create_table(
        "indicator_values",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("indicator_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("z_score", sa.Float(), nullable=True),
        sa.Column("percentile", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["indicator_id"], ["indicators.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("indicator_id", "date", name="uq_indicator_date"),
    )
    op.create_index("ix_indicator_values_indicator_id", "indicator_values", ["indicator_id"])
    op.create_index("ix_indicator_values_date", "indicator_values", ["date"])

    op.create_table(
        "regime_snapshots",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("regime", sa.String(), nullable=False),
        sa.Column("growth_score", sa.Float(), nullable=False),
        sa.Column("inflation_score", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("composite_score", sa.Float(), nullable=False),
        sa.Column("component_scores", JSONB(), server_default="{}"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("date"),
    )
    op.create_index("ix_regime_snapshots_date", "regime_snapshots", ["date"])

    op.create_table(
        "fetch_log",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("series_id", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("records_added", sa.Integer(), server_default="0"),
        sa.Column("error_message", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("fetch_log")
    op.drop_table("regime_snapshots")
    op.drop_table("indicator_values")
    op.drop_table("indicators")

"""Persist practice recording metadata."""

from alembic import op
import sqlalchemy as sa

revision = "002_practice_recordings"
down_revision = "001_practice_sessions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "recordings",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "practice_session_id",
            sa.String(36),
            sa.ForeignKey("practice_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "practice_segment_id",
            sa.String(36),
            sa.ForeignKey("practice_segments.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("passage_definition_id", sa.String(36), nullable=True),
        sa.Column("recording_number", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("storage_key", sa.String(1024), nullable=True, unique=True),
        sa.Column("original_mime_type", sa.String(255), nullable=True),
        sa.Column("size_bytes", sa.BigInteger(), nullable=True),
        sa.Column("sha256_checksum", sa.String(64), nullable=True),
        sa.Column("sample_rate_hz", sa.Integer(), nullable=True),
        sa.Column("channel_count", sa.Integer(), nullable=True),
        sa.Column("microphone_label", sa.String(255), nullable=True),
        sa.Column("removal_reason", sa.String(64), nullable=True),
        sa.Column("removed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("practice_session_id", "recording_number", name="uq_recordings_session_number"),
        sa.CheckConstraint(
            "status IN ('capturing', 'saved', 'processing', 'ready', 'invalid', 'removed', 'failed')",
            name="ck_recordings_status",
        ),
        sa.CheckConstraint("recording_number > 0", name="ck_recordings_number_positive"),
        sa.CheckConstraint("duration_ms IS NULL OR duration_ms >= 0", name="ck_recordings_duration_nonnegative"),
        sa.CheckConstraint("size_bytes IS NULL OR size_bytes >= 0", name="ck_recordings_size_nonnegative"),
        sa.CheckConstraint("sample_rate_hz IS NULL OR sample_rate_hz > 0", name="ck_recordings_sample_rate_positive"),
        sa.CheckConstraint("channel_count IS NULL OR channel_count > 0", name="ck_recordings_channel_count_positive"),
        sa.CheckConstraint(
            "(status = 'removed' AND removed_at IS NOT NULL) OR status != 'removed'",
            name="ck_recordings_removed_at",
        ),
    )
    op.create_index("ix_recordings_practice_session_id", "recordings", ["practice_session_id"])
    op.create_index("ix_recordings_practice_segment_id", "recordings", ["practice_segment_id"])
    op.create_index("ix_recordings_status", "recordings", ["status"])


def downgrade() -> None:
    op.drop_index("ix_recordings_status", table_name="recordings")
    op.drop_index("ix_recordings_practice_segment_id", table_name="recordings")
    op.drop_index("ix_recordings_practice_session_id", table_name="recordings")
    op.drop_table("recordings")

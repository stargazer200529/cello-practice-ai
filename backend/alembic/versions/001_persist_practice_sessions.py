"""Persist practice sessions and initial segments."""

from alembic import op
import sqlalchemy as sa

revision = "001_practice_sessions"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "practice_sessions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("piece_id", sa.String(36), sa.ForeignKey("pieces.id", ondelete="CASCADE"), nullable=False),
        sa.Column("instrument_profile_id", sa.String(36), nullable=True),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("practice_source", sa.String(32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("elapsed_seconds", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("target_duration_seconds", sa.Integer(), nullable=True),
        sa.Column("session_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("status IN ('active', 'completed', 'abandoned', 'interrupted')", name="ck_practice_sessions_status"),
        sa.CheckConstraint("elapsed_seconds >= 0", name="ck_practice_sessions_elapsed_nonnegative"),
        sa.CheckConstraint("target_duration_seconds IS NULL OR target_duration_seconds > 0", name="ck_practice_sessions_target_positive"),
        sa.CheckConstraint(
            "(status = 'active' AND ended_at IS NULL) OR (status != 'active' AND ended_at IS NOT NULL)",
            name="ck_practice_sessions_status_end_time",
        ),
    )
    op.create_index("ix_practice_sessions_user_id", "practice_sessions", ["user_id"])
    op.create_index("ix_practice_sessions_piece_id", "practice_sessions", ["piece_id"])
    op.create_index("ix_practice_sessions_status", "practice_sessions", ["status"])
    op.create_table(
        "practice_segments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("practice_session_id", sa.String(36), sa.ForeignKey("practice_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("passage_definition_id", sa.String(36), nullable=True),
        sa.Column("focus_codes", sa.JSON(), nullable=False),
        sa.Column("sequence_number", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("target_tempo_bpm", sa.Numeric(6, 2), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("practice_session_id", "sequence_number", name="uq_practice_segments_session_sequence"),
        sa.CheckConstraint("sequence_number >= 0", name="ck_practice_segments_sequence_nonnegative"),
        sa.CheckConstraint("target_tempo_bpm IS NULL OR target_tempo_bpm > 0", name="ck_practice_segments_tempo_positive"),
    )
    op.create_index("ix_practice_segments_practice_session_id", "practice_segments", ["practice_session_id"])


def downgrade() -> None:
    op.drop_index("ix_practice_segments_practice_session_id", table_name="practice_segments")
    op.drop_table("practice_segments")
    op.drop_index("ix_practice_sessions_status", table_name="practice_sessions")
    op.drop_index("ix_practice_sessions_piece_id", table_name="practice_sessions")
    op.drop_index("ix_practice_sessions_user_id", table_name="practice_sessions")
    op.drop_table("practice_sessions")

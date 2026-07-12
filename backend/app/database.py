from collections.abc import Iterator
from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    create_engine,
    event,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker


class Base(DeclarativeBase):
    pass


class PieceEntity(Base):
    __tablename__ = "pieces"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    composer: Mapped[str | None] = mapped_column(String(500), nullable=True)
    original_filename: Mapped[str] = mapped_column(String(500))
    musicxml_path: Mapped[str] = mapped_column(String(1000), unique=True)
    part_names: Mapped[list[str]] = mapped_column(JSON)
    measure_count: Mapped[int] = mapped_column(Integer)
    time_signatures: Mapped[list[str]] = mapped_column(JSON)
    key_signatures: Mapped[list[str]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    archived: Mapped[bool] = mapped_column(Boolean, default=False)


class PracticeSessionEntity(Base):
    __tablename__ = "practice_sessions"
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'completed', 'abandoned', 'interrupted')",
            name="ck_practice_sessions_status",
        ),
        CheckConstraint("elapsed_seconds >= 0", name="ck_practice_sessions_elapsed_nonnegative"),
        CheckConstraint(
            "target_duration_seconds IS NULL OR target_duration_seconds > 0",
            name="ck_practice_sessions_target_positive",
        ),
        CheckConstraint(
            "(status = 'active' AND ended_at IS NULL) OR (status != 'active' AND ended_at IS NOT NULL)",
            name="ck_practice_sessions_status_end_time",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), index=True)
    piece_id: Mapped[str] = mapped_column(ForeignKey("pieces.id", ondelete="CASCADE"), index=True)
    instrument_profile_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    practice_source: Mapped[str] = mapped_column(String(32))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    elapsed_seconds: Mapped[int] = mapped_column(Integer, default=0)
    target_duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    session_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    segments: Mapped[list["PracticeSegmentEntity"]] = relationship(
        back_populates="practice_session", cascade="all, delete-orphan", order_by="PracticeSegmentEntity.sequence_number"
    )
    recordings: Mapped[list["RecordingEntity"]] = relationship(
        back_populates="practice_session", cascade="all, delete-orphan", order_by="RecordingEntity.recording_number"
    )


class PracticeSegmentEntity(Base):
    __tablename__ = "practice_segments"
    __table_args__ = (
        UniqueConstraint("practice_session_id", "sequence_number", name="uq_practice_segments_session_sequence"),
        CheckConstraint("sequence_number >= 0", name="ck_practice_segments_sequence_nonnegative"),
        CheckConstraint(
            "target_tempo_bpm IS NULL OR target_tempo_bpm > 0", name="ck_practice_segments_tempo_positive"
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    practice_session_id: Mapped[str] = mapped_column(
        ForeignKey("practice_sessions.id", ondelete="CASCADE"), index=True
    )
    passage_definition_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    focus_codes: Mapped[list[str]] = mapped_column(JSON, default=list)
    sequence_number: Mapped[int] = mapped_column(Integer)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    target_tempo_bpm: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    practice_session: Mapped[PracticeSessionEntity] = relationship(back_populates="segments")
    recordings: Mapped[list["RecordingEntity"]] = relationship(back_populates="practice_segment")


class RecordingEntity(Base):
    __tablename__ = "recordings"
    __table_args__ = (
        UniqueConstraint("practice_session_id", "recording_number", name="uq_recordings_session_number"),
        CheckConstraint(
            "status IN ('capturing', 'saved', 'processing', 'ready', 'invalid', 'removed', 'failed')",
            name="ck_recordings_status",
        ),
        CheckConstraint("recording_number > 0", name="ck_recordings_number_positive"),
        CheckConstraint("duration_ms IS NULL OR duration_ms >= 0", name="ck_recordings_duration_nonnegative"),
        CheckConstraint("size_bytes IS NULL OR size_bytes >= 0", name="ck_recordings_size_nonnegative"),
        CheckConstraint("sample_rate_hz IS NULL OR sample_rate_hz > 0", name="ck_recordings_sample_rate_positive"),
        CheckConstraint("channel_count IS NULL OR channel_count > 0", name="ck_recordings_channel_count_positive"),
        CheckConstraint(
            "(status = 'removed' AND removed_at IS NOT NULL) OR status != 'removed'",
            name="ck_recordings_removed_at",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    practice_session_id: Mapped[str] = mapped_column(
        ForeignKey("practice_sessions.id", ondelete="CASCADE"), index=True
    )
    practice_segment_id: Mapped[str] = mapped_column(
        ForeignKey("practice_segments.id", ondelete="CASCADE"), index=True
    )
    passage_definition_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    recording_number: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(32), index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    storage_key: Mapped[str | None] = mapped_column(String(1024), unique=True, nullable=True)
    original_mime_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    sha256_checksum: Mapped[str | None] = mapped_column(String(64), nullable=True)
    sample_rate_hz: Mapped[int | None] = mapped_column(Integer, nullable=True)
    channel_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    microphone_label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    removal_reason: Mapped[str | None] = mapped_column(String(64), nullable=True)
    removed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    practice_session: Mapped[PracticeSessionEntity] = relationship(back_populates="recordings")
    practice_segment: Mapped[PracticeSegmentEntity] = relationship(back_populates="recordings")


class Database:
    def __init__(self, url: str):
        connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
        self.engine = create_engine(url, connect_args=connect_args)
        if url.startswith("sqlite"):
            event.listen(self.engine, "connect", _enable_sqlite_foreign_keys)
        self.session_factory = sessionmaker(self.engine, expire_on_commit=False)

    def initialize(self) -> None:
        Base.metadata.create_all(self.engine)

    def session(self) -> Iterator[Session]:
        with self.session_factory() as session:
            yield session


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _enable_sqlite_foreign_keys(dbapi_connection, _connection_record) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

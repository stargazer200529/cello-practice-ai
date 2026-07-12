from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import PracticeSegmentEntity, RecordingEntity


class RecordingRepository:
    def __init__(self, session: Session):
        self.session = session

    def next_number(self, practice_session_id: str) -> int:
        highest = self.session.scalar(
            select(func.max(RecordingEntity.recording_number)).where(
                RecordingEntity.practice_session_id == practice_session_id
            )
        )
        return (highest or 0) + 1

    def add(self, recording: RecordingEntity) -> RecordingEntity:
        self.session.add(recording)
        self.session.commit()
        return recording

    def get(self, recording_id: str) -> RecordingEntity | None:
        return self.session.get(RecordingEntity, recording_id)

    def list_for_session(self, practice_session_id: str) -> list[RecordingEntity]:
        statement = (
            select(RecordingEntity)
            .where(RecordingEntity.practice_session_id == practice_session_id)
            .order_by(RecordingEntity.recording_number)
        )
        return list(self.session.scalars(statement))

    def get_segment(self, segment_id: str) -> PracticeSegmentEntity | None:
        return self.session.get(PracticeSegmentEntity, segment_id)

    def save_audio(
        self,
        recording: RecordingEntity,
        *,
        ended_at: datetime,
        duration_ms: int,
        storage_key: str,
        mime_type: str,
        size_bytes: int,
        checksum: str,
        sample_rate_hz: int | None,
        channel_count: int | None,
    ) -> RecordingEntity:
        recording.status = "saved"
        recording.ended_at = ended_at
        recording.duration_ms = duration_ms
        recording.storage_key = storage_key
        recording.original_mime_type = mime_type
        recording.size_bytes = size_bytes
        recording.sha256_checksum = checksum
        recording.sample_rate_hz = sample_rate_hz
        recording.channel_count = channel_count
        recording.updated_at = ended_at
        self.session.commit()
        return recording

    def remove(self, recording: RecordingEntity, reason: str | None, removed_at: datetime) -> RecordingEntity:
        recording.status = "removed"
        recording.removal_reason = reason
        recording.removed_at = removed_at
        recording.storage_key = None
        recording.updated_at = removed_at
        self.session.commit()
        return recording

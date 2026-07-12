from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


RecordingStatus = Literal["capturing", "saved", "processing", "ready", "invalid", "removed", "failed"]
RemovalReason = Literal[
    "accidental_recording",
    "wrong_piece_or_passage",
    "no_usable_audio",
    "user_requested_removal",
    "other",
]


class RecordingCreate(BaseModel):
    practice_segment_id: str = Field(min_length=1, max_length=36)
    passage_id: str | None = Field(default=None, max_length=36)
    started_at: datetime | None = None
    microphone_label: str | None = Field(default=None, max_length=255)


class RecordingRemove(BaseModel):
    reason: RemovalReason | None = None


class RecordingResponse(BaseModel):
    id: str
    practice_session_id: str
    practice_segment_id: str
    passage_id: str | None
    recording_number: int
    label: str
    status: RecordingStatus
    started_at: datetime
    ended_at: datetime | None
    duration_ms: int | None
    original_mime_type: str | None
    size_bytes: int | None
    sha256_checksum: str | None
    sample_rate_hz: int | None
    channel_count: int | None
    microphone_label: str | None
    removal_reason: str | None
    removed_at: datetime | None
    created_at: datetime
    updated_at: datetime

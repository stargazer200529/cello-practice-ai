from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class PracticeSessionCreate(BaseModel):
    piece_id: str = Field(min_length=1, max_length=36)
    instrument_profile_id: str | None = Field(default=None, max_length=36)
    practice_source: Literal["musician_choice", "teacher_assignment", "application_recommendation"] = (
        "musician_choice"
    )
    initial_passage_id: str | None = Field(default=None, max_length=36)
    focus_codes: list[str] = Field(default_factory=list)
    target_duration_seconds: int | None = Field(default=None, gt=0)
    target_tempo_bpm: float | None = Field(default=None, gt=0, le=9999.99)
    session_notes: str | None = None


class PracticeSessionComplete(BaseModel):
    ended_at: datetime | None = None


class PracticeSegmentResponse(BaseModel):
    id: str
    passage_id: str | None
    focus_codes: list[str]
    sequence_number: int
    started_at: datetime
    ended_at: datetime | None
    target_tempo_bpm: float | None
    notes: str | None


class PracticeSessionResponse(BaseModel):
    id: str
    piece_id: str
    status: Literal["active", "completed", "abandoned", "interrupted"]
    practice_source: Literal["musician_choice", "teacher_assignment", "application_recommendation"]
    instrument_profile_id: str | None
    started_at: datetime
    ended_at: datetime | None
    elapsed_seconds: int
    target_duration_seconds: int | None
    session_notes: str | None
    current_segment: PracticeSegmentResponse | None
    segments: list[PracticeSegmentResponse]

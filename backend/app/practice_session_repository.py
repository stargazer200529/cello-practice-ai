from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import PracticeSessionEntity, PracticeSegmentEntity


class PracticeSessionRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, practice_session: PracticeSessionEntity, segment: PracticeSegmentEntity) -> PracticeSessionEntity:
        practice_session.segments.append(segment)
        self.session.add(practice_session)
        self.session.commit()
        return self.get(practice_session.id)  # type: ignore[return-value]

    def get(self, session_id: str) -> PracticeSessionEntity | None:
        statement = (
            select(PracticeSessionEntity)
            .where(PracticeSessionEntity.id == session_id)
            .options(selectinload(PracticeSessionEntity.segments))
        )
        return self.session.scalar(statement)

    def complete(self, practice_session: PracticeSessionEntity, ended_at: datetime, elapsed_seconds: int) -> None:
        practice_session.status = "completed"
        practice_session.ended_at = ended_at
        practice_session.elapsed_seconds = elapsed_seconds
        practice_session.updated_at = ended_at
        for segment in practice_session.segments:
            if segment.ended_at is None:
                segment.ended_at = ended_at
                segment.updated_at = ended_at
        self.session.commit()

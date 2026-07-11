from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import PieceEntity


class PieceRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, piece: PieceEntity) -> PieceEntity:
        self.session.add(piece)
        self.session.commit()
        return piece

    def list_active(self) -> list[PieceEntity]:
        statement = select(PieceEntity).where(PieceEntity.archived.is_(False)).order_by(PieceEntity.created_at.desc())
        return list(self.session.scalars(statement))

    def get_active(self, piece_id: str) -> PieceEntity | None:
        return self.session.scalar(select(PieceEntity).where(PieceEntity.id == piece_id, PieceEntity.archived.is_(False)))

    def delete(self, piece: PieceEntity) -> None:
        self.session.delete(piece)
        self.session.commit()

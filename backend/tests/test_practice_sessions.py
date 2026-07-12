from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

from app.config import Settings
from app.database import Database, PracticeSegmentEntity, PracticeSessionEntity, utc_now
from app.main import LOCAL_USER_ID, create_app
from app.practice_session_repository import PracticeSessionRepository
from tests.test_pieces import upload


def client_for(tmp_path: Path) -> TestClient:
    settings = Settings(database_url=f"sqlite:///{tmp_path / 'test.db'}", musicxml_storage_dir=tmp_path / "scores")
    return TestClient(create_app(settings))


def create_piece(client: TestClient) -> str:
    response = upload(client)
    assert response.status_code == 201
    return response.json()["id"]


def test_create_session_persists_initial_segment_context(tmp_path: Path) -> None:
    client = client_for(tmp_path)
    piece_id = create_piece(client)

    response = client.post(
        "/api/v1/practice-sessions",
        json={
            "piece_id": piece_id,
            "initial_passage_id": "passage-23-25",
            "focus_codes": ["intonation", "technique"],
            "target_duration_seconds": 1200,
            "target_tempo_bpm": 60,
            "session_notes": "Relax the shifting hand.",
        },
    )

    assert response.status_code == 201
    practice_session = response.json()
    assert practice_session["piece_id"] == piece_id
    assert practice_session["status"] == "active"
    assert practice_session["practice_source"] == "musician_choice"
    assert practice_session["elapsed_seconds"] == 0
    assert practice_session["target_duration_seconds"] == 1200
    assert len(practice_session["segments"]) == 1
    assert practice_session["current_segment"] == practice_session["segments"][0]
    assert practice_session["current_segment"]["sequence_number"] == 0
    assert practice_session["current_segment"]["passage_id"] == "passage-23-25"
    assert practice_session["current_segment"]["focus_codes"] == ["intonation", "technique"]
    assert practice_session["current_segment"]["target_tempo_bpm"] == 60.0

    retrieved = client.get(f"/api/v1/practice-sessions/{practice_session['id']}")
    assert retrieved.status_code == 200
    assert retrieved.json() == practice_session


def test_create_session_requires_an_existing_piece(tmp_path: Path) -> None:
    response = client_for(tmp_path).post(
        "/api/v1/practice-sessions", json={"piece_id": "00000000-0000-0000-0000-000000000999"}
    )
    assert response.status_code == 404


def test_complete_session_closes_it_once_and_is_idempotent(tmp_path: Path) -> None:
    client = client_for(tmp_path)
    created = client.post("/api/v1/practice-sessions", json={"piece_id": create_piece(client)}).json()
    started_at = datetime.fromisoformat(created["started_at"])
    ended_at = started_at + timedelta(minutes=12, seconds=4)

    completed_response = client.post(
        f"/api/v1/practice-sessions/{created['id']}/complete", json={"ended_at": ended_at.isoformat()}
    )
    assert completed_response.status_code == 200
    completed = completed_response.json()
    assert completed["status"] == "completed"
    assert datetime.fromisoformat(completed["ended_at"]) == ended_at
    assert completed["elapsed_seconds"] == 724
    assert completed["current_segment"] is None
    assert datetime.fromisoformat(completed["segments"][0]["ended_at"]) == ended_at

    later_end = ended_at + timedelta(hours=1)
    repeated = client.post(
        f"/api/v1/practice-sessions/{created['id']}/complete", json={"ended_at": later_end.isoformat()}
    )
    assert repeated.status_code == 200
    assert repeated.json() == completed


def test_complete_rejects_end_before_start(tmp_path: Path) -> None:
    client = client_for(tmp_path)
    created = client.post("/api/v1/practice-sessions", json={"piece_id": create_piece(client)}).json()
    before_start = datetime.fromisoformat(created["started_at"]) - timedelta(seconds=1)
    response = client.post(
        f"/api/v1/practice-sessions/{created['id']}/complete", json={"ended_at": before_start.isoformat()}
    )
    assert response.status_code == 422
    assert client.get(f"/api/v1/practice-sessions/{created['id']}").json()["status"] == "active"


def test_session_survives_application_restart(tmp_path: Path) -> None:
    first_client = client_for(tmp_path)
    created = first_client.post("/api/v1/practice-sessions", json={"piece_id": create_piece(first_client)}).json()
    first_client.close()

    retrieved = client_for(tmp_path).get(f"/api/v1/practice-sessions/{created['id']}")
    assert retrieved.status_code == 200
    assert retrieved.json()["id"] == created["id"]


def test_other_users_session_is_not_visible_or_completable(tmp_path: Path) -> None:
    settings = Settings(database_url=f"sqlite:///{tmp_path / 'test.db'}", musicxml_storage_dir=tmp_path / "scores")
    client = TestClient(create_app(settings))
    piece_id = create_piece(client)
    now = utc_now()
    session_id = str(uuid4())
    database = Database(settings.database_url)
    with database.session_factory() as database_session:
        practice_session = PracticeSessionEntity(
            id=session_id,
            user_id="00000000-0000-0000-0000-000000000002",
            piece_id=piece_id,
            instrument_profile_id=None,
            status="active",
            practice_source="musician_choice",
            started_at=now,
            ended_at=None,
            elapsed_seconds=0,
            target_duration_seconds=None,
            session_notes=None,
            created_at=now,
            updated_at=now,
        )
        segment = PracticeSegmentEntity(
            id=str(uuid4()),
            practice_session_id=session_id,
            passage_definition_id=None,
            focus_codes=[],
            sequence_number=0,
            started_at=now,
            ended_at=None,
            target_tempo_bpm=None,
            notes=None,
            created_at=now,
            updated_at=now,
        )
        PracticeSessionRepository(database_session).add(practice_session, segment)

    assert LOCAL_USER_ID != practice_session.user_id
    assert client.get(f"/api/v1/practice-sessions/{session_id}").status_code == 404
    assert client.post(f"/api/v1/practice-sessions/{session_id}/complete", json={}).status_code == 404

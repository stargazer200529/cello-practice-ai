from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

from app.config import Settings
from app.database import Database, PracticeSegmentEntity, PracticeSessionEntity, RecordingEntity, utc_now
from app.main import LOCAL_USER_ID, create_app
from app.practice_session_repository import PracticeSessionRepository
from tests.test_pieces import upload


AUDIO = b"browser-recorded-audio"


def settings_for(tmp_path: Path, max_recording_bytes: int = 1024) -> Settings:
    return Settings(
        database_url=f"sqlite:///{tmp_path / 'test.db'}",
        musicxml_storage_dir=tmp_path / "scores",
        recording_storage_dir=tmp_path / "recordings",
        max_recording_bytes=max_recording_bytes,
    )


def client_for(tmp_path: Path, max_recording_bytes: int = 1024) -> TestClient:
    return TestClient(create_app(settings_for(tmp_path, max_recording_bytes)))


def create_session(client: TestClient, passage_id: str = "passage-1") -> dict[str, object]:
    piece_response = upload(client)
    assert piece_response.status_code == 201
    response = client.post(
        "/api/v1/practice-sessions",
        json={"piece_id": piece_response.json()["id"], "initial_passage_id": passage_id},
    )
    assert response.status_code == 201
    return response.json()


def create_recording(client: TestClient, practice_session: dict[str, object]) -> dict[str, object]:
    segment = practice_session["current_segment"]
    assert isinstance(segment, dict)
    response = client.post(
        f"/api/v1/practice-sessions/{practice_session['id']}/recordings",
        json={
            "practice_segment_id": segment["id"],
            "started_at": practice_session["started_at"],
            "microphone_label": "Built-in Microphone",
        },
    )
    assert response.status_code == 201
    return response.json()


def upload_audio(client: TestClient, recording: dict[str, object], content: bytes = AUDIO):
    ended_at = datetime.fromisoformat(str(recording["started_at"])) + timedelta(seconds=3)
    return client.post(
        f"/api/v1/recordings/{recording['id']}/audio",
        files={"file": ("capture.webm", content, "audio/webm")},
        data={
            "ended_at": ended_at.isoformat(),
            "duration_ms": "3000",
            "original_mime_type": "audio/webm;codecs=opus",
            "sample_rate_hz": "48000",
            "channel_count": "1",
        },
    )


def test_recording_lifecycle_persists_metadata_and_private_audio(tmp_path: Path) -> None:
    settings = settings_for(tmp_path)
    client = TestClient(create_app(settings))
    practice_session = create_session(client)
    recording = create_recording(client, practice_session)

    assert recording["recording_number"] == 1
    assert recording["label"] == "Recording 1"
    assert recording["status"] == "capturing"
    assert recording["passage_id"] == "passage-1"
    saved_response = upload_audio(client, recording)
    assert saved_response.status_code == 200
    saved = saved_response.json()
    assert saved["status"] == "saved"
    assert saved["original_mime_type"] == "audio/webm;codecs=opus"
    assert saved["duration_ms"] == 3000
    assert saved["size_bytes"] == len(AUDIO)
    assert len(saved["sha256_checksum"]) == 64
    assert saved["sample_rate_hz"] == 48000
    assert saved["channel_count"] == 1
    assert "storage_key" not in saved

    stored_files = list(settings.recording_storage_dir.rglob("*.webm"))
    assert len(stored_files) == 1
    assert stored_files[0].read_bytes() == AUDIO
    assert stored_files[0].parts[-3:] == (LOCAL_USER_ID, str(practice_session["id"]), f"{recording['id']}.webm")

    client.close()
    restarted = TestClient(create_app(settings))
    assert restarted.get(f"/api/v1/recordings/{recording['id']}").json() == saved
    audio_response = restarted.get(f"/api/v1/recordings/{recording['id']}/audio")
    assert audio_response.status_code == 200
    assert audio_response.content == AUDIO
    assert audio_response.headers["content-type"].startswith("audio/webm")
    listed = restarted.get(f"/api/v1/practice-sessions/{practice_session['id']}/recordings")
    assert listed.status_code == 200
    assert listed.json() == [saved]


def test_removal_deletes_audio_but_preserves_number_and_metadata(tmp_path: Path) -> None:
    client = client_for(tmp_path)
    practice_session = create_session(client)
    first = create_recording(client, practice_session)
    assert upload_audio(client, first).status_code == 200

    removed_response = client.post(
        f"/api/v1/recordings/{first['id']}/remove",
        json={"reason": "accidental_recording"},
    )
    assert removed_response.status_code == 200
    removed = removed_response.json()
    assert removed["status"] == "removed"
    assert removed["removal_reason"] == "accidental_recording"
    assert removed["removed_at"] is not None
    assert removed["size_bytes"] == len(AUDIO)
    assert client.get(f"/api/v1/recordings/{first['id']}/audio").status_code == 404
    assert list((tmp_path / "recordings").rglob("*.webm")) == []

    second = create_recording(client, practice_session)
    assert second["recording_number"] == 2
    assert second["label"] == "Recording 2"
    listed = client.get(f"/api/v1/practice-sessions/{practice_session['id']}/recordings").json()
    assert [item["recording_number"] for item in listed] == [1, 2]
    assert [item["status"] for item in listed] == ["removed", "capturing"]


def test_recording_requires_active_session_segment_and_matching_session(tmp_path: Path) -> None:
    client = client_for(tmp_path)
    first_session = create_session(client)
    second_session = create_session(client)
    second_segment = second_session["current_segment"]
    assert isinstance(second_segment, dict)

    mismatch = client.post(
        f"/api/v1/practice-sessions/{first_session['id']}/recordings",
        json={"practice_segment_id": second_segment["id"]},
    )
    assert mismatch.status_code == 404

    assert client.post(f"/api/v1/practice-sessions/{first_session['id']}/complete", json={}).status_code == 200
    first_segment = first_session["current_segment"]
    assert isinstance(first_segment, dict)
    inactive = client.post(
        f"/api/v1/practice-sessions/{first_session['id']}/recordings",
        json={"practice_segment_id": first_segment["id"]},
    )
    assert inactive.status_code == 409


def test_invalid_audio_upload_leaves_recording_capturing_without_file(tmp_path: Path) -> None:
    client = client_for(tmp_path, max_recording_bytes=4)
    practice_session = create_session(client)
    recording = create_recording(client, practice_session)

    response = upload_audio(client, recording, b"too-large")
    assert response.status_code == 413
    assert client.get(f"/api/v1/recordings/{recording['id']}").json()["status"] == "capturing"
    assert not (tmp_path / "recordings").exists()


def test_foreign_owned_recordings_are_hidden_from_all_recording_endpoints(tmp_path: Path) -> None:
    settings = settings_for(tmp_path)
    client = TestClient(create_app(settings))
    piece_response = upload(client)
    assert piece_response.status_code == 201
    now = utc_now()
    session_id = str(uuid4())
    segment_id = str(uuid4())
    recording_id = str(uuid4())
    database = Database(settings.database_url)
    with database.session_factory() as database_session:
        practice_session = PracticeSessionEntity(
            id=session_id,
            user_id="00000000-0000-0000-0000-000000000002",
            piece_id=piece_response.json()["id"],
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
            id=segment_id,
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
        database_session.add(
            RecordingEntity(
                id=recording_id,
                practice_session_id=session_id,
                practice_segment_id=segment_id,
                passage_definition_id=None,
                recording_number=1,
                status="capturing",
                started_at=now,
                ended_at=None,
                duration_ms=None,
                storage_key=None,
                original_mime_type=None,
                size_bytes=None,
                sha256_checksum=None,
                sample_rate_hz=None,
                channel_count=None,
                microphone_label=None,
                removal_reason=None,
                removed_at=None,
                created_at=now,
                updated_at=now,
            )
        )
        database_session.commit()

    assert client.get(f"/api/v1/recordings/{recording_id}").status_code == 404
    assert client.get(f"/api/v1/recordings/{recording_id}/audio").status_code == 404
    assert client.get(f"/api/v1/practice-sessions/{session_id}/recordings").status_code == 404
    assert client.post(f"/api/v1/recordings/{recording_id}/remove", json={}).status_code == 404
    ended_at = (now + timedelta(seconds=1)).isoformat()
    upload_response = client.post(
        f"/api/v1/recordings/{recording_id}/audio",
        files={"file": ("capture.webm", AUDIO, "audio/webm")},
        data={"ended_at": ended_at, "duration_ms": "1000"},
    )
    assert upload_response.status_code == 404

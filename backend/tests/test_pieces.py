from pathlib import Path
from io import BytesIO
from zipfile import ZipFile

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
VALID_SCORE = b"""<score-partwise version="4.0"><work><work-title>Cello Study</work-title></work>
<identification><creator type="composer">Ada Example</creator></identification>
<part-list><score-part id="P1"><part-name>Violoncello</part-name></score-part></part-list>
<part id="P1"><measure number="1"><attributes><key><fifths>0</fifths></key>
<time><beats>4</beats><beat-type>4</beat-type></time></attributes></measure></part></score-partwise>"""


def client_for(tmp_path: Path) -> TestClient:
    settings = Settings(database_url=f"sqlite:///{tmp_path / 'test.db'}", musicxml_storage_dir=tmp_path / "scores")
    return TestClient(create_app(settings))


def upload(client: TestClient, filename: str = "study.musicxml", content: bytes = VALID_SCORE):
    return client.post("/pieces", files={"file": (filename, content, "application/xml")})


def compressed_score() -> bytes:
    output = BytesIO()
    with ZipFile(output, "w") as archive:
        archive.writestr("META-INF/container.xml", "<container><rootfiles><rootfile full-path='score/main.musicxml'/></rootfiles></container>")
        archive.writestr("score/main.musicxml", VALID_SCORE)
    return output.getvalue()


def test_create_list_retrieve_content_and_delete(tmp_path: Path) -> None:
    client = client_for(tmp_path)
    first = upload(client, "same.musicxml")
    second = upload(client, "same.musicxml")
    assert first.status_code == 201 and second.status_code == 201
    first_piece = first.json()
    assert first_piece["title"] == "Cello Study"
    assert len(client.get("/pieces").json()) == 2
    assert client.get(f"/pieces/{first_piece['id']}").json() == first_piece
    xml_response = client.get(f"/pieces/{first_piece['id']}/musicxml")
    assert xml_response.status_code == 200
    assert "<score-partwise" in xml_response.text
    assert len(list((tmp_path / "scores").iterdir())) == 2

    assert client.delete(f"/pieces/{first_piece['id']}").status_code == 204
    assert client.get(f"/pieces/{first_piece['id']}").status_code == 404
    assert len(client.get("/pieces").json()) == 1
    assert len(list((tmp_path / "scores").iterdir())) == 1


def test_invalid_upload_leaves_no_record_or_file(tmp_path: Path) -> None:
    client = client_for(tmp_path)
    response = upload(client, content=b"<not-musicxml />")
    assert response.status_code == 422
    assert client.get("/pieces").json() == []
    assert list((tmp_path / "scores").iterdir()) == []


def test_compressed_mxl_persists_extracted_root_musicxml(tmp_path: Path) -> None:
    client = client_for(tmp_path)
    response = upload(client, "study.mxl", compressed_score())
    assert response.status_code == 201
    piece = response.json()
    assert piece["original_filename"] == "study.mxl"
    stored_files = list((tmp_path / "scores").iterdir())
    assert len(stored_files) == 1
    assert stored_files[0].suffix == ".musicxml"
    assert stored_files[0].read_bytes() == VALID_SCORE
    assert client.get(f"/pieces/{piece['id']}/musicxml").content == VALID_SCORE

from io import BytesIO

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

VALID_SCORE = b"""<?xml version="1.0" encoding="UTF-8"?>
<score-partwise version="4.0">
  <work><work-title>Cello Study</work-title></work>
  <identification><creator type="composer">Ada Example</creator></identification>
  <part-list>
    <score-part id="P1"><part-name>Violoncello</part-name></score-part>
    <score-part id="P2"><part-name>Piano</part-name></score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes>
        <key><fifths>-2</fifths><mode>minor</mode></key>
        <time><beats>4</beats><beat-type>4</beat-type></time>
      </attributes>
    </measure>
    <measure number="2">
      <attributes><time><beats>3</beats><beat-type>4</beat-type></time></attributes>
    </measure>
  </part>
  <part id="P2"><measure number="1"/><measure number="2"/></part>
</score-partwise>
"""


def upload(content: bytes, filename: str = "study.musicxml"):
    return client.post(
        "/scores/metadata",
        files={"file": (filename, BytesIO(content), "application/xml")},
    )


def test_upload_returns_real_score_metadata() -> None:
    response = upload(VALID_SCORE)

    assert response.status_code == 200
    assert response.json() == {
        "title": "Cello Study",
        "composer": "Ada Example",
        "part_names": ["Violoncello", "Piano"],
        "measure_count": 2,
        "time_signatures": ["4/4", "3/4"],
        "key_signatures": ["-2 fifths, minor"],
    }


def test_upload_preserves_absent_optional_metadata() -> None:
    response = upload(
        b"""<score-partwise><part-list><score-part id="P1">
        <part-name>Cello</part-name></score-part></part-list>
        <part id="P1"><measure number="1"/></part></score-partwise>"""
    )

    assert response.status_code == 200
    assert response.json()["title"] is None
    assert response.json()["composer"] is None
    assert response.json()["time_signatures"] == []
    assert response.json()["key_signatures"] == []


def test_upload_rejects_malformed_xml() -> None:
    response = upload(b"<score-partwise>")

    assert response.status_code == 422
    assert response.json() == {"detail": "The uploaded file is not valid XML."}


def test_upload_rejects_xml_entity_declarations() -> None:
    response = upload(
        b"""<?xml version="1.0"?>
        <!DOCTYPE score-partwise [<!ENTITY unsafe "entity content">]>
        <score-partwise>
          <part-list><score-part id="P1"><part-name>&unsafe;</part-name></score-part></part-list>
          <part id="P1"><measure number="1"/></part>
        </score-partwise>"""
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "The uploaded XML contains unsupported external or entity content."
    }


def test_upload_rejects_non_musicxml_xml() -> None:
    response = upload(b"<catalog><item>Not a score</item></catalog>", "catalog.xml")

    assert response.status_code == 422
    assert response.json() == {
        "detail": "The uploaded XML is not a supported MusicXML score."
    }


def test_upload_rejects_unsupported_extension() -> None:
    response = upload(VALID_SCORE, "study.txt")

    assert response.status_code == 422
    assert response.json() == {
        "detail": "Choose a MusicXML file with a .musicxml or .xml extension."
    }


def test_upload_supports_local_frontend_cors_preflight() -> None:
    response = client.options(
        "/scores/metadata",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert "POST" in response.headers["access-control-allow-methods"]

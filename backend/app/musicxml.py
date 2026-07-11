from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from xml.etree.ElementTree import Element

from defusedxml import ElementTree
from defusedxml.common import DefusedXmlException

SUPPORTED_EXTENSIONS = {".musicxml", ".xml"}


class MusicXMLValidationError(ValueError):
    """Raised when uploaded content cannot be treated as supported MusicXML."""


@dataclass(frozen=True)
class ScoreMetadata:
    title: str | None
    composer: str | None
    part_names: list[str]
    measure_count: int
    time_signatures: list[str]
    key_signatures: list[str]


def validate_filename(filename: str | None) -> None:
    if not filename or Path(filename).suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise MusicXMLValidationError(
            "Choose a MusicXML file with a .musicxml or .xml extension."
        )


def parse_musicxml(content: bytes) -> ScoreMetadata:
    try:
        root = ElementTree.parse(BytesIO(content)).getroot()
    except ElementTree.ParseError as error:
        raise MusicXMLValidationError("The uploaded file is not valid XML.") from error
    except DefusedXmlException as error:
        raise MusicXMLValidationError(
            "The uploaded XML contains unsupported external or entity content."
        ) from error

    score_type = _local_name(root.tag)
    if score_type not in {"score-partwise", "score-timewise"}:
        raise MusicXMLValidationError(
            "The uploaded XML is not a supported MusicXML score."
        )

    measure_count = _measure_count(root, score_type)
    if measure_count == 0:
        raise MusicXMLValidationError(
            "The MusicXML score does not contain any notated parts."
        )

    return ScoreMetadata(
        title=_first_text(root, ("work", "work-title"))
        or _first_text(root, ("movement-title",)),
        composer=_composer(root),
        part_names=_part_names(root),
        measure_count=measure_count,
        time_signatures=_time_signatures(root),
        key_signatures=_key_signatures(root),
    )


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _children(element: Element, name: str) -> list[Element]:
    return [child for child in element if _local_name(child.tag) == name]


def _descendants(element: Element, name: str) -> list[Element]:
    return [item for item in element.iter() if _local_name(item.tag) == name]


def _first_text(element: Element, path: tuple[str, ...]) -> str | None:
    current = element
    for name in path:
        matches = _children(current, name)
        if not matches:
            return None
        current = matches[0]
    return _clean_text(current)


def _clean_text(element: Element) -> str | None:
    text = "".join(element.itertext()).strip()
    return " ".join(text.split()) or None


def _composer(root: Element) -> str | None:
    for creator in _descendants(root, "creator"):
        if creator.attrib.get("type", "").lower() == "composer":
            return _clean_text(creator)
    return None


def _part_names(root: Element) -> list[str]:
    names: list[str] = []
    for score_part in _descendants(root, "score-part"):
        name = _first_text(score_part, ("part-name",))
        if name and name not in names:
            names.append(name)
    return names


def _measure_count(root: Element, score_type: str) -> int:
    if score_type == "score-timewise":
        measures = _children(root, "measure")
        return len(measures) if any(_children(measure, "part") for measure in measures) else 0

    parts = _children(root, "part")
    return max((len(_children(part, "measure")) for part in parts), default=0)


def _time_signatures(root: Element) -> list[str]:
    signatures: list[str] = []
    for time in _descendants(root, "time"):
        beats = [_clean_text(item) for item in _children(time, "beats")]
        beat_types = [_clean_text(item) for item in _children(time, "beat-type")]
        pairs = [
            f"{beat}/{beat_type}"
            for beat, beat_type in zip(beats, beat_types, strict=False)
            if beat and beat_type
        ]
        signature = "+".join(pairs)
        if signature and signature not in signatures:
            signatures.append(signature)
    return signatures


def _key_signatures(root: Element) -> list[str]:
    signatures: list[str] = []
    for key in _descendants(root, "key"):
        fifths = _first_text(key, ("fifths",))
        mode = _first_text(key, ("mode",))
        if fifths is None:
            continue
        signature = f"{fifths} fifths"
        if mode:
            signature = f"{signature}, {mode}"
        if signature not in signatures:
            signatures.append(signature)
    return signatures

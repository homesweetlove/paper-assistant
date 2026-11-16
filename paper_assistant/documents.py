"""Document input and deliberately non-destructive exports."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LoadedDocument:
    text: str
    path: Path
    notice: str


def load_document(path: str | Path) -> LoadedDocument:
    source = Path(path).resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    suffix = source.suffix.lower()
    if suffix == ".docx":
        try:
            from docx import Document
        except ImportError as exc:
            raise RuntimeError("DOCX를 열려면 python-docx를 설치하세요.") from exc
        doc = Document(source)
        # python-docx 1.1+ retains document order for both tables and paragraphs.
        pieces: list[str] = []
        for block in doc.iter_inner_content():
            if hasattr(block, "rows"):
                for row in block.rows:
                    pieces.append(" | ".join(cell.text for cell in row.cells))
            else:
                pieces.append(block.text)
        return LoadedDocument("\n".join(pieces), source,
                              "분석 전용으로 읽었습니다. 각주·도형 등 일부 요소는 검사에서 제외될 수 있습니다.")
    if suffix in {".txt", ".md"}:
        return LoadedDocument(source.read_text(encoding="utf-8-sig"), source,
                              "분석 전용으로 읽었습니다. 원본 파일은 변경하지 않습니다.")
    raise ValueError("지원하는 입력 형식: .docx, .txt, .md")


def export_plain_docx(text: str, path: str | Path, *, original: str | Path | None = None) -> Path:
    """Save a NEW plain-text draft. Refuse to replace the loaded original."""
    destination = Path(path).resolve()
    if destination.suffix.lower() != ".docx":
        raise ValueError("출력 확장자는 .docx여야 합니다")
    if original and destination == Path(original).resolve():
        raise ValueError("원본 DOCX 파일을 덮어쓸 수 없습니다. 다른 파일 이름을 선택하세요.")
    try:
        from docx import Document
    except ImportError as exc:
        raise RuntimeError("DOCX를 저장하려면 python-docx를 설치하세요.") from exc
    doc = Document()
    for para in text.split("\n"):
        doc.add_paragraph(para)
    with destination.open("xb") as output:
        doc.save(output)
    return destination

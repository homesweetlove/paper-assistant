"""Local reports. Never modify the input manuscript."""

from __future__ import annotations

from html import escape
from pathlib import Path

from .analysis import AnalysisResult


def _preview(text: str, start: int, end: int) -> str:
    return text[max(0, start - 35):min(len(text), end + 35)].replace("\n", " ").strip()


def report_html(text: str, result: AnalysisResult) -> str:
    stat_rows = "".join(f"<tr><th>{escape(str(k))}</th><td>{escape(str(v))}</td></tr>"
                        for k, v in result.stats.items())
    issue_rows = "".join(
        "<tr>"
        f"<td>{escape(i.category)}</td><td>{escape(i.message)}</td>"
        f"<td>{escape(_preview(text, i.start, i.end))}</td>"
        f"<td>{escape(i.suggestion)}</td>"
        "</tr>" for i in result.issues
    )
    return ("<!doctype html><html lang='ko'><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width, initial-scale=1'>"
            "<title>Paper Assistant 검사 보고서</title>"
            "<style>body{font:15px system-ui,sans-serif;max-width:1050px;margin:40px auto;"
            "padding:0 18px;color:#243447}h1{color:#174e7c}table{width:100%;border-collapse:collapse;"
            "margin:18px 0 30px}th,td{border:1px solid #d8e3eb;padding:10px;text-align:left;"
            "vertical-align:top}th{background:#edf5fa}tr:nth-child(even){background:#f9fbfd}"
            ".note{padding:12px;border-left:4px solid #ddb264;background:#fffaed}</style>"
            "<h1>Paper Assistant 검사 보고서</h1>"
            "<p class='note'>규칙 기반 후보 표시입니다. 문장 오류, 연구 결과, 인용 출처의 진위를 "
            "판정하지 않습니다. 보고서는 로컬에만 저장됩니다.</p>"
            f"<h2>문서 통계</h2><table>{stat_rows}</table>"
            f"<h2>검토 후보 ({len(result.issues)}건)</h2>"
            "<table><tr><th>분류</th><th>내용</th><th>주변 문맥</th><th>검토 힌트</th></tr>"
            f"{issue_rows}</table></html>")


def report_markdown(text: str, result: AnalysisResult) -> str:
    def safe(value: str) -> str:
        return escape(value).replace("|", "\\|").replace("\n", " ")
    lines = ["# Paper Assistant 검사 보고서", "",
             "> 규칙 기반 검토 후보입니다. 사실성·인용 정확성을 보증하지 않습니다.", "",
             "## 통계", ""]
    lines += [f"- {k}: {v}" for k, v in result.stats.items()]
    lines += ["", "## 검사 결과", "", "| 유형 | 메시지 | 주변 문맥 |", "| --- | --- | --- |"]
    lines += [f"| {safe(i.category)} | {safe(i.message)} | {safe(_preview(text, i.start, i.end))} |"
              for i in result.issues]
    return "\n".join(lines) + "\n"


def save_report(path: str | Path, text: str, result: AnalysisResult, *, original: str | Path | None = None) -> Path:
    destination = Path(path).resolve()
    if original and destination == Path(original).resolve():
        raise ValueError("원본 문서 경로로 보고서를 저장할 수 없습니다")
    if destination.suffix.lower() == ".html":
        content = report_html(text, result)
    elif destination.suffix.lower() == ".md":
        content = report_markdown(text, result)
    else:
        raise ValueError("보고서는 .html 또는 .md로 저장하세요")
    with destination.open("x", encoding="utf-8") as output:
        output.write(content)
    return destination

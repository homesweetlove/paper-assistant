"""Deterministic, explainable writing suggestions with precise text offsets.

These checks are heuristics. They do not assess factual correctness, research
quality, source validity, or whether a sentence is grammatically incorrect.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True)
class Issue:
    rule: str
    category: str
    message: str
    start: int
    end: int
    suggestion: str = ""


@dataclass(frozen=True)
class AnalysisResult:
    issues: tuple[Issue, ...]
    stats: dict[str, int | float]
    top_words: tuple[tuple[str, int], ...]


TOKEN = re.compile(r"[가-힣A-Za-z0-9]+")
REPEAT = re.compile(r"(?<!\w)([가-힣A-Za-z]{2,})(\s+)\1(?!\w)", re.IGNORECASE)
COLLOQUIAL = re.compile(r"(해요|했어요|이에요|예요|이예요|죠|네요|거든요|잖아요|군요|구나|지요)\s*[.!?]*$")
FIRST_PERSON = re.compile(r"(?<!\w)(내가|저는|우리는|우리가|제가)(?!\w)")
INTENSIFIER = re.compile(r"(?<!\w)(매우|정말|아주|굉장히|엄청|되게|진짜|너무)(?!\w)")
OPENERS = ("그래서", "근데", "그리고", "하지만", "그런데", "그러면")
UNIT_VARIANTS = re.compile(r"(?<!\w)\d+(?:\.\d+)?\s*(msec|millisecond(?:s)?|밀리초)(?![A-Za-z0-9])", re.IGNORECASE)
ACRONYM = re.compile(r"(?<![A-Za-z])[A-Z]{2,8}(?![A-Za-z])")
KNOWN_ACRONYMS = {"AI", "API", "CPU", "GPU", "USB", "DNA", "PDF", "HTML", "IEEE", "ISO"}
DOI = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", re.IGNORECASE)
CAPTION = re.compile(r"(?m)^\s*(그림|표)\s*(\d+)\s*[:.\-–]?\s*\S+")
FIGURE_REFERENCE = re.compile(r"(?<!\w)(그림|표)\s*(\d+)(?!\d)")
STOPWORDS = {"그리고", "그러나", "하지만", "때문에", "것이다", "있다", "한다", "대한", "통해"}
ABBREVIATIONS = {"e.g", "i.e", "vs", "fig", "dr", "mr", "mrs", "prof"}


def _trim_span(text: str, start: int, end: int) -> tuple[str, int, int]:
    while start < end and text[start].isspace():
        start += 1
    while end > start and text[end - 1].isspace():
        end -= 1
    return text[start:end], start, end


def split_sentences(text: str) -> list[tuple[str, int, int]]:
    """Split punctuation and newline-delimited sentences without losing offsets.

    Decimal points, common English abbreviations and DOI prefixes are not treated
    as sentence boundaries. Every returned span is an exact slice of `text`.
    """
    out: list[tuple[str, int, int]] = []
    start = 0
    length = len(text)
    for index, char in enumerate(text):
        if char in "\r\n":
            sent, left, right = _trim_span(text, start, index)
            if sent:
                out.append((sent, left, right))
            start = index + 1
            continue
        if char not in ".!?":
            continue
        if char == ".":
            if 0 < index < length - 1 and text[index - 1].isdigit() and text[index + 1].isdigit():
                continue
            prior = re.search(r"([A-Za-z.]+)$", text[start:index])
            if prior and prior.group(1).lower().strip(".") in ABBREVIATIONS:
                continue
        if index + 1 < length and text[index + 1] in ".!?":
            continue
        if index + 1 < length and not text[index + 1].isspace():
            continue
        sent, left, right = _trim_span(text, start, index + 1)
        if sent:
            out.append((sent, left, right))
        start = index + 1
    if start < length:
        sent, left, right = _trim_span(text, start, length)
        if sent:
            out.append((sent, left, right))
    return out


def analyze_text(
    text: str,
    *,
    long_sentence_limit: int = 100,
    repeat_minimum: int = 4,
    repeat_ratio: float = 0.08,
    academic_checks: bool = False,
) -> AnalysisResult:
    """Return read-only suggestions and counts for supplied plain text."""
    if long_sentence_limit < 20:
        raise ValueError("긴 문장 기준은 20자 이상이어야 합니다")
    if repeat_minimum < 2 or not 0 < repeat_ratio <= 1:
        raise ValueError("반복 단어 기준이 유효하지 않습니다")

    issues: list[Issue] = []
    sentences = split_sentences(text)
    previous_tail = ""
    tail_streak = 0

    for sent, start, end in sentences:
        if len(sent) >= long_sentence_limit:
            issues.append(Issue("long_sentence", "문장", f"긴 문장 ({len(sent)}자)", start, end,
                                "두 문장으로 나눌 수 있는지 검토하세요."))
        if sent.endswith(("?", "!")):
            issues.append(Issue("question", "문장", "의문·감탄 표현 확인", start, end,
                                "학술 문체에 적절한지 확인하세요."))
        found = COLLOQUIAL.search(sent)
        if found:
            issues.append(Issue("colloquial", "문체", f"구어체 종결 표현: {found.group(1)}",
                                start + found.start(1), start + found.end(1), "학술 문체를 검토하세요."))
        first = re.match(r"\S+", sent)
        if first and first.group().rstrip(",，") in OPENERS:
            issues.append(Issue("opener", "문체", f"문두 접속어: {first.group()}",
                                start + first.start(), start + first.end(), "앞 문장과 연결이 필요한지 검토하세요."))
        for rule, pattern, label in (("first_person", FIRST_PERSON, "1인칭 표현"),
                                     ("intensifier", INTENSIFIER, "정량적 근거를 검토할 수식어")):
            found = pattern.search(sent)
            if found:
                issues.append(Issue(rule, "문체", f"{label}: {found.group()}",
                                    start + found.start(), start + found.end()))
        for found in REPEAT.finditer(sent):
            issues.append(Issue("adjacent_repeat", "반복", f"연속 중복 표현: {found.group(1)}",
                                start + found.start(), start + found.end()))

        tail = re.search(r"([가-힣]{2,4})[.!?]*$", sent)
        current_tail = tail.group(1) if tail else ""
        tail_streak = tail_streak + 1 if current_tail and current_tail == previous_tail else 1
        if tail_streak == 3:
            issues.append(Issue("ending_repeat", "반복", "세 문장에서 비슷한 종결 표현 반복",
                                start, end, "문장 전개를 확인하세요. 반드시 수정할 필요는 없습니다."))
        previous_tail = current_tail

    found_words = list(TOKEN.finditer(text))
    words = [m.group().lower() for m in found_words if len(m.group()) >= 2 and m.group() not in STOPWORDS]
    counts = Counter(words)
    for word, count in counts.most_common():
        if count < repeat_minimum or count / max(len(words), 1) < repeat_ratio:
            continue
        first = next(m for m in found_words if m.group().lower() == word)
        issues.append(Issue("word_frequency", "반복", f"'{word}' {count}회 반복 ({count / len(words):.0%})",
                            first.start(), first.end(), "핵심 용어라면 반복이 자연스러울 수 있습니다."))

    if academic_checks:
        for found in UNIT_VARIANTS.finditer(text):
            issues.append(Issue("unit_style", "학술", f"단위 표기 통일 검토: {found.group()}",
                                found.start(), found.end(), "예: 10 ms (학술지 규정을 우선하세요)."))
        acronyms = Counter(m.group() for m in ACRONYM.finditer(text))
        for abbreviation, count in acronyms.items():
            if count < 2 or abbreviation in KNOWN_ACRONYMS:
                continue
            if re.search(r"\(\s*" + re.escape(abbreviation) + r"\s*\)", text):
                continue
            found = re.search(r"\b" + re.escape(abbreviation) + r"\b", text)
            if found:
                issues.append(Issue("acronym_definition", "학술", f"약어 '{abbreviation}'의 첫 정의 확인",
                                    found.start(), found.end(), "첫 등장 시 전체 명칭을 설명했는지 확인하세요."))
        for caption in CAPTION.finditer(text):
            kind, number = caption.group(1), caption.group(2)
            occurrences = [m for m in FIGURE_REFERENCE.finditer(text)
                           if m.group(1) == kind and m.group(2) == number]
            if len(occurrences) <= 1:
                issues.append(Issue("caption_reference", "학술", f"{kind} {number}: 본문에서 참조했는지 확인",
                                    caption.start(1), caption.end(2),
                                    "표·그림의 캡션과 본문 참조 번호가 일치하는지 확인하세요."))

    stats: dict[str, int | float] = {
        "글자 수(공백 포함)": len(text),
        "글자 수(공백 제외)": len(re.sub(r"\s", "", text)),
        "단어 수(공백 기준)": len(text.split()),
        "문장 수": len(sentences),
        "문단 수": sum(bool(p.strip()) for p in re.split(r"\r?\n\s*\r?\n", text) if p.strip()),
        "평균 문장 길이": round(sum(len(s) for s, _, _ in sentences) / max(len(sentences), 1), 1),
        "DOI 문자열 수": len(DOI.findall(text)),
    }
    return AnalysisResult(tuple(sorted(issues, key=lambda issue: (issue.start, issue.end, issue.rule))),
                          stats, tuple(counts.most_common(20)))

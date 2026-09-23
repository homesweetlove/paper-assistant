# Paper Assistant

한국어 논문·보고서 초안을 오프라인에서 점검하기 위한 경량 작성 보조 도구입니다.

AI API나 외부 서버 없이 로컬에서 문장을 분석하며, Python GUI 버전과 Microsoft Word VBA 매크로 버전을 함께 제공합니다.

## 주요 기능

### Python GUI

`paper_assistant.pyw`는 Tkinter 기반 데스크톱 도구입니다.

- 텍스트 직접 작성 및 붙여넣기
- `.docx` 문서 열기 / 저장
- 글자 수, 단어 수, 문장 수, 문단 수 통계
- 평균 문장 길이 계산
- 긴 문장 탐지
- 감탄문·의문문 탐지
- 구어체 종결어미 탐지
- 문두 접속어, 1인칭 표현, 과도한 수식어 점검
- 반복 어휘 및 단어 빈도 분석
- 실시간 분석 및 문제 구간 하이라이트

### Microsoft Word VBA

- `PaperAssist.bas` — Word에서 실시간 문장 점검을 수행하는 VBA 모듈
- `PaperAssist_ko.bas` — 한국어 사용을 고려한 VBA 모듈

Word 매크로 버전은 긴 문장, 감탄·의문문, 일부 구어체 표현을 색상으로 표시합니다.

## 실행 환경

- Windows 권장
- Python 3.x
- Tkinter
- `python-docx` — Word 문서 열기/저장 기능에 사용

Tkinter는 일반적인 Windows용 Python 설치에 포함되어 있습니다.

### 설치

```powershell
pip install python-docx
```

### 실행

```powershell
pythonw paper_assistant.pyw
```

콘솔을 확인하면서 실행하려면:

```powershell
python paper_assistant.pyw
```

## Word VBA 사용

1. Microsoft Word에서 `Alt + F11`로 VBA 편집기를 엽니다.
2. **File → Import File**에서 `PaperAssist.bas` 또는 `PaperAssist_ko.bas`를 가져옵니다.
3. 매크로 실행이 허용된 문서에서 사용합니다.
4. `CheckAll`을 실행하면 전체 문서를 검사할 수 있습니다.
5. `ClearMarks`로 표시를 제거할 수 있습니다.

매크로 보안 정책은 사용하는 PC와 조직 설정을 따릅니다.

## 프로젝트 구조

```text
paper-assistant/
├─ paper_assistant.pyw   # Python/Tkinter 데스크톱 앱
├─ PaperAssist.bas       # Word VBA 버전
├─ PaperAssist_ko.bas    # 한국어용 Word VBA 버전
└─ README.md
```

## 분석 기준에 대하여

이 프로젝트의 검사는 정규식과 단순 휴리스틱을 기반으로 합니다. 따라서 표시된 문장이 반드시 잘못된 문장이라는 뜻은 아닙니다.

논문 내용의 사실성, 인용의 정확성, 학술적 타당성이나 연구 윤리를 판정하는 도구가 아니라 **작성 중 다시 확인할 후보를 빠르게 찾는 보조 도구**로 사용하는 것을 권장합니다.

## 개인정보

Python 버전의 문장 분석은 로컬에서 수행됩니다. 별도의 AI API 호출이나 원격 서버 전송 기능은 포함되어 있지 않습니다.

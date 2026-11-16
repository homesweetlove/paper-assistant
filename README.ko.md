<div align="center">

# Paper Assistant

**한국어 논문·보고서용 오프라인 글쓰기 검사 도구**

[![Python CI](https://github.com/homesweetlove/paper-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/homesweetlove/paper-assistant/actions/workflows/ci.yml)
[![Windows EXE](https://img.shields.io/badge/Windows-EXE-236d9d?logo=windows)](https://github.com/homesweetlove/paper-assistant/releases)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3572A5?logo=python&logoColor=white)](pyproject.toml)
[![MIT License](https://img.shields.io/badge/License-MIT-197B64)](LICENSE)

[**English**](README.md) · [**다운로드**](https://github.com/homesweetlove/paper-assistant/releases) · [**변경 기록**](CHANGELOG.md)

</div>

Paper Assistant는 한국어 논문과 보고서를 작성할 때 검토할 만한 표현을 빠르게 찾아주는 도구입니다. **원고를 외부 서버나 AI API에 전송하지 않고 로컬에서 분석**합니다. 결과는 정규식·휴리스틱 기반의 참고 제안이며, **문장이 틀렸다거나 논문이 학술적으로 타당하다는 판정이 아닙니다.**

## 주요 기능

| 구분 | 기능 |
| --- | --- |
| 문장 검사 | 긴 문장, 감탄·의문 표현, 문두 접속어, 구어체 어미, 1인칭·주관적 수식어 |
| 반복 검사 | 연속 중복 단어, 어미 반복, 자주 사용한 어휘 |
| 학술 검사(선택) | 약어의 첫 정의 확인, ms 단위 표기, 그림·표 본문 참조 누락 후보 |
| 통계 | 글자·단어·문장·문단 수, 평균 문장 길이, 단어 빈도, DOI 문자열 수 |
| 검토 화면 | 유형별 색상 강조, 검사 결과 클릭 시 원문 위치 이동, 입력 중 자동 분석 |
| 원본 보호 | DOCX를 읽기 전용으로 분석하고 기존 파일 덮어쓰기 차단 |
| 결과 저장 | 별도의 HTML·Markdown 검사 보고서, 새 텍스트 전용 DOCX 초안 |
| Word 매크로 | 사용자가 직접 실행하는 댓글 기반 검사; 기존 형광펜·댓글 보존 |

## 설치 및 실행

**Windows:** [Releases](https://github.com/homesweetlove/paper-assistant/releases)에 게시된 `PaperAssistant.exe`를 다운로드하면 Python 없이 사용할 수 있습니다. 현재 EXE는 **코드 서명되지 않은 파일**이므로 반드시 릴리스 출처와 SHA-256을 확인하세요. Windows SmartScreen 경고가 나타날 수 있습니다.

**Python:**

```powershell
python -m pip install -r requirements.txt
python paper_assistant.pyw
```

Python 3.10 이상과 Tkinter가 필요합니다. `.docx` 문서 지원은 `python-docx`를 사용합니다.

## 사용 방법

1. `.docx`, `.txt`, `.md` 파일을 열거나 직접 원고를 입력합니다.
2. 긴 문장 기준을 조절하면서 문장·문체·반복 검사 결과를 확인합니다.
3. 필요하면 **학술 표기 검사(실험적)**를 켭니다.
4. 검사 결과를 **HTML 또는 Markdown 보고서**로 별도 저장합니다.
5. 텍스트만 새 Word 문서로 내보낼 수도 있습니다. 이 기능은 **원본의 표·이미지·글꼴·각주를 복제하지 않으며**, 원본 파일은 덮어쓸 수 없습니다.

Word 문서는 본문과 표의 텍스트를 순서대로 읽지만, 각주·도형 등 일부 요소는 분석에서 제외될 수 있습니다. 반드시 원본 파일을 보관하세요.

### Word VBA 사용

Microsoft Word의 `Alt + F11` → **File → Import File**에서 아래 중 **하나만** 가져옵니다.

- `PaperAssist_ko.bas`: 한국어 검사 매크로. 한글 Windows에서 가져오기 쉽도록 CP949 인코딩으로 제공.
- `PaperAssist.bas`: 기본 영문 설명을 제공하는 매크로.

한국어 모듈의 `전체검사`를 직접 실행하면 문서에 검토 댓글을 추가합니다. `표시지우기`는 Paper Assistant가 생성한 댓글만 제거합니다. **원래 있던 형광펜과 다른 댓글은 지우지 않습니다.** Word 시작 자동 실행과 1초 간격 반복 타이머는 제거했습니다.

## 개발 및 검증

```powershell
python -m unittest discover -s tests -v
python -m py_compile paper_assistant.pyw
```

GitHub Actions가 Windows·Linux에서 테스트하며, 버전 태그를 푸시하면 Windows EXE를 자동 생성합니다. [배포 안내](docs/RELEASE.md)를 참고하세요.

## 한계와 주의사항

- 한국어 문장 분리 및 표현 검사는 휴리스틱으로, **오탐이 발생할 수 있습니다.**
- DOI 문자열 수는 DOI 유효성 검증이 아닙니다. 외부 참고문헌 데이터베이스 조회도 하지 않습니다.
- 논문의 사실성·표절·통계적 타당성·게재 가능성을 판정하지 않습니다.
- HTML·Markdown 보고서에는 원고 일부가 들어갈 수 있으니 원고만큼 안전하게 관리하세요.
- Word 매크로는 코드 차원의 안전장치를 적용했으며, Microsoft Word 실제 설치 환경에서 추가 검증이 필요합니다.

[MIT 라이선스](LICENSE) · [보안 정책](SECURITY.md) · [변경 기록](CHANGELOG.md)

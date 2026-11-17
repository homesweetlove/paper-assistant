<div align="center">

# Paper Assistant

**한국어 논문 오프라인 검사 + 선택형 AI 논문 작성 도구**

[![Python CI](https://github.com/homesweetlove/paper-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/homesweetlove/paper-assistant/actions/workflows/ci.yml)
[![Windows EXE](https://img.shields.io/badge/Windows-EXE-236d9d?logo=windows)](https://github.com/homesweetlove/paper-assistant/releases)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3572A5?logo=python&logoColor=white)](pyproject.toml)
[![MIT License](https://img.shields.io/badge/License-MIT-197B64)](LICENSE)

[**English**](README.md) · [**다운로드**](https://github.com/homesweetlove/paper-assistant/releases) · [**변경 기록**](CHANGELOG.md)

</div>

Paper Assistant는 한국어 논문과 보고서에서 검토할 만한 표현을 찾아주는 도구입니다. 기존 **오프라인 검사 모드**는 원고를 외부 서버나 AI API에 전송하지 않습니다. 검사 결과는 정규식·휴리스틱 기반의 참고 제안이며, **문장이 틀렸다거나 연구가 타당하다는 판정이 아닙니다.**

새 **AI 논문 작성 모드**는 별도로 설치한 [Google Research PaperOrchestra](https://github.com/google-research/paper-orchestra)를 연결하는 선택 기능입니다. 사용자가 전송에 명시적으로 동의한 경우에만 연구 자료를 모델·논문 검색 API로 전송합니다.

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
| AI 논문 작성(선택) | PaperOrchestra 기반 목차·선행연구·본문·개선 및 시각자료 생성 |
| 한국어·영어 선택 | 학술 문체 지시, 한국어 XeLaTeX·kotex 조판 지원 |
| 연구 프로젝트 관리 | sEMG·RAM Flow 연구 자료의 분리 저장 및 백업 |

## 설치 및 실행

**Windows:** [Releases](https://github.com/homesweetlove/paper-assistant/releases)에 게시된 `PaperAssistant.exe`를 다운로드하면 Python 없이 사용할 수 있습니다. 현재 EXE는 **코드 서명되지 않은 파일**이므로 반드시 릴리스 출처와 SHA-256을 확인하세요. Windows SmartScreen 경고가 나타날 수 있습니다.

**Python:**

```powershell
python -m pip install -r requirements.txt
python paper_assistant.pyw
```

Python 3.10 이상과 Tkinter가 필요합니다. `.docx` 문서 지원은 `python-docx`를 사용합니다.

### PaperOrchestra AI 논문 작성 (선택 기능)

AI 모델과 PaperOrchestra는 이 저장소·EXE에 포함되지 않습니다. [PaperOrchestra 설치 안내](https://github.com/google-research/paper-orchestra#installation)에 따라 Python 3.11 가상환경과 Gemini API 키를 별도로 준비하세요.

1. Paper Assistant 상단의 **AI 논문 작성** 버튼을 누릅니다.
2. 연구 프로젝트(**sEMG / RAM Flow**)와 작성 언어(**한국어 / English**)를 선택합니다.
3. **엔진 폴더**에 로컬 PaperOrchestra 설치 경로를 지정합니다. 기본값은 `문서/ResearchPapers/paper-orchestra`입니다.
4. **연구 아이디어**와 **실험 기록** 탭을 작성합니다. 연구 자료는 **프로젝트 저장 (로컬)** 버튼으로 보관할 수 있으며, 기존 내용 변경 시 백업을 생성합니다.
5. 실제 측정 그래프가 있다면 작업 폴더의 `projects/semg/figures/` 또는 `projects/ramflow/figures/`에 PNG·JPG·PDF 파일을 넣습니다.
6. **AI 논문 작성 시작**을 누르고 외부 API 전송 및 비용 안내를 확인합니다. 실행 기록을 확인하거나 작업을 중단할 수 있습니다.
7. 결과는 작업 폴더의 `runs/semg/` 또는 `runs/ramflow/` 아래 고유한 실행 폴더에 저장됩니다. 원본 원고와 PaperOrchestra 설치 파일은 수정하지 않습니다.

**한국어 논문 주의:** 한국어 모드는 에이전트에 국문 학술 문체 지시를 추가하고 `xelatex`·`bibtex`·`kotex`로 PDF를 컴파일합니다. MiKTeX 또는 TeX Live에서 해당 도구를 별도로 설치해야 합니다. 포함된 CVPR·ICLR 템플릿은 KCI 학술지 양식이 아니며, 실제 투고 전 학술지 규정·수치·인용 출처와 PDF 조판을 검토해야 합니다. AI 모델·TeX 설치 상태에 따라 생성이 실패할 수 있습니다.

**개인정보 및 비용:** 오프라인 검사는 기존대로 외부 전송이 없습니다. AI 모드는 PaperOrchestra가 외부 서비스를 호출하므로 키와 미공개 연구 자료를 안전하게 관리해야 하며, API 비용이 발생할 수 있습니다. 키는 별도 PaperOrchestra 폴더의 `.env`에만 저장하세요.

**라이선스:** 이 앱은 MIT, 별도로 설치하는 PaperOrchestra는 Apache-2.0 라이선스입니다. 해당 프로젝트의 원본 고지와 사용 조건을 유지해야 합니다.

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
- AI 논문 작성 기능은 별도 PaperOrchestra 설치·모델 API·LaTeX 환경이 필요하며, 논문 내용의 사실성과 학술적 기여를 보증하지 않습니다.

[MIT 라이선스](LICENSE) · [보안 정책](SECURITY.md) · [변경 기록](CHANGELOG.md)

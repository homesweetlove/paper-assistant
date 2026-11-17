<div align="center">

# Paper Assistant

**Offline Korean manuscript review + optional AI research-paper writing**

[![Python CI](https://github.com/homesweetlove/paper-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/homesweetlove/paper-assistant/actions/workflows/ci.yml)
[![Windows EXE](https://img.shields.io/badge/Windows-EXE-236d9d?logo=windows)](https://github.com/homesweetlove/paper-assistant/releases)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3572A5?logo=python&logoColor=white)](pyproject.toml)
[![MIT License](https://img.shields.io/badge/License-MIT-197B64)](LICENSE)

[**한국어 설명**](README.ko.md) · [**Releases**](https://github.com/homesweetlove/paper-assistant/releases) · [**Change log**](CHANGELOG.md)

</div>

Paper Assistant helps reviewers identify passages worth revisiting in Korean academic papers and reports. Its original review mode works **locally**, without an AI API, internet connection, telemetry, or server-side document upload. Its suggestions are transparent, rule-based heuristics — **not verdicts about correctness or research quality**.

The optional **AI 논문 작성** window connects to a separately installed [Google Research PaperOrchestra](https://github.com/google-research/paper-orchestra). It is opt-in and sends supplied research materials to configured external model/search APIs only after a confirmation. The two modes are independent.

## Highlights

| | Feature | What it does |
| --- | --- | --- |
| 📝 | Text inspection | Long sentences, conversational endings, first-person language, repetitive expressions |
| 📚 | Optional academic checks | Abbreviation definitions, inconsistent millisecond units, figures/tables without a matching body reference |
| 📈 | Statistics | Character, sentence, paragraph, word counts, repeated words and DOI string counts |
| 🔎 | Review navigator | Colored issue highlights, click-to-jump, issue list, live analysis |
| 🔐 | Original protection | Reads Word documents without modifying them; blocks overwriting input or existing output files |
| 📑 | Review report | Save a separate HTML or Markdown report, with contextual snippets |
| 🧩 | Word VBA | Optional user-triggered review comments; preserves existing highlights and user comments |
| 🎻 | Optional AI writing | PaperOrchestra outline, literature review, section writing, refinement, and optional figure generation |
| 🌐 | Korean/English | Language-specific writing instructions; Korean uses XeLaTeX and the `kotex` package |
| 🗂️ | Research projects | Separate sEMG and RAM Flow local notes, snapshots, and generated results |

## Install and run

**Windows:** Get the optional packaged `PaperAssistant.exe` from [GitHub Releases](https://github.com/homesweetlove/paper-assistant/releases) when available. It is currently **unsigned**, so review its origin and SHA-256 checksum. A warning may appear on Windows SmartScreen. No Excel or Word installation is needed for the Python GUI.

**Python (Windows/Linux/macOS):**

```bash
python -m pip install -r requirements.txt
python paper_assistant.pyw
```

Python 3.10+ and Tkinter are required. On some Linux distributions Tkinter is a separate system package. Word `.docx` support uses `python-docx`.

### Optional PaperOrchestra connection (AI mode)

This integration **does not bundle** Google's research framework, AI models, or TeX. Install PaperOrchestra separately following [its README](https://github.com/google-research/paper-orchestra#installation), including its Python 3.11 environment and Gemini API configuration.

1. Open `AI 논문 작성` in the Paper Assistant toolbar. This feature works in the existing Windows Tkinter app; it does not start the upstream Linux-oriented Streamlit frontend.
2. Choose a project (`sEMG` or `RAM Flow`) and manuscript language (`한국어` or `English`).
3. Select the local PaperOrchestra folder (the default is `Documents/ResearchPapers/paper-orchestra`). Use that installation's `.venv` for AI dependencies.
4. Enter the **Research Idea** and **Experimental Log** in separate tabs. Save locally if desired; the app preserves backups of changed notes. For figures, put verified PNG/JPEG/PDF files under `PaperAssistant/projects/<project>/figures` in the workspace directory.
5. Select a model and template. Press `AI 논문 작성 시작`, review the external transmission/cost confirmation, and monitor the execution log. Outputs are saved in newly created, timestamped `PaperAssistant/runs/<project>/` folders.

**Korean manuscripts:** The integration adds Korean academic-writing instructions and requests Unicode-aware compilation through `xelatex`, `bibtex`, and `kotex`. Install these tools via MiKTeX or TeX Live first. The included CVPR/ICLR templates are *examples*, not KCI-compliant templates. Korean results are best-effort and still require verification of citations, numerical claims, layout and target journal guidelines. Failed compilation is surfaced as an error; the app does not claim a PDF succeeded unless it exists.

**Privacy:** Offline review still makes no API requests. AI writing makes third-party requests through your separate PaperOrchestra environment. API keys belong in that checkout's local `.env`, never in a manuscript or committed repository. The app itself does not store API keys. See [Security](SECURITY.md).

**Licensing:** This project is MIT-licensed. The separately installed PaperOrchestra project is Apache-2.0 licensed and is not redistributed here; retain its original notices and comply with its terms.

### Read-only manuscript workflow

1. Open a `.docx`, `.txt`, or `.md` file — or paste text directly.
2. Review sentence/style/repetition suggestions and change the long-sentence threshold as needed.
3. Turn on **experimental academic checks** only if you want extra notation suggestions.
4. Export a **separate HTML or Markdown report**. The input document is never written back automatically.
5. If needed, create a **new text-only DOCX draft**. This does **not** copy the original document's figures, styles, footnotes, or embedded objects, and cannot overwrite the loaded original.

The `.docx` analyzer includes paragraphs and tables in reading order; some elements such as footnotes or embedded shapes may not be included. Always retain the original document.

## Microsoft Word VBA (optional)

- `PaperAssist_ko.bas` — Korean review comments; saved in Korean Windows-compatible CP949 encoding.
- `PaperAssist.bas` — simpler English-language review comments.

Open Word → `Alt + F11` → **File → Import File** and import **only one** module. Run `전체검사` (Korean) or `CheckAll` (English) manually; run `표시지우기` or `ClearMarks` to remove **only Paper Assistant's own comments**. Existing document highlights and other people's comments are preserved. There is no automatic 1-second timer or `AutoExec` macro. Word macro security settings remain the user's responsibility.

## Build and quality

```bash
python -m unittest discover -s tests -v
python -m py_compile paper_assistant.pyw
```

CI runs offline tests on Windows and Linux. The Windows release workflow packages the GUI using PyInstaller and publishes an EXE with SHA-256 on a `v*` tag. See [release instructions](docs/RELEASE.md).

## Limitations

- Korean segmentation and writing rules are approximate. Some suggestions will be false positives.
- DOI string detection is **not** DOI verification; there is no external citation lookup.
- Academic checks cannot assess novelty, statistical validity, factual accuracy, plagiarism, or whether a paper is publishable.
- Report files may include manuscript excerpts. Handle them as private research material.
- VBA behavior has source-level safety checks, but must be validated in the user's installed Microsoft Word version.
- AI writing requires a correctly installed upstream environment, network/API access and (for PDF output) TeX. Model access may cost money. AI-generated text does not validate experimental results or publication eligibility.

The source is released under the [MIT License](LICENSE). See [Security](SECURITY.md) and [Changelog](CHANGELOG.md).

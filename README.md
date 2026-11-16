<div align="center">

# Paper Assistant

**Offline academic writing review for Korean manuscripts**

[![Python CI](https://github.com/homesweetlove/paper-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/homesweetlove/paper-assistant/actions/workflows/ci.yml)
[![Windows EXE](https://img.shields.io/badge/Windows-EXE-236d9d?logo=windows)](https://github.com/homesweetlove/paper-assistant/releases)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3572A5?logo=python&logoColor=white)](pyproject.toml)
[![MIT License](https://img.shields.io/badge/License-MIT-197B64)](LICENSE)

[**한국어 설명**](README.ko.md) · [**Releases**](https://github.com/homesweetlove/paper-assistant/releases) · [**Change log**](CHANGELOG.md)

</div>

Paper Assistant helps reviewers identify passages worth revisiting in Korean academic papers and reports. It works **locally**, without an AI API, internet connection, telemetry, or server-side document upload. Its suggestions are transparent, rule-based heuristics — **not verdicts about correctness or research quality**.

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

## Install and run

**Windows:** Get the optional packaged `PaperAssistant.exe` from [GitHub Releases](https://github.com/homesweetlove/paper-assistant/releases) when available. It is currently **unsigned**, so review its origin and SHA-256 checksum. A warning may appear on Windows SmartScreen. No Excel or Word installation is needed for the Python GUI.

**Python (Windows/Linux/macOS):**

```bash
python -m pip install -r requirements.txt
python paper_assistant.pyw
```

Python 3.10+ and Tkinter are required. On some Linux distributions Tkinter is a separate system package. Word `.docx` support uses `python-docx`.

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

The source is released under the [MIT License](LICENSE). See [Security](SECURITY.md) and [Changelog](CHANGELOG.md).

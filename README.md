[![English](https://img.shields.io/badge/README-English-24292f?style=for-the-badge)](./README.md) [![한국어](https://img.shields.io/badge/README-%ED%95%9C%EA%B5%AD%EC%96%B4-24292f?style=for-the-badge)](./README.ko.md)

# Paper Assistant

A lightweight offline writing assistant for reviewing Korean academic-paper and report drafts.

It analyzes text locally without an AI API or external server and provides both a Python GUI and Microsoft Word VBA macros.

## Features

### Python GUI

`paper_assistant.pyw` is a Tkinter-based desktop tool.

- Write or paste text directly
- Open / save `.docx` documents
- Character, word, sentence, and paragraph statistics
- Average sentence-length calculation
- Long-sentence detection
- Exclamation / question sentence detection
- Conversational sentence-ending detection
- Sentence-opening conjunction, first-person expression, and excessive modifier checks
- Repeated-word and word-frequency analysis
- Real-time analysis and problem-area highlighting

### Microsoft Word VBA

- `PaperAssist.bas` — VBA module for real-time sentence checking in Word
- `PaperAssist_ko.bas` — VBA module designed with Korean usage in mind

The Word macro version highlights long sentences, exclamations/questions, and selected conversational expressions.

## Runtime

- Windows recommended
- Python 3.x
- Tkinter
- `python-docx` — used for opening/saving Word documents

Tkinter is included in standard Windows Python installations.

### Install

```powershell
pip install python-docx
```

### Run

```powershell
pythonw paper_assistant.pyw
```

To keep the console visible:

```powershell
python paper_assistant.pyw
```

## Using the Word VBA Version

1. Open the VBA editor in Microsoft Word with `Alt + F11`.
2. Use **File → Import File** to import `PaperAssist.bas` or `PaperAssist_ko.bas`.
3. Use it in a document where macro execution is allowed.
4. Run `CheckAll` to review the full document.
5. Run `ClearMarks` to remove the highlights.

Follow the macro security policy of your PC or organization.

## Project Structure

```text
paper-assistant/
├─ paper_assistant.pyw   # Python/Tkinter desktop app
├─ PaperAssist.bas       # Word VBA version
├─ PaperAssist_ko.bas    # Korean-oriented Word VBA version
└─ README.md
```

## About the Analysis Rules

Checks are based on regular expressions and simple heuristics. A flagged sentence is not necessarily incorrect.

This tool does not judge factual accuracy, citation correctness, academic validity, or research ethics. It is intended as a **writing assistant that quickly surfaces passages worth reviewing again**.

## Privacy

The Python version performs text analysis locally. It does not include AI API calls or remote-server uploads.

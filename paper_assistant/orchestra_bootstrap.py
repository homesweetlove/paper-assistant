"""Korean-language compatibility launcher for an external PaperOrchestra checkout.

This script runs inside PaperOrchestra's *own* Python environment. It changes
process-local prompts and LaTeX compilation without editing upstream files.
"""

from __future__ import annotations

import argparse
import os
import runpy
import shutil
import subprocess
import sys
from pathlib import Path


KOREAN_DIRECTIVE = (
    "\n\nIMPORTANT OUTPUT LANGUAGE RULE: Write manuscript prose, titles, abstract, "
    "headings, tables and figure captions in formal Korean (한국어). "
    "Do not translate BibTeX citation keys, identifiers, author names or titles "
    "of cited publications. Preserve all experimental numerical values verbatim. "
    "Never fabricate results, citations, or data. Keep the LaTeX compilable "
    "with XeLaTeX and the kotex package.\n"
)


def _compile_korean_latex(cwd: str, pdf_file: str, texfile_name: str = "template", timeout: int = 30) -> None:
    """Replace upstream pdflatex compilation with Unicode-aware XeLaTeX."""
    tex_dir = Path(cwd)
    for binary in ("xelatex", "bibtex"):
        if not shutil.which(binary):
            raise RuntimeError(
                f"한국어 PDF를 생성하려면 {binary}가 필요합니다. "
                "MiKTeX/TeX Live에서 XeLaTeX, BibTeX 및 kotex를 설치하세요."
            )
    pdf = tex_dir / (texfile_name + ".pdf")
    if pdf.exists():
        pdf.unlink()
    env = os.environ.copy()
    for var in ("TEXINPUTS", "TEXMFHOME", "TEXMF", "TEXMFVAR", "TEXMFCONFIG"):
        env.pop(var, None)
    commands = (
        ("xelatex", "-interaction=nonstopmode", "-halt-on-error", texfile_name + ".tex"),
        ("bibtex", texfile_name),
        ("xelatex", "-interaction=nonstopmode", "-halt-on-error", texfile_name + ".tex"),
        ("xelatex", "-interaction=nonstopmode", "-halt-on-error", texfile_name + ".tex"),
    )
    for command in commands:
        finished = subprocess.run(
            command, cwd=tex_dir, env=env, text=True, encoding="utf-8",
            errors="replace", capture_output=True, timeout=max(90, timeout), check=False,
        )
        if finished.returncode:
            tail = (finished.stdout + "\n" + finished.stderr)[-5000:]
            raise RuntimeError(f"{' '.join(command)} 실패:\n{tail}")
    if not pdf.is_file():
        raise RuntimeError("XeLaTeX가 PDF를 생성하지 못했습니다.")
    destination = Path(pdf_file)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if pdf.resolve() != destination.resolve():
        shutil.copy2(pdf, destination)


def _apply_korean_overrides() -> None:
    from methods.agents import content_refinement_agent, literature_review_agent, outline_agent, section_writing_agent

    outline_agent.outline_agent_system_prompt += KOREAN_DIRECTIVE
    literature_review_agent.literature_review_agent_writter_prompt += KOREAN_DIRECTIVE
    section_writing_agent.section_writing_agent_prompt += KOREAN_DIRECTIVE
    content_refinement_agent.content_refinement_agent_system_prompt += KOREAN_DIRECTIVE
    content_refinement_agent.compile_latex = _compile_korean_latex


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run PaperOrchestra in Korean mode")
    parser.add_argument("--engine-root", required=True)
    options, arguments = parser.parse_known_args(argv)
    if arguments and arguments[0] == "--":
        arguments = arguments[1:]
    engine = Path(options.engine_root).expanduser().resolve()
    cli = engine / "paper_writing_cli.py"
    if not cli.is_file():
        parser.error("올바른 PaperOrchestra 설치 경로가 아닙니다.")

    # An actionable error before running expensive AI requests.
    missing = [binary for binary in ("xelatex", "bibtex") if not shutil.which(binary)]
    if missing:
        parser.error("한국어 PDF 빌드 도구가 없습니다: " + ", ".join(missing) + ". MiKTeX 또는 TeX Live를 설치하세요.")

    sys.path.insert(0, str(engine))
    os.chdir(engine)
    _apply_korean_overrides()
    sys.argv = [str(cli), *arguments]
    runpy.run_path(str(cli), run_name="__main__")

    # Upstream may finish with code 0 even when its own retry loop failed.
    if "--output_dir" in arguments:
        output = Path(arguments[arguments.index("--output_dir") + 1])
        if not (output / "final_paper.pdf").is_file():
            print("한국어 논문 PDF가 생성되지 않았습니다. 실행 기록과 LaTeX 오류를 확인하세요.", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

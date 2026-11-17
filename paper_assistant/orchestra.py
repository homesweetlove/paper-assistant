"""Optional, explicitly authorized PaperOrchestra integration.

The offline manuscript analyzer never imports an LLM SDK. This module prepares
separate, inspectable research inputs and delegates paper generation to a
user-installed copy of the upstream PaperOrchestra project.
"""

from __future__ import annotations

import os
import re
import shutil
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


PROJECTS = {
    "semg": "sEMG 팔꿈치 관절각 연구",
    "ramflow": "RAM Flow 메모리 연구",
}
LANGUAGES = {"ko": "한국어", "en": "English"}
TEMPLATES = ("cvpr2025", "iclr2025")

INITIAL_IDEAS = {
    "semg": (
        "# 연구 아이디어\n"
        "sEMG 기반 팔꿈치 관절각 추정에서 신규 피험자 보정 시간의 영향을 분석한다.\n\n"
        "# 연구 질문\n"
        "보정 시간 0·5·15·30초에 따른 MAE/RMSE 변화와 피험자 간 일반화를 검증한다.\n\n"
        "# 연구 기여\n실험을 통해 입증한 내용만 여기에 기록한다.\n"
    ),
    "ramflow": (
        "# 연구 아이디어\n"
        "RAM Flow의 Windows 메모리 관리 정책이 시스템 응답성과 메모리 사용에 미치는 영향을 평가한다.\n\n"
        "# 비교 기준\nWindows 기본 상태 및 정의된 기준선과 동일 조건에서 비교한다.\n\n"
        "# 연구 기여\n실험으로 입증된 내용만 여기에 기록한다.\n"
    ),
}
INITIAL_LOG = (
    "# 실험 환경\n"
    "데이터셋, 하드웨어·소프트웨어 버전, 실험 분할 및 반복 횟수를 기록한다.\n\n"
    "# 실제 측정 결과\n"
    "아직 측정하지 않은 수치와 결과는 기재하지 않는다.\n\n"
    "# 한계와 재현 정보\n"
    "실험 코드, 시드, 제외 기준 및 제한사항을 기록한다.\n"
)

LANGUAGE_GUIDANCE = {
    "ko": (
        "PAPER ASSISTANT WRITING LANGUAGE: Korean (한국어). "
        "Write the title, abstract, section headings, figure/table captions, "
        "and all manuscript prose in formal Korean academic language. "
        "Keep authors' names, identifiers, technical acronyms, bibliography "
        "entries and original publication titles unchanged. Cite real sources "
        "with their exact keys. Do not invent experiments, numbers or citations. "
        "Use valid LaTeX with Hangul supported by XeLaTeX and the kotex package."
    ),
    "en": (
        "PAPER ASSISTANT WRITING LANGUAGE: English. "
        "Write manuscript prose in formal academic English. "
        "Do not invent experiments, numbers, results or citations."
    ),
}


def default_engine_directory() -> Path:
    return Path.home() / "Documents" / "ResearchPapers" / "paper-orchestra"


def default_workspace_directory() -> Path:
    return Path.home() / "Documents" / "ResearchPapers" / "PaperAssistant"


def project_files(workspace: Path, project: str) -> tuple[Path, Path]:
    if project not in PROJECTS:
        raise ValueError("지원하지 않는 연구 프로젝트입니다.")
    root = Path(workspace).expanduser() / "projects" / project
    return root / "idea_sparse.md", root / "experimental_log.md"


def read_project(workspace: Path, project: str) -> tuple[str, str]:
    idea_path, log_path = project_files(workspace, project)
    idea = idea_path.read_text(encoding="utf-8-sig") if idea_path.exists() else INITIAL_IDEAS[project]
    log = log_path.read_text(encoding="utf-8-sig") if log_path.exists() else INITIAL_LOG
    return idea, log


def _safe_replace_text(destination: Path, content: str) -> None:
    """Preserve a recoverable copy if a user explicitly saves changed notes."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        old = destination.read_text(encoding="utf-8-sig")
        if old == content:
            return
        backup = destination.with_name(destination.name + "." + uuid.uuid4().hex[:8] + ".bak")
        shutil.copy2(destination, backup)
    tmp = destination.with_name(destination.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        tmp.write_text(content, encoding="utf-8")
        tmp.replace(destination)
    finally:
        if tmp.exists():
            tmp.unlink()


def save_project(workspace: Path, project: str, idea: str, log: str) -> tuple[Path, Path]:
    if not idea.strip() or not log.strip():
        raise ValueError("연구 아이디어와 실험 기록을 모두 입력하세요.")
    idea_path, log_path = project_files(workspace, project)
    _safe_replace_text(idea_path, idea)
    _safe_replace_text(log_path, log)
    return idea_path, log_path


@dataclass(frozen=True)
class RunOptions:
    engine_directory: Path
    workspace_directory: Path
    project: str
    language: str = "ko"
    template: str = "cvpr2025"
    model: str = "gemini-3.1-pro-preview"
    plotting: bool = False


@dataclass(frozen=True)
class PreparedRun:
    command: tuple[str, ...]
    work_directory: Path
    result_directory: Path
    environment: dict[str, str]


def _engine_python(engine: Path) -> Path:
    candidates = (
        engine / ".venv" / "Scripts" / "python.exe",
        engine / ".venv" / "bin" / "python",
    )
    for path in candidates:
        if path.is_file():
            return path
    if not getattr(sys, "frozen", False):
        return Path(sys.executable)
    installed = shutil.which("python")
    return Path(installed) if installed else engine / ".venv" / "Scripts" / "python.exe"


def _bootstrap_path() -> Path:
    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS"))
        return base / "paper_assistant" / "orchestra_bootstrap.py"
    return Path(__file__).with_name("orchestra_bootstrap.py")


def prepare_run(options: RunOptions, idea: str, log: str) -> PreparedRun:
    """Stage a *new* run; never write into or modify the upstream checkout."""
    if options.project not in PROJECTS:
        raise ValueError("프로젝트를 선택하세요.")
    if options.language not in LANGUAGES:
        raise ValueError("작성 언어를 선택하세요.")
    if options.template not in TEMPLATES:
        raise ValueError("지원하지 않는 논문 템플릿입니다.")
    if not re.fullmatch(r"[A-Za-z0-9._:-]{2,100}", options.model):
        raise ValueError("모델 이름에 허용되지 않는 문자가 있습니다.")
    if not idea.strip() or not log.strip():
        raise ValueError("연구 아이디어와 실험 기록을 모두 입력하세요.")
    if log.strip() == INITIAL_LOG.strip():
        raise ValueError("실험 기록이 기본 안내문 그대로입니다. 실제 실험 조건과 측정 결과를 입력한 후 실행하세요.")

    engine = Path(options.engine_directory).expanduser().resolve()
    workspace = Path(options.workspace_directory).expanduser().resolve()
    cli = engine / "paper_writing_cli.py"
    template = engine / "templates" / options.template
    if not cli.is_file() or not (template / "template.tex").is_file() or not (template / "guidelines.md").is_file():
        raise FileNotFoundError("PaperOrchestra 폴더와 템플릿을 확인하세요. (paper_writing_cli.py 필요)")
    python = _engine_python(engine)
    if not python.is_file():
        raise FileNotFoundError("PaperOrchestra용 Python 실행 파일을 찾을 수 없습니다.")
    if options.language == "ko" and not _bootstrap_path().is_file():
        raise FileNotFoundError("한국어 실행 모듈을 찾을 수 없습니다. 설치 파일을 확인하세요.")
    if engine == workspace or engine in workspace.parents:
        raise ValueError("출력 폴더는 PaperOrchestra 설치 폴더 바깥에 지정하세요.")

    run_name = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:6]
    run_root = workspace / "runs" / options.project / run_name
    run_root.mkdir(parents=True, exist_ok=False)
    raw = run_root / "raw_materials"
    raw.mkdir()
    template_copy = run_root / "template"
    shutil.copytree(template, template_copy)

    # Source materials remain untouched; language rules are scoped to this run.
    policy = LANGUAGE_GUIDANCE[options.language]
    (raw / "idea_sparse.md").write_text(idea.rstrip() + "\n\n## Writing policy\n" + policy + "\n", encoding="utf-8")
    (raw / "experimental_log.md").write_text(log, encoding="utf-8")
    # Reuse verified plots already placed in the saved local research project.
    figures = project_files(workspace, options.project)[0].parent / "figures"
    if figures.is_dir():
        copied_figures = raw / "figures"
        copied_figures.mkdir()
        for item in figures.iterdir():
            if item.is_file() and item.suffix.lower() in {".png", ".jpg", ".jpeg", ".pdf"}:
                shutil.copy2(item, copied_figures / item.name)
    guidelines = template_copy / "guidelines.md"
    with guidelines.open("a", encoding="utf-8") as handle:
        handle.write("\n\n## Paper Assistant language requirements\n" + policy + "\n")

    if options.language == "ko":
        tex = template_copy / "template.tex"
        source = tex.read_text(encoding="utf-8")
        if "\\usepackage{kotex}" not in source:
            if "\\begin{document}" not in source:
                raise ValueError("LaTeX 문서 템플릿에 begin{document}가 없습니다.")
            source = source.replace("\\begin{document}", "\\usepackage{kotex}\n\\begin{document}", 1)
        for english, korean in (
            ("Introduction", "서론"),
            ("Related Work", "관련 연구"),
            ("Methodology", "연구 방법"),
            ("Experiments", "실험 및 결과"),
            ("Conclusion", "결론"),
        ):
            source = source.replace("\\section{" + english + "}", "\\section{" + korean + "}")
        tex.write_text(source, encoding="utf-8")

    result = run_root / "generated"
    args = (
        "--raw_materials_dir", str(raw),
        "--latex_template_dir", str(template_copy),
        "--output_dir", str(result),
        "--writer_model_name", options.model,
        "--reflection_model_name", options.model,
        "--use_plotting", str(options.plotting).lower(),
    )
    if options.language == "ko":
        command = (str(python), str(_bootstrap_path()), "--engine-root", str(engine), "--") + args
    else:
        command = (str(python), str(cli)) + args
    environment = os.environ.copy()
    environment["PYTHONUTF8"] = "1"
    environment["PYTHONIOENCODING"] = "utf-8"
    return PreparedRun(command, engine, result, environment)

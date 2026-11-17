"""Korean Tkinter UI for optional PaperOrchestra paper generation."""

from __future__ import annotations

import os
import queue
import subprocess
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

from .orchestra import (
    LANGUAGES,
    PROJECTS,
    TEMPLATES,
    RunOptions,
    default_engine_directory,
    default_workspace_directory,
    prepare_run,
    read_project,
    save_project,
)


class PaperOrchestraWindow(tk.Toplevel):
    """Keep all external network work behind a dedicated, opt-in window."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master)
        self.title("Paper Assistant · AI 논문 작성")
        self.geometry("1060x820")
        self.minsize(790, 600)
        self.project_var = tk.StringVar(value="semg")
        self.language_var = tk.StringVar(value="ko")
        self.template_var = tk.StringVar(value="cvpr2025")
        self.model_var = tk.StringVar(value="gemini-3.1-pro-preview")
        self.engine_var = tk.StringVar(value=str(default_engine_directory()))
        self.workspace_var = tk.StringVar(value=str(default_workspace_directory()))
        self.plotting_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="오프라인에서 작성 자료를 준비한 뒤 AI 작업을 시작하세요.")
        self._active_project = "semg"
        self._drafts: dict[str, tuple[str, str]] = {}
        self._events: queue.Queue[tuple[str, object]] = queue.Queue()
        self._running = False
        self._process: subprocess.Popen[str] | None = None
        self._cancel_requested = threading.Event()
        self._current_result: Path | None = None
        self._build_ui()
        self._load_project("semg")
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self) -> None:
        layout = ttk.Frame(self, padding=16)
        layout.pack(fill="both", expand=True)
        ttk.Label(layout, text="AI 논문 작성", font=("맑은 고딕", 17, "bold")).pack(anchor="w")
        ttk.Label(
            layout,
            text="기존 오프라인 검사는 그대로 유지됩니다. AI 작업을 시작하면 입력한 연구 자료가 외부 API로 전송됩니다.",
            foreground="#825520",
            wraplength=950,
        ).pack(fill="x", pady=(3, 12))

        settings = ttk.LabelFrame(layout, text="연구 및 모델 설정", padding=9)
        settings.pack(fill="x")
        settings.columnconfigure(1, weight=1)
        settings.columnconfigure(3, weight=1)

        ttk.Label(settings, text="연구 프로젝트").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        project = ttk.Combobox(settings, state="readonly", values=list(PROJECTS.values()), width=30)
        project.current(0)
        project.grid(row=0, column=1, sticky="ew", padx=4, pady=4)
        project.bind("<<ComboboxSelected>>", lambda _event: self._switch_project(list(PROJECTS)[project.current()]))
        self.project_combo = project

        ttk.Label(settings, text="작성 언어").grid(row=0, column=2, sticky="w", padx=4)
        language = ttk.Combobox(settings, state="readonly", values=list(LANGUAGES.values()), width=18)
        language.current(0)
        language.grid(row=0, column=3, sticky="ew", padx=4, pady=4)
        language.bind("<<ComboboxSelected>>", lambda _event: self.language_var.set(list(LANGUAGES)[language.current()]))

        ttk.Label(settings, text="논문 양식").grid(row=1, column=0, sticky="w", padx=4)
        ttk.Combobox(settings, state="readonly", textvariable=self.template_var, values=TEMPLATES).grid(
            row=1, column=1, sticky="ew", padx=4, pady=4
        )
        ttk.Label(settings, text="AI 모델").grid(row=1, column=2, sticky="w", padx=4)
        ttk.Combobox(
            settings, textvariable=self.model_var,
            values=("gemini-3.1-pro-preview", "gemini-3-flash-preview"),
        ).grid(row=1, column=3, sticky="ew", padx=4, pady=4)

        ttk.Label(settings, text="엔진 폴더").grid(row=2, column=0, sticky="w", padx=4)
        ttk.Entry(settings, textvariable=self.engine_var).grid(row=2, column=1, columnspan=2, sticky="ew", padx=4, pady=4)
        ttk.Button(settings, text="찾아보기", command=lambda: self._choose_directory(self.engine_var)).grid(row=2, column=3, sticky="ew", padx=4)
        ttk.Label(settings, text="작업 폴더").grid(row=3, column=0, sticky="w", padx=4)
        ttk.Entry(settings, textvariable=self.workspace_var).grid(row=3, column=1, columnspan=2, sticky="ew", padx=4, pady=4)
        ttk.Button(settings, text="찾아보기", command=lambda: self._choose_directory(self.workspace_var)).grid(row=3, column=3, sticky="ew", padx=4)

        ttk.Checkbutton(settings, text="AI 시각자료 생성 (별도 비용·결과 검증 필요)", variable=self.plotting_var).grid(
            row=4, column=0, columnspan=4, sticky="w", padx=4, pady=4
        )

        tabs = ttk.Notebook(layout)
        tabs.pack(fill="both", expand=True, pady=(10, 5))
        self.idea_editor = self._new_editor_tab(tabs, "연구 아이디어")
        self.log_editor = self._new_editor_tab(tabs, "실험 기록")

        toolbar = ttk.Frame(layout)
        toolbar.pack(fill="x", pady=(2, 6))
        ttk.Button(toolbar, text="파일 가져오기", command=lambda: self._import_file(tabs)).pack(side="left")
        self.load_button = ttk.Button(toolbar, text="저장된 프로젝트 불러오기", command=self._reload_project)
        self.load_button.pack(side="left", padx=5)
        self.save_button = ttk.Button(toolbar, text="프로젝트 저장 (로컬)", command=self._save_project)
        self.save_button.pack(side="left", padx=5)
        self.run_button = ttk.Button(toolbar, text="AI 논문 작성 시작", command=self._start)
        self.run_button.pack(side="right")
        self.cancel_button = ttk.Button(toolbar, text="작업 중단", state="disabled", command=self._cancel)
        self.cancel_button.pack(side="right", padx=5)

        ttk.Label(
            layout,
            text="한국어 PDF: XeLaTeX·BibTeX·kotex 필요  |  CVPR/ICLR은 예시 양식이며 KCI 투고 규정과 별개입니다.",
            foreground="#526475", wraplength=950,
        ).pack(anchor="w", pady=(0, 4))
        ttk.Label(layout, textvariable=self.status_var, wraplength=950).pack(fill="x", pady=(0, 5))
        self.output_log = scrolledtext.ScrolledText(layout, height=9, wrap="word", state="disabled", font=("Consolas", 9))
        self.output_log.pack(fill="both", expand=False)
        bottom = ttk.Frame(layout)
        bottom.pack(fill="x", pady=(5, 0))
        self.folder_button = ttk.Button(bottom, text="결과 폴더 열기", state="disabled", command=self._open_output)
        self.folder_button.pack(side="right")

    @staticmethod
    def _new_editor_tab(tabs: ttk.Notebook, label: str) -> tk.Text:
        frame = ttk.Frame(tabs)
        tabs.add(frame, text=label)
        editor = scrolledtext.ScrolledText(frame, wrap="word", font=("맑은 고딕", 10), undo=True)
        editor.pack(fill="both", expand=True, padx=3, pady=3)
        return editor

    def _choose_directory(self, variable: tk.StringVar) -> None:
        selected = filedialog.askdirectory(parent=self, initialdir=variable.get() if Path(variable.get()).is_dir() else str(Path.home()))
        if selected:
            variable.set(selected)

    def _contents(self) -> tuple[str, str]:
        return self.idea_editor.get("1.0", "end-1c"), self.log_editor.get("1.0", "end-1c")

    def _load_project(self, project: str) -> None:
        if project in self._drafts:
            idea, log = self._drafts[project]
        else:
            idea, log = read_project(Path(self.workspace_var.get()), project)
        for editor, text in ((self.idea_editor, idea), (self.log_editor, log)):
            editor.delete("1.0", "end")
            editor.insert("1.0", text)
        self._active_project = project
        self.project_var.set(project)
        self.status_var.set(f"{PROJECTS[project]} 자료를 불러왔습니다. 실험 결과는 실제 측정값만 기재하세요.")

    def _switch_project(self, project: str) -> None:
        self._drafts[self._active_project] = self._contents()
        try:
            self._load_project(project)
        except (OSError, UnicodeError) as exc:
            messagebox.showerror("프로젝트 불러오기", str(exc), parent=self)

    def _reload_project(self) -> None:
        if not messagebox.askyesno("프로젝트 불러오기", "현재 입력을 저장된 프로젝트 내용으로 교체할까요?", parent=self):
            return
        self._drafts.pop(self._active_project, None)
        self._load_project(self._active_project)

    def _save_project(self) -> None:
        try:
            paths = save_project(Path(self.workspace_var.get()), self._active_project, *self._contents())
        except (OSError, UnicodeError, ValueError) as exc:
            messagebox.showerror("저장 실패", str(exc), parent=self)
            return
        self.status_var.set(f"로컬 프로젝트 저장 완료: {paths[0].parent}")

    def _import_file(self, tabs: ttk.Notebook) -> None:
        path = filedialog.askopenfilename(parent=self, filetypes=[("연구 메모", "*.md *.txt")])
        if not path:
            return
        try:
            contents = Path(path).read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as exc:
            messagebox.showerror("파일 가져오기", str(exc), parent=self)
            return
        editor = self.idea_editor if tabs.index(tabs.select()) == 0 else self.log_editor
        editor.delete("1.0", "end")
        editor.insert("1.0", contents)

    def _append_log(self, line: str) -> None:
        self.output_log.configure(state="normal")
        self.output_log.insert("end", line + ("" if line.endswith("\n") else "\n"))
        self.output_log.see("end")
        self.output_log.configure(state="disabled")

    def _set_running(self, running: bool) -> None:
        self._running = running
        self.run_button.configure(state="disabled" if running else "normal")
        self.cancel_button.configure(state="normal" if running else "disabled")
        self.save_button.configure(state="disabled" if running else "normal")
        self.load_button.configure(state="disabled" if running else "normal")
        self.project_combo.configure(state="disabled" if running else "readonly")

    def _start(self) -> None:
        if self._running:
            return
        if not messagebox.askyesno(
            "외부 AI 전송 확인",
            "입력한 연구 아이디어와 실험 기록이 PaperOrchestra의 외부 AI API로 전송됩니다.\n"
            "API 사용 비용이 발생할 수 있습니다. 계속하시겠습니까?",
            parent=self,
        ):
            return
        try:
            options = RunOptions(
                engine_directory=Path(self.engine_var.get()),
                workspace_directory=Path(self.workspace_var.get()),
                project=self._active_project,
                language=self.language_var.get(),
                template=self.template_var.get(),
                model=self.model_var.get().strip(),
                plotting=self.plotting_var.get(),
            )
            prepared = prepare_run(options, *self._contents())
        except (OSError, ValueError) as exc:
            messagebox.showerror("실행 준비 실패", str(exc), parent=self)
            return
        self._current_result = prepared.result_directory
        self.folder_button.configure(state="normal")
        self._append_log("[시작] " + PROJECTS[options.project] + " / " + LANGUAGES[options.language])
        self._append_log("[출력] " + str(prepared.result_directory))
        self.status_var.set("논문 생성 중입니다. 프로그램을 닫으면 작업이 중단됩니다.")
        self._cancel_requested.clear()
        self._set_running(True)
        threading.Thread(target=self._worker, args=(prepared,), daemon=True).start()
        self.after(150, self._poll_events)

    def _worker(self, prepared) -> None:
        try:
            flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            process = subprocess.Popen(
                prepared.command, cwd=prepared.work_directory, env=prepared.environment,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace", bufsize=1,
                creationflags=flags, shell=False,
            )
            self._process = process
            if self._cancel_requested.is_set() and process.poll() is None:
                process.terminate()
            assert process.stdout is not None
            for line in process.stdout:
                self._events.put(("log", line))
            return_code = process.wait()
            complete = (not self._cancel_requested.is_set() and return_code == 0
                        and (prepared.result_directory / "final_paper.pdf").is_file())
            self._events.put(("done", (complete, return_code)))
        except Exception as exc:
            self._events.put(("error", str(exc)))
        finally:
            self._process = None

    def _poll_events(self) -> None:
        if not self.winfo_exists():
            return
        try:
            while True:
                kind, payload = self._events.get_nowait()
                if kind == "log":
                    self._append_log(str(payload).rstrip("\n"))
                elif kind == "done":
                    complete, code = payload
                    self._set_running(False)
                    if complete:
                        self.status_var.set("논문 PDF 생성이 완료됐습니다. 수치·인용·도표를 반드시 검증하세요.")
                    else:
                        self.status_var.set("논문 생성이 완료되지 않았습니다. 위 실행 기록을 확인하세요.")
                        self._append_log(f"[실패] 종료 코드 {code}, 최종 PDF 확인 필요")
                elif kind == "error":
                    self._set_running(False)
                    self.status_var.set("실행 중 오류가 발생했습니다.")
                    self._append_log("[오류] " + str(payload))
        except queue.Empty:
            pass
        if self._running:
            self.after(150, self._poll_events)

    def _cancel(self) -> None:
        if self._running:
            self._cancel_requested.set()
        if self._running and self._process and self._process.poll() is None:
            try:
                self._process.terminate()
                self._append_log("[중단 요청] 실행 중인 PaperOrchestra 작업을 종료합니다.")
            except OSError as exc:
                self._append_log("[중단 오류] " + str(exc))

    def _open_output(self) -> None:
        if self._current_result is None:
            return
        path = self._current_result.parent
        try:
            if os.name == "nt":
                os.startfile(str(path))  # type: ignore[attr-defined]
            else:
                subprocess.Popen(["xdg-open", str(path)])
        except OSError as exc:
            messagebox.showerror("폴더 열기", str(exc), parent=self)

    def _on_close(self) -> None:
        if self._running:
            if not messagebox.askyesno("작업 종료", "AI 논문 생성을 중단하고 창을 닫을까요?", parent=self):
                return
            self._cancel()
        self.destroy()

# -*- coding: utf-8 -*-
"""
논문 작성 보조 도구 (오프라인)
- .docx 파일 불러오기 / 저장
- 통계: 글자수, 단어수, 문장수, 문단수, 평균 문장 길이
- 문장 검사: 과도하게 긴 문장, 감탄/의문문, 조사 중복, 어미 반복
- 문체 검사: 구어체 종결어미, 문두 접속어, 1인칭, 수식어 남용
- 반복 어휘: 단어 빈도 분석
실행: python paper_assistant.py
"""
import re
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from paper_assistant.analysis import analyze_text
from paper_assistant.documents import export_plain_docx, load_document
from paper_assistant.reports import save_report

try:
    from docx import Document
except ImportError:
    Document = None

SENT_SPLIT = re.compile(r"[^.!?\n]+(?:[.!?]+|$)")
TOKEN_RE = re.compile(r"[가-힣a-zA-Z0-9]+")
REPEAT_TOKEN_RE = re.compile(r"\b([가-힣]+)\s+\1\b")

COLLOQUIAL_ENDINGS = re.compile(
    r"(해요|했어요|이에요|예요|이예요|죠|네요|거든요|잖아요|군요|구나|어라|지요)\s*[.!?]?$"
)
SENT_OPENERS = ("그래서", "근데", "그리고", "하지만", "그런데", "그러면", "또")
INTENSIFIERS = ("매우", "정말", "아주", "굉장히", "엄청", "되게", "진짜", "너무")
FIRST_PERSON = ("내가", "저는", "우리는", "우리가")
PARTICLES = ("은", "는", "이", "가", "을", "를", "의", "에", "에서", "로", "으로", "와", "과", "도", "만")

ISSUE_SENT = "문장"
ISSUE_STYLE = "문체"
ISSUE_REPEAT = "반복"


def split_sentences(text):
    """(문장, 시작오프셋, 끝오프셋) 리스트 반환."""
    out = []
    for m in SENT_SPLIT.finditer(text):
        s = m.group(0)
        if s.strip():
            start = m.start() + (len(s) - len(s.lstrip()))
            out.append((s.strip(), start, m.end()))
    return out


def analyze(text, long_sent_limit=100, repeat_ratio=0.02, repeat_min=4):
    issues = []  # (kind, msg, start, end)
    sentences = split_sentences(text)
    ending_streak = []  # 어미 반복 추적

    for sent, start, end in sentences:
        if len(sent) >= long_sent_limit:
            issues.append((ISSUE_SENT, f"문장이 깁니다 ({len(sent)}자): {sent[:30]}…", start, end))
        if sent.rstrip().endswith(("!", "?")):
            issues.append((ISSUE_SENT, f"감탄/의문문: {sent[:30]}…", start, end))
        m = COLLOQUIAL_ENDINGS.search(sent)
        if m:
            issues.append((ISSUE_STYLE, f"구어체 어미 '~{m.group(1)}': {sent[:30]}…", start, end))
        first = sent.split()[0] if sent.split() else ""
        if first.rstrip(",") in SENT_OPENERS:
            issues.append((ISSUE_STYLE, f"문두 접속어 '{first.rstrip(',')}': {sent[:30]}…", start, end))
        for w in FIRST_PERSON:
            if w in sent:
                issues.append((ISSUE_STYLE, f"1인칭 '{w}' — '본 연구에서는' 등 권장: {sent[:30]}…", start, end))
                break
        for w in INTENSIFIERS:
            if w in sent:
                issues.append((ISSUE_STYLE, f"수식어 '{w}' — 정량적 표현 권장: {sent[:30]}…", start, end))
                break
        for m2 in REPEAT_TOKEN_RE.finditer(sent):
            if m2.group(1) in PARTICLES or len(m2.group(1)) >= 2:
                issues.append((ISSUE_REPEAT, f"같은 단어 연속 '{m2.group(1)} {m2.group(1)}'", start + m2.start(), start + m2.end()))

        # 종결어미 추적 (~다. 로 끝나는 명사형 패턴의 꼬리)
        tail = re.search(r"([가-힣]{1,4})[.!?]?$", sent)
        tail = tail.group(1) if tail else ""
        if ending_streak and ending_streak[-1][0] == tail and tail:
            ending_streak.append((tail, start, end))
            if len(ending_streak) >= 3:
                issues.append((ISSUE_STYLE, f"'~{tail}' 어미가 {len(ending_streak)}문장 연속 반복", start, end))
        else:
            ending_streak = [(tail, start, end)]

    # 단어 빈도
    words = [w.lower() for w in TOKEN_RE.findall(text) if len(w) >= 2 and w not in PARTICLES]
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    total = len(words) or 1
    overused = sorted(
        ((w, c) for w, c in freq.items() if c >= repeat_min and c / total >= repeat_ratio),
        key=lambda x: -x[1],
    )
    for w, c in overused:
        issues.append((ISSUE_REPEAT, f"단어 '{w}' {c}회 사용 ({c / total:.1%}) — 과다 반복 가능", 0, 0))

    stats = {
        "글자수(공백포함)": len(text),
        "글자수(공백제외)": len(re.sub(r"\s", "", text)),
        "단어수": len(text.split()),
        "문장수": len(sentences),
        "문단수": len([p for p in text.split("\n") if p.strip()]),
        "평균 문장길이": round(sum(len(s) for s, _, _ in sentences) / max(len(sentences), 1), 1),
    }
    top_words = sorted(freq.items(), key=lambda x: -x[1])[:20]
    return issues, stats, top_words


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Paper Assistant · 논문 작성 보조")
        self.geometry("1200x760")
        self.minsize(900, 580)
        self.configure(bg="#f2f6fa")
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#f2f6fa")
        style.configure("TLabel", background="#f2f6fa", foreground="#183954")
        style.configure("TButton", padding=(10, 7))
        style.configure("TNotebook.Tab", padding=(12, 8))
        style.configure("Treeview", rowheight=31)
        self.issues = []
        self.source_path = None
        self.analysis_result = None
        self.orchestra_window = None
        self._build_ui()

    def _build_ui(self):
        title = ttk.Frame(self)
        title.pack(fill="x", padx=18, pady=(16, 9))
        ttk.Label(title, text="Paper Assistant", font=("맑은 고딕", 19, "bold")).pack(anchor="w")
        ttk.Label(title, text="오프라인 논문 작성 보조 · DOCX 원본 파일을 변경하지 않습니다.").pack(anchor="w")

        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=18, pady=7)
        ttk.Button(bar, text="문서 열기", command=self.open_docx).pack(side="left")
        ttk.Button(bar, text="새 DOCX 초안", command=self.save_docx).pack(side="left", padx=4)
        ttk.Button(bar, text="검사 보고서", command=self.export_report).pack(side="left", padx=4)
        ttk.Button(bar, text="분석 실행", command=self.run_analysis).pack(side="left", padx=4)
        ttk.Button(bar, text="AI 논문 작성", command=self.open_orchestra).pack(side="left", padx=4)
        ttk.Button(bar, text="전체 복사", command=self.copy_all).pack(side="left", padx=4)
        ttk.Label(bar, text="긴 문장 기준:").pack(side="left", padx=(16, 2))
        self.limit_var = tk.IntVar(value=100)
        ttk.Spinbox(bar, from_=40, to=300, width=5, textvariable=self.limit_var).pack(side="left")
        ttk.Label(bar, text="자").pack(side="left")
        self.realtime_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(bar, text="실시간 분석", variable=self.realtime_var).pack(side="left", padx=(16, 0))
        self.academic_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(bar, text="학술 표기 검사(실험적)", variable=self.academic_var).pack(side="left", padx=10)

        paned = ttk.PanedWindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=18, pady=8)

        left = ttk.Frame(paned)
        self.editor = tk.Text(left, wrap="word", font=("맑은 고딕", 11), undo=True,
                              background="white", foreground="#183954", padx=14, pady=14,
                              relief="flat", spacing1=4, spacing3=5)
        scroll = ttk.Scrollbar(left, command=self.editor.yview)
        self.editor.configure(yscrollcommand=scroll.set)
        self.editor.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        for name, color in {"문장": "#fbe4a5", "문체": "#bde2f5", "반복": "#d9d0f2", "학술": "#cfeadd"}.items():
            self.editor.tag_configure(name, background=color)
        self.editor.bind("<KeyRelease>", self._on_key)
        self._pending = None
        paned.add(left, weight=3)

        right = ttk.Frame(paned)
        nb = ttk.Notebook(right)
        nb.pack(fill="both", expand=True)

        self.stats_text = tk.Text(nb, wrap="word", font=("맑은 고딕", 10), state="disabled")
        nb.add(self.stats_text, text="통계")

        self.issue_tree = ttk.Treeview(nb, columns=("kind", "msg"), show="headings")
        self.issue_tree.heading("kind", text="유형")
        self.issue_tree.heading("msg", text="내용")
        self.issue_tree.column("kind", width=50)
        self.issue_tree.column("msg", width=380)
        self.issue_tree.bind("<<TreeviewSelect>>", self.jump_to_issue)
        nb.add(self.issue_tree, text="검사 결과")

        self.words_text = tk.Text(nb, wrap="word", font=("맑은 고딕", 10), state="disabled")
        nb.add(self.words_text, text="단어 빈도")

        paned.add(right, weight=2)

        self.status = ttk.Label(self, text="원고를 불러오거나 텍스트를 입력하세요. 검사 결과는 참고용 제안입니다.")
        self.status.pack(fill="x", padx=18, pady=8)

    def open_docx(self):
        path = filedialog.askopenfilename(filetypes=[("문서", "*.docx *.txt *.md")])
        if not path:
            return
        try:
            loaded = load_document(path)
            self.editor.delete("1.0", "end")
            self.editor.insert("1.0", loaded.text)
            self.source_path = loaded.path
            self.status.config(text=f"{loaded.path.name} · {loaded.notice}")
            self.run_analysis()
        except Exception as exc:
            messagebox.showerror("문서 열기 실패", str(exc))

    def open_orchestra(self):
        if self.orchestra_window is not None and self.orchestra_window.winfo_exists():
            self.orchestra_window.lift()
            self.orchestra_window.focus_force()
            return
        from paper_assistant.orchestra_ui import PaperOrchestraWindow

        self.orchestra_window = PaperOrchestraWindow(self)

    def save_docx(self):
        path = filedialog.asksaveasfilename(defaultextension=".docx", filetypes=[("Word 문서", "*.docx")],
                                            title="원본과 다른 새 파일 이름으로 저장")
        if not path:
            return
        if not messagebox.askyesno("새 DOCX 초안", "텍스트만 새 문서에 저장합니다. 원본의 서식·이미지·표는 복제하지 않습니다. 계속할까요?"):
            return
        try:
            saved = export_plain_docx(self.editor.get("1.0", "end-1c"), path, original=self.source_path)
            self.status.config(text=f"새 초안 저장: {saved.name} · 원본 변경 없음")
        except Exception as exc:
            messagebox.showerror("저장 실패", str(exc))

    def export_report(self):
        self.run_analysis()
        if self.analysis_result is None:
            return
        path = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[
            ("HTML 보고서", "*.html"), ("Markdown 보고서", "*.md")])
        if not path:
            return
        try:
            saved = save_report(path, self.editor.get("1.0", "end-1c"), self.analysis_result,
                                original=self.source_path)
            self.status.config(text=f"검사 보고서 저장: {saved.name}")
        except Exception as exc:
            messagebox.showerror("보고서 저장 실패", str(exc))

    def copy_all(self):
        self.clipboard_clear()
        self.clipboard_append(self.editor.get("1.0", "end-1c"))
        self.status.config(text="전체 텍스트를 클립보드에 복사했습니다.")

    def _on_key(self, _event):
        if not self.realtime_var.get():
            return
        if self._pending:
            self.after_cancel(self._pending)
        self._pending = self.after(650, self.run_analysis)

    def run_analysis(self):
        self._pending = None
        text = self.editor.get("1.0", "end-1c")
        if not text.strip():
            self.analysis_result = None
            self.issues = []
            for row in self.issue_tree.get_children():
                self.issue_tree.delete(row)
            for category in ("문장", "문체", "반복", "학술"):
                self.editor.tag_remove(category, "1.0", "end")
            self.status.config(text="분석할 텍스트가 없습니다.")
            return
        try:
            self.analysis_result = analyze_text(text, long_sentence_limit=self.limit_var.get(),
                                                academic_checks=self.academic_var.get())
        except (ValueError, tk.TclError) as exc:
            self.status.config(text=f"설정을 확인하세요: {exc}")
            return
        result = self.analysis_result
        self.issues = [(issue.category, issue.message, issue.start, issue.end) for issue in result.issues]
        stats, top_words = result.stats, result.top_words

        for category in ("문장", "문체", "반복", "학술"):
            self.editor.tag_remove(category, "1.0", "end")
        for row in self.issue_tree.get_children():
            self.issue_tree.delete(row)
        for i, (kind, msg, s, e) in enumerate(self.issues):
            self.issue_tree.insert("", "end", iid=str(i), values=(kind, msg))
            if e > s:
                self.editor.tag_add(kind, f"1.0+{s}c", f"1.0+{e}c")

        self.stats_text.config(state="normal")
        self.stats_text.delete("1.0", "end")
        self.stats_text.insert("end", "\n".join(f"{k}: {v}" for k, v in stats.items()))
        self.stats_text.insert("end", f"\n\n검출된 이슈: {len(self.issues)}건")
        self.stats_text.config(state="disabled")

        self.words_text.config(state="normal")
        self.words_text.delete("1.0", "end")
        self.words_text.insert("end", "단어 빈도 TOP 20\n\n" + "\n".join(f"{w}: {c}회" for w, c in top_words))
        self.words_text.config(state="disabled")

        self.status.config(
            text=f"글자 {stats['글자 수(공백 제외)']:,}자 | 단어 {stats['단어 수(공백 기준)']:,}개 | 문장 {stats['문장 수']}개 | 검토 후보 {len(self.issues)}건"
        )

    def jump_to_issue(self, _event):
        sel = self.issue_tree.selection()
        if not sel:
            return
        _, _, s, e = self.issues[int(sel[0])]
        if e <= s:
            return
        self.editor.see(f"1.0+{s}c")
        self.editor.tag_remove("sel", "1.0", "end")
        self.editor.tag_add("sel", f"1.0+{s}c", f"1.0+{e}c")
        self.editor.focus_set()


if __name__ == "__main__":
    App().mainloop()

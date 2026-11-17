"""Offline tests for the optional AI integration (no API keys or network)."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from paper_assistant.orchestra import (
    INITIAL_LOG,
    RunOptions,
    prepare_run,
    project_files,
    read_project,
    save_project,
)


class PaperOrchestraIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.root = Path(self.tempdir.name)
        self.engine = self.root / "paper-orchestra"
        self.workspace = self.root / "workspace"
        template = self.engine / "templates" / "cvpr2025"
        template.mkdir(parents=True)
        (template / "template.tex").write_text(
            "\\documentclass{article}\n\\begin{document}\n"
            "\\section{Introduction}\n\\section{Conclusion}\n\\end{document}\n",
            encoding="utf-8",
        )
        (template / "guidelines.md").write_text("Conference guidelines\n", encoding="utf-8")
        # A tiny local fake verifies command wiring without running costly models.
        (self.engine / "paper_writing_cli.py").write_text(
            "import argparse\nfrom pathlib import Path\n"
            "p=argparse.ArgumentParser()\n"
            "p.add_argument('--raw_materials_dir')\n"
            "p.add_argument('--latex_template_dir')\n"
            "p.add_argument('--output_dir')\n"
            "p.add_argument('--writer_model_name')\n"
            "p.add_argument('--reflection_model_name')\n"
            "p.add_argument('--use_plotting')\n"
            "a=p.parse_args()\n"
            "assert (Path(a.raw_materials_dir)/'idea_sparse.md').exists()\n"
            "Path(a.output_dir).mkdir(parents=True, exist_ok=True)\n"
            "(Path(a.output_dir)/'final_paper.pdf').write_bytes(b'%PDF-test')\n",
            encoding="utf-8",
        )

    def options(self, language="ko"):
        return RunOptions(
            engine_directory=self.engine,
            workspace_directory=self.workspace,
            project="semg",
            language=language,
            template="cvpr2025",
            plotting=False,
        )

    def test_korean_mode_patches_only_staged_template(self):
        run = prepare_run(self.options(), "실험 질문", "MAE: 실험 전")
        directory = run.result_directory.parent
        tex = (directory / "template" / "template.tex").read_text(encoding="utf-8")
        self.assertIn("\\usepackage{kotex}", tex)
        self.assertIn("\\section{서론}", tex)
        self.assertIn("\\section{결론}", tex)
        self.assertNotIn("kotex", (self.engine / "templates" / "cvpr2025" / "template.tex").read_text())
        idea = (directory / "raw_materials" / "idea_sparse.md").read_text(encoding="utf-8")
        self.assertIn("Korean", idea)
        self.assertIn("실험 질문", idea)
        self.assertEqual((directory / "raw_materials" / "experimental_log.md").read_text(encoding="utf-8"), "MAE: 실험 전")
        self.assertEqual(run.environment["PYTHONUTF8"], "1")
        self.assertIn("orchestra_bootstrap.py", run.command[1])
        self.assertNotIn("API_KEY", " ".join(run.command))

    def test_english_mode_runs_external_cli_without_modifying_source(self):
        run = prepare_run(self.options("en"), "Idea", "Measured score 1.23")
        outcome = subprocess.run(run.command, cwd=run.work_directory, env=run.environment, capture_output=True)
        self.assertEqual(outcome.returncode, 0, outcome.stderr.decode(errors="replace"))
        self.assertTrue((run.result_directory / "final_paper.pdf").is_file())
        self.assertEqual(Path(run.command[1]).name, "paper_writing_cli.py")

    def test_project_notes_stay_separate_and_have_recoverable_backups(self):
        save_project(self.workspace, "semg", "실험 1", "수치 1")
        save_project(self.workspace, "ramflow", "실험 2", "수치 2")
        save_project(self.workspace, "semg", "실험 1 수정", "수치 1")
        self.assertEqual(read_project(self.workspace, "semg"), ("실험 1 수정", "수치 1"))
        self.assertEqual(read_project(self.workspace, "ramflow"), ("실험 2", "수치 2"))
        idea_path, _ = project_files(self.workspace, "semg")
        backups = list(idea_path.parent.glob("idea_sparse.md.*.bak"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(encoding="utf-8"), "실험 1")

    def test_existing_figures_are_copied_to_the_run(self):
        figures = project_files(self.workspace, "semg")[0].parent / "figures"
        figures.mkdir(parents=True)
        (figures / "real_measurement.png").write_bytes(b"plot")
        (figures / "ignore.exe").write_bytes(b"code")
        run = prepare_run(self.options("en"), "Idea", "Log")
        staged = run.result_directory.parent / "raw_materials" / "figures"
        self.assertEqual((staged / "real_measurement.png").read_bytes(), b"plot")
        self.assertFalse((staged / "ignore.exe").exists())

    def test_rejects_missing_engine_before_writing_outputs(self):
        (self.engine / "paper_writing_cli.py").unlink()
        with self.assertRaises(FileNotFoundError):
            prepare_run(self.options(), "Idea", "Log")
        self.assertFalse(self.workspace.exists())

    def test_rejects_untouched_experiment_placeholder(self):
        with self.assertRaisesRegex(ValueError, "기본 안내문"):
            prepare_run(self.options(), "Research idea", INITIAL_LOG)
        self.assertFalse(self.workspace.exists())


if __name__ == "__main__":
    unittest.main()

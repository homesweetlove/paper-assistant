from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from docx import Document

from paper_assistant.analysis import analyze_text
from paper_assistant.documents import export_plain_docx, load_document
from paper_assistant.reports import report_html, save_report


class DocumentTests(unittest.TestCase):
    def test_docx_read_keeps_original_unchanged_and_reads_tables(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "original.docx"
            doc = Document()
            doc.add_paragraph("연구 첫 문단")
            table = doc.add_table(rows=1, cols=2)
            table.cell(0, 0).text = "각도"
            table.cell(0, 1).text = "MAE"
            doc.add_paragraph("연구 마지막 문단")
            doc.save(path)
            original_bytes = path.read_bytes()
            loaded = load_document(path)
            self.assertIn("각도 | MAE", loaded.text)
            self.assertLess(loaded.text.index("각도 | MAE"), loaded.text.index("연구 마지막"))
            self.assertEqual(original_bytes, path.read_bytes())

    def test_export_does_not_overwrite_original_or_existing_file(self):
        with TemporaryDirectory() as folder:
            original = Path(folder) / "original.docx"
            original.write_bytes(b"user document")
            with self.assertRaises(ValueError):
                export_plain_docx("test", original, original=original)
            output = Path(folder) / "new.docx"
            # Windows temp paths can be represented with either long or 8.3 names.
            # Verify that the returned path points to the actual output file.
            self.assertTrue(export_plain_docx("첫 문단\n둘째 문단", output, original=original).samefile(output))
            self.assertEqual(len(Document(output).paragraphs), 2)
            with self.assertRaises(FileExistsError):
                export_plain_docx("overwrite", output)
            self.assertEqual(original.read_bytes(), b"user document")

    def test_report_escapes_untrusted_manuscript_and_does_not_overwrite(self):
        text = "<script>alert(1)</script> 아주 긴 말"
        result = analyze_text(text, long_sentence_limit=20)
        html = report_html(text, result)
        self.assertNotIn("<script>", html)
        self.assertIn("&lt;script&gt;", html)
        with TemporaryDirectory() as folder:
            output = Path(folder) / "report.html"
            save_report(output, text, result)
            self.assertIn("Paper Assistant", output.read_text(encoding="utf-8"))
            with self.assertRaises(FileExistsError):
                save_report(output, text, result)


class MacroSafetyTests(unittest.TestCase):
    def test_word_macros_do_not_erase_highlighting_or_start_automatically(self):
        root = Path(__file__).resolve().parents[1]
        for name in ("PaperAssist.bas", "PaperAssist_ko.bas"):
            content = (root / name).read_bytes().decode("cp949") if name.endswith("_ko.bas") else (root / name).read_text(encoding="utf-8")
            self.assertNotIn("HighlightColorIndex", content)
            self.assertNotIn("Sub AutoExec", content)
            self.assertNotIn("Application.OnTime", content)
            self.assertIn("COMMENT_PREFIX", content)


if __name__ == "__main__":
    unittest.main()

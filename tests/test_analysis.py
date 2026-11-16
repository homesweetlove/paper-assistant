import unittest

from paper_assistant.analysis import analyze_text, split_sentences


class SentenceTests(unittest.TestCase):
    def test_multiline_without_punctuation_is_not_discarded(self):
        text = "첫 번째 문장\n두 번째 문장\n\n세 번째 문장."
        sentences = split_sentences(text)
        self.assertEqual([row[0] for row in sentences], ["첫 번째 문장", "두 번째 문장", "세 번째 문장."])
        for sentence, start, end in sentences:
            self.assertEqual(text[start:end], sentence)

    def test_decimals_are_not_separate_sentences(self):
        self.assertEqual(len(split_sentences("평균은 4.45도이다. 결과를 확인했다.")), 2)

    def test_colloquial_offset_is_exact(self):
        text = "  연구를 했어요."
        result = analyze_text(text)
        issue = next(i for i in result.issues if i.rule == "colloquial")
        self.assertEqual(text[issue.start:issue.end], "했어요")

    def test_empty_text_has_zero_counts(self):
        result = analyze_text("")
        self.assertEqual(result.stats["문장 수"], 0)
        self.assertEqual(result.stats["문단 수"], 0)

    def test_repeated_word_has_real_offset(self):
        text = "로봇 제어와 로봇 제어, 로봇 연구 그리고 로봇 제어"
        result = analyze_text(text, repeat_minimum=4, repeat_ratio=0.2)
        issue = next(i for i in result.issues if i.rule == "word_frequency" and "로봇" in i.message)
        self.assertEqual(text[issue.start:issue.end], "로봇")

    def test_academic_checks_are_opt_in(self):
        text = "EMG 신호를 측정했다. EMG 지연은 10 msec이다."
        self.assertFalse(any(i.category == "학술" for i in analyze_text(text).issues))
        result = analyze_text(text, academic_checks=True)
        self.assertTrue(any(i.rule == "unit_style" for i in result.issues))
        self.assertTrue(any(i.rule == "acronym_definition" for i in result.issues))

    def test_invalid_threshold_raises(self):
        with self.assertRaises(ValueError):
            analyze_text("검사할 문장", long_sentence_limit=0)

    def test_caption_without_body_reference_is_flagged_only_in_academic_mode(self):
        text = "그림 1 실험 구성\n측정값을 비교했다."
        self.assertFalse(any(i.rule == "caption_reference" for i in analyze_text(text).issues))
        result = analyze_text(text, academic_checks=True)
        self.assertTrue(any(i.rule == "caption_reference" for i in result.issues))


if __name__ == "__main__":
    unittest.main()

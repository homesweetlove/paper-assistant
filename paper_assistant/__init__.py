"""Offline Korean academic-writing checks for Paper Assistant."""

from .analysis import AnalysisResult, Issue, analyze_text, split_sentences

__all__ = ["AnalysisResult", "Issue", "analyze_text", "split_sentences"]

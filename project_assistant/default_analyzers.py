from __future__ import annotations

from project_assistant.analyzer_registry import (
    AnalyzerRegistry,
)


def build_default_analyzer_registry() -> AnalyzerRegistry:
    return AnalyzerRegistry()

from __future__ import annotations

from project_assistant.analyzer_registry import (
    AnalysisContext,
    AnalyzerRegistry,
    RegisteredAnalyzer,
)
from project_assistant.analyzers import (
    ApiAnalyzer,
    ArchitectureAnalyzer,
    CliAnalyzer,
    ConfigurationAnalyzer,
    DeploymentAnalyzer,
    PyprojectAnalyzer,
    PyprojectFacts,
    ReadmeAnalyzer,
    SecurityAnalyzer,
    SpecificationAnalyzer,
)


def _analyze_pyproject(
    context: AnalysisContext,
) -> PyprojectFacts:
    return PyprojectAnalyzer().analyze(
        context.project
    )


def _analyze_configuration(
    context: AnalysisContext,
):
    return ConfigurationAnalyzer().analyze(
        context.project
    )


def _analyze_cli(
    context: AnalysisContext,
):
    pyproject = context.require_as(
        "pyproject",
        PyprojectFacts,
    )

    return CliAnalyzer().analyze(
        context.project,
        entry_points=pyproject.scripts,
    )


def _analyze_architecture(
    context: AnalysisContext,
):
    return ArchitectureAnalyzer().analyze(
        context.project
    )


def _analyze_deployment(
    context: AnalysisContext,
):
    return DeploymentAnalyzer().analyze(
        context.project
    )


def _analyze_api(
    context: AnalysisContext,
):
    return ApiAnalyzer().analyze(
        context.project
    )


def _analyze_specification(
    context: AnalysisContext,
):
    return SpecificationAnalyzer().analyze(
        context.project
    )


def _analyze_readme(
    context: AnalysisContext,
):
    return ReadmeAnalyzer().analyze(
        context.project
    )


def _analyze_security(
    context: AnalysisContext,
):
    return SecurityAnalyzer().analyze(
        context.project,
        protected_documents=(
            context.protected_documents
        ),
    )


def build_default_analyzer_registry() -> AnalyzerRegistry:
    registry = AnalyzerRegistry()

    registry.register(
        RegisteredAnalyzer(
            name="pyproject",
            analyze=_analyze_pyproject,
        )
    )

    registry.register(
        RegisteredAnalyzer(
            name="configuration",
            analyze=_analyze_configuration,
        )
    )

    registry.register(
        RegisteredAnalyzer(
            name="cli",
            analyze=_analyze_cli,
            profiles=frozenset(
                {
                    "python-cli",
                }
            ),
            dependencies=(
                "pyproject",
            ),
        )
    )

    registry.register(
        RegisteredAnalyzer(
            name="architecture",
            analyze=_analyze_architecture,
        )
    )

    registry.register(
        RegisteredAnalyzer(
            name="deployment",
            analyze=_analyze_deployment,
        )
    )

    registry.register(
        RegisteredAnalyzer(
            name="api",
            analyze=_analyze_api,
        )
    )

    registry.register(
        RegisteredAnalyzer(
            name="specification",
            analyze=_analyze_specification,
        )
    )

    registry.register(
        RegisteredAnalyzer(
            name="readme",
            analyze=_analyze_readme,
        )
    )

    registry.register(
        RegisteredAnalyzer(
            name="security",
            analyze=_analyze_security,
        )
    )

    return registry

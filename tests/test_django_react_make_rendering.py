from pathlib import Path
from types import SimpleNamespace

from docforge.manual_deterministic import ManualDeterministicContentBuilder
from docforge.analyzers.django_react_application import DjangoReactApplicationAnalyzer
from docforge.manual_django_react import DjangoReactManualKnowledgeBuilder
from docforge.manual_knowledge import ManualFactSource, ManualInstallation, ManualKnowledge, ManualProject


def _command(name: str, parameters: list[str]):
    return SimpleNamespace(name=name, invocation=f"make {name}", parameters=[SimpleNamespace(name=item) for item in parameters])


def test_make_syntax_only_uses_parameters_declared_for_the_target() -> None:
    builder = ManualDeterministicContentBuilder()
    assert builder._make_syntax(_command("logs", []), ["backend"]) == ["make logs"]
    assert builder._make_syntax(_command("rebuild", []), ["backend"]) == ["make rebuild"]
    assert builder._make_syntax(_command("logs", ["SERVICE"]), ["backend"]) == ["make logs SERVICE=backend"]
    assert builder._make_syntax(_command("restore", ["FILE"]), []) == ["make restore", "make restore FILE=chemin/vers/sauvegarde.sql.gz"]
    assert builder._make_syntax(_command("restore", []), []) == ["make restore"]


def test_migration_effect_requires_a_precaution() -> None:
    assert ManualDeterministicContentBuilder._precaution(["Application des migrations de base de données"])
    assert ManualDeterministicContentBuilder._precaution([]) is None


def test_manual_knowledge_paths_are_portable_for_distinct_roots(tmp_path: Path) -> None:
    manual = ManualKnowledge(
        schema_version=3,
        project=ManualProject("test", None, None, "django-react", None, None, ManualFactSource("detected", (str(tmp_path),))),
        profile={"evidence": [str(tmp_path / "backend" / "urls.py")]},
        installation=ManualInstallation("test"),
        application={"source_paths": [str(tmp_path / "frontend" / "src" / "App.jsx")]},
        operational_commands={"commands": [{"body": [str(tmp_path / "scripts" / "run.sh"), "/opt/apps/nonportable"]}]},
    )
    normalized = DjangoReactManualKnowledgeBuilder._normalize_manual_paths(manual, tmp_path)
    serialized = normalized.to_json()
    assert str(tmp_path) not in serialized
    assert "/opt/apps/" not in serialized
    assert "frontend/src/App.jsx" in serialized
    assert "[chemin externe non résolu]" in serialized


def test_effect_taxonomy_keeps_test_cleanup_secondary() -> None:
    command = SimpleNamespace(
        body=["docker compose run --rm backend python manage.py test"],
        category="tests",
        name="test-backend",
        manifest_destructive_effects=[],
    )
    assert DjangoReactManualKnowledgeBuilder._command_destructive_effects(command) == []
    assert ManualDeterministicContentBuilder._precaution(["Création d’un artefact de sauvegarde de base de données"]) is None
    assert "schéma" in ManualDeterministicContentBuilder._precaution(["Migration ou modification du schéma ou de l’état de la base de données"])
    assert "écraser" in ManualDeterministicContentBuilder._precaution(["Modification ou écrasement potentiel des données PostgreSQL"])

def test_public_test_aggregator_is_documentable_from_dependencies() -> None:
    analyzer = DjangoReactApplicationAnalyzer()
    result = analyzer._classify_make_target(target="test", prerequisites=["test-backend", "test-frontend"], body=[], help_text="Lance les tests", visibility="public", template_manifest={"targets": {}}, local_origin_manifest=None, application_declarations={})
    assert result[:2] == ("developer-public", "developer-reference")

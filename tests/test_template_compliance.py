from pathlib import Path

from docforge.analyzers import (
    TemplateAnalyzer,
    TemplateComplianceAnalyzer,
)


def _write_template(root: Path) -> None:
    for path in (
        "README.md",
        "README_DEV.md",
        "CODEX_START.md",
        "AGENTS.md",
        "INVARIANTS.md",
        "docs/specification.md",
    ):
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("# Document\n", encoding="utf-8")

    (root / ".env.template.example").write_text(
        "APP_NAME=\n",
        encoding="utf-8",
    )

    scripts = root / "scripts"
    scripts.mkdir()

    for name in (
        "backup-db.sh",
        "check-invariants.sh",
        "down.sh",
        "env-switch.sh",
        "generate-env.sh",
        "generate-secrets.sh",
        "init.sh",
        "logs.sh",
        "migrate.sh",
        "ps.sh",
        "rebuild.sh",
        "restart.sh",
        "restore-db.sh",
        "up.sh",
        "update.sh",
    ):
        (scripts / name).write_text(
            "#!/bin/sh\n",
            encoding="utf-8",
        )

    (root / "backend").mkdir()
    (root / "backend" / "manage.py").write_text(
        "",
        encoding="utf-8",
    )
    (root / "backend" / "requirements.txt").write_text(
        "Django\npsycopg2-binary\n",
        encoding="utf-8",
    )

    (root / "frontend").mkdir()
    (root / "frontend" / "package.json").write_text(
        """
{
  "dependencies": {"react": "^18"},
  "devDependencies": {"vite": "^5"}
}
""",
        encoding="utf-8",
    )

    compose = """
services:
  db:
    image: postgres:16
  backend:
    build: ./backend
    depends_on: [db]
  frontend:
    build: ./frontend
    depends_on: [backend]
networks:
  edge:
    external: true
"""

    (root / "docker-compose.dev.yml").write_text(
        compose,
        encoding="utf-8",
    )
    (root / "docker-compose.prod.yml").write_text(
        compose,
        encoding="utf-8",
    )

    (root / "Makefile").write_text(
        """
backup:
check:
dev:
down:
help:
init:
logs:
migrate:
prod:
ps:
rebuild:
restart:
restore:
up:
update:
""",
        encoding="utf-8",
    )


def test_compliance_detects_missing_canonical_files(
    tmp_path: Path,
) -> None:
    template_root = tmp_path / "template"
    template_root.mkdir()
    _write_template(template_root)

    app_root = tmp_path / "app"
    app_root.mkdir()

    (app_root / "backend").mkdir()
    (app_root / "backend" / "manage.py").write_text(
        "",
        encoding="utf-8",
    )
    (app_root / "backend" / "requirements.txt").write_text(
        "Django\npsycopg2-binary\n",
        encoding="utf-8",
    )

    (app_root / "frontend").mkdir()
    (app_root / "frontend" / "package.json").write_text(
        """
{
  "dependencies": {"react": "^18"},
  "devDependencies": {"vite": "^5"}
}
""",
        encoding="utf-8",
    )

    for name in (
        "docker-compose.dev.yml",
        "docker-compose.prod.yml",
    ):
        (app_root / name).write_text(
            "services: {}\n",
            encoding="utf-8",
        )

    template = TemplateAnalyzer().analyze(template_root)

    report = TemplateComplianceAnalyzer().analyze(
        app_root,
        template,
    )

    assert report.eligible is True
    assert report.score < 100
    assert any(
        finding.code == "DOC001"
        for finding in report.findings
    )
    assert any(
        finding.code == "SCR001"
        for finding in report.findings
    )

def test_compliance_does_not_require_materialization_scripts_for_existing_apps(
    tmp_path: Path,
) -> None:
    template_root = tmp_path / "template"
    template_root.mkdir()
    _write_template(template_root)

    template_scripts = template_root / "scripts"
    for name in (
        "app_template_metadata.py",
        "docforge-project-metadata.py",
        "materialize-application.py",
    ):
        (template_scripts / name).write_text(
            "#!/usr/bin/env python3\n",
            encoding="utf-8",
        )

    app_root = tmp_path / "app"
    app_root.mkdir()

    for document in (
        "README.md",
        "README_DEV.md",
        "CODEX_START.md",
        "AGENTS.md",
        "INVARIANTS.md",
        "docs/specification.md",
    ):
        target = app_root / document
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("# Document\n", encoding="utf-8")

    scripts = app_root / "scripts"
    scripts.mkdir()
    for name in (
        "backup-db.sh",
        "check-invariants.sh",
        "down.sh",
        "env-switch.sh",
        "generate-env.sh",
        "generate-secrets.sh",
        "init.sh",
        "logs.sh",
        "migrate.sh",
        "ps.sh",
        "rebuild.sh",
        "restart.sh",
        "restore-db.sh",
        "up.sh",
        "update.sh",
    ):
        (scripts / name).write_text(
            "#!/bin/sh\n",
            encoding="utf-8",
        )

    backend = app_root / "backend"
    backend.mkdir()
    (backend / "manage.py").write_text("", encoding="utf-8")
    (backend / "requirements.txt").write_text(
        "Django\npsycopg2-binary\n",
        encoding="utf-8",
    )

    frontend = app_root / "frontend"
    frontend.mkdir()
    (frontend / "package.json").write_text(
        """
{
  "dependencies": {"react": "^18"},
  "devDependencies": {"vite": "^5"}
}
""",
        encoding="utf-8",
    )

    compose = """
services:
  db:
    image: postgres:16
  backend:
    build: ./backend
    depends_on: [db]
  frontend:
    build: ./frontend
    depends_on: [backend]
networks:
  edge:
    external: true
"""

    for name in (
        "docker-compose.dev.yml",
        "docker-compose.prod.yml",
    ):
        (app_root / name).write_text(
            compose,
            encoding="utf-8",
        )

    (app_root / "Makefile").write_text(
        """
backup:
check:
dev:
down:
help:
init:
logs:
migrate:
prod:
ps:
rebuild:
restart:
restore:
up:
update:
""",
        encoding="utf-8",
    )
    (app_root / ".env.dev").write_text("APP_ENV=dev\n", encoding="utf-8")
    (app_root / ".env.prod").write_text("APP_ENV=prod\n", encoding="utf-8")
    (app_root / ".env.local").write_text("SECRET=value\n", encoding="utf-8")
    (app_root / ".env").symlink_to(".env.dev")
    (app_root / ".env.template.example").write_text("APP_NAME=\n", encoding="utf-8")
    (app_root / ".gitignore").write_text(".env\n.env.local\n", encoding="utf-8")

    template = TemplateAnalyzer().analyze(template_root)

    report = TemplateComplianceAnalyzer().analyze(
        app_root,
        template,
    )

    materialization_paths = {
        "scripts/app_template_metadata.py",
        "scripts/docforge-project-metadata.py",
        "scripts/materialize-application.py",
    }

    assert report.eligible is True
    assert all(
        finding.path not in materialization_paths
        for finding in report.findings
        if finding.code == "SCR001"
    )


def test_compliance_requires_materialization_scripts_when_metadata_is_present(
    tmp_path: Path,
) -> None:
    template_root = tmp_path / "template"
    template_root.mkdir()
    _write_template(template_root)

    template_scripts = template_root / "scripts"
    for name in (
        "app_template_metadata.py",
        "docforge-project-metadata.py",
        "materialize-application.py",
    ):
        (template_scripts / name).write_text(
            "#!/usr/bin/env python3\n",
            encoding="utf-8",
        )

    app_root = tmp_path / "app"
    app_root.mkdir()

    for document in (
        "README.md",
        "README_DEV.md",
        "CODEX_START.md",
        "AGENTS.md",
        "INVARIANTS.md",
        "docs/specification.md",
    ):
        target = app_root / document
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("# Document\n", encoding="utf-8")

    scripts = app_root / "scripts"
    scripts.mkdir()
    for name in (
        "backup-db.sh",
        "check-invariants.sh",
        "down.sh",
        "env-switch.sh",
        "generate-env.sh",
        "generate-secrets.sh",
        "init.sh",
        "logs.sh",
        "migrate.sh",
        "ps.sh",
        "rebuild.sh",
        "restart.sh",
        "restore-db.sh",
        "up.sh",
        "update.sh",
    ):
        (scripts / name).write_text(
            "#!/bin/sh\n",
            encoding="utf-8",
        )

    (app_root / "docforge.project.json").write_text(
        "{}\n",
        encoding="utf-8",
    )

    backend = app_root / "backend"
    backend.mkdir()
    (backend / "manage.py").write_text("", encoding="utf-8")
    (backend / "requirements.txt").write_text(
        "Django\npsycopg2-binary\n",
        encoding="utf-8",
    )

    frontend = app_root / "frontend"
    frontend.mkdir()
    (frontend / "package.json").write_text(
        """
{
  "dependencies": {"react": "^18"},
  "devDependencies": {"vite": "^5"}
}
""",
        encoding="utf-8",
    )

    compose = """
services:
  db:
    image: postgres:16
  backend:
    build: ./backend
    depends_on: [db]
  frontend:
    build: ./frontend
    depends_on: [backend]
networks:
  edge:
    external: true
"""

    for name in (
        "docker-compose.dev.yml",
        "docker-compose.prod.yml",
    ):
        (app_root / name).write_text(
            compose,
            encoding="utf-8",
        )

    (app_root / "Makefile").write_text(
        """
backup:
check:
dev:
down:
help:
init:
logs:
migrate:
prod:
ps:
rebuild:
restart:
restore:
up:
update:
""",
        encoding="utf-8",
    )
    (app_root / ".env.dev").write_text("APP_ENV=dev\n", encoding="utf-8")
    (app_root / ".env.prod").write_text("APP_ENV=prod\n", encoding="utf-8")
    (app_root / ".env.local").write_text("SECRET=value\n", encoding="utf-8")
    (app_root / ".env").symlink_to(".env.dev")
    (app_root / ".env.template.example").write_text("APP_NAME=\n", encoding="utf-8")
    (app_root / ".gitignore").write_text(".env\n.env.local\n", encoding="utf-8")

    template = TemplateAnalyzer().analyze(template_root)

    report = TemplateComplianceAnalyzer().analyze(
        app_root,
        template,
    )

    materialization_paths = {
        "scripts/app_template_metadata.py",
        "scripts/docforge-project-metadata.py",
        "scripts/materialize-application.py",
    }

    assert materialization_paths.issubset(
        {
            finding.path
            for finding in report.findings
            if finding.code == "SCR001"
        }
    )



def test_non_django_project_is_ignored(
    tmp_path: Path,
) -> None:
    template_root = tmp_path / "template"
    template_root.mkdir()
    _write_template(template_root)

    project_root = tmp_path / "static-site"
    project_root.mkdir()
    (project_root / "README.md").write_text(
        "# Site\n",
        encoding="utf-8",
    )

    template = TemplateAnalyzer().analyze(template_root)

    report = TemplateComplianceAnalyzer().analyze(
        project_root,
        template,
    )

    assert report.eligible is False
    assert report.checks == []


def test_compliance_detects_local_secret_file_without_scanning_it(
    tmp_path: Path,
) -> None:
    template_root = tmp_path / "template"
    template_root.mkdir()
    _write_template(template_root)

    app_root = tmp_path / "app"
    app_root.mkdir()

    for document in (
        "README.md",
        "README_DEV.md",
        "CODEX_START.md",
        "AGENTS.md",
        "INVARIANTS.md",
        "docs/specification.md",
    ):
        target = app_root / document
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("# Document\n", encoding="utf-8")

    backend = app_root / "backend"
    backend.mkdir()
    (backend / "manage.py").write_text("", encoding="utf-8")
    (backend / "requirements.txt").write_text(
        "Django\npsycopg2-binary\n",
        encoding="utf-8",
    )

    frontend = app_root / "frontend"
    frontend.mkdir()
    (frontend / "package.json").write_text(
        """
{
  "dependencies": {"react": "^18"},
  "devDependencies": {"vite": "^5"}
}
""",
        encoding="utf-8",
    )

    compose = """
services:
  db:
    image: postgres:16
  backend:
    build: ./backend
  frontend:
    build: ./frontend
networks:
  edge:
    external: true
"""

    for filename in (
        "docker-compose.dev.yml",
        "docker-compose.prod.yml",
    ):
        (app_root / filename).write_text(
            compose,
            encoding="utf-8",
        )

    for filename in (
        ".env.dev",
        ".env.prod",
        ".env.local",
        ".env.template.example",
    ):
        (app_root / filename).write_text(
            "VALUE=test\n",
            encoding="utf-8",
        )

    (app_root / ".env").symlink_to(".env.dev")

    (app_root / ".gitignore").write_text(
        ".env\n.env.local\n",
        encoding="utf-8",
    )

    scripts = app_root / "scripts"
    scripts.mkdir()

    for script in (
        "backup-db.sh",
        "check-invariants.sh",
        "down.sh",
        "env-switch.sh",
        "generate-env.sh",
        "generate-secrets.sh",
        "init.sh",
        "logs.sh",
        "migrate.sh",
        "ps.sh",
        "rebuild.sh",
        "restart.sh",
        "restore-db.sh",
        "up.sh",
        "update.sh",
    ):
        (scripts / script).write_text(
            "#!/bin/sh\n",
            encoding="utf-8",
        )

    (app_root / "Makefile").write_text(
        """
backup:
check:
dev:
down:
help:
init:
logs:
migrate:
prod:
ps:
rebuild:
restart:
restore:
up:
update:
""",
        encoding="utf-8",
    )

    template = TemplateAnalyzer().analyze(template_root)
    report = TemplateComplianceAnalyzer().analyze(
        app_root,
        template,
    )

    assert not any(
        finding.path == ".env.local"
        for finding in report.findings
    )
    assert not any(
        finding.code == "ENV002"
        for finding in report.findings
    )

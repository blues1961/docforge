from pathlib import Path

from docforge.detectors import TechnologyDetector
from docforge.scanners import FileSystemScanner


def test_detector_finds_django_react_vite_and_docker(
    tmp_path: Path,
) -> None:
    backend = tmp_path / "backend"
    backend.mkdir()
    (backend / "manage.py").write_text("", encoding="utf-8")

    config = backend / "config"
    config.mkdir()
    (config / "settings.py").write_text("", encoding="utf-8")

    frontend = tmp_path / "frontend"
    frontend.mkdir()
    (frontend / "package.json").write_text(
        """
        {
          "dependencies": {
            "react": "^19.0.0"
          },
          "devDependencies": {
            "vite": "^7.0.0"
          }
        }
        """,
        encoding="utf-8",
    )

    (tmp_path / "docker-compose.dev.yml").write_text(
        """
        services:
          db:
            image: postgres:16-alpine
          backend:
            build: ./backend
          frontend:
            build: ./frontend
        networks:
          appnet:
        volumes:
          pgdata:
        """,
        encoding="utf-8",
    )

    project = FileSystemScanner().scan(tmp_path)
    TechnologyDetector().detect(project)

    assert "Django" in project.frameworks
    assert "React" in project.frameworks
    assert "Vite" in project.frameworks

    technology_names = {
        technology.name
        for technology in project.technologies
    }

    assert "Docker Compose" in technology_names
    assert "PostgreSQL" in technology_names

    service_names = {
        service.name
        for service in project.docker.services
    }

    assert service_names == {"db", "backend", "frontend"}
    assert project.docker.networks == ["appnet"]
    assert project.docker.volumes == ["pgdata"]


def test_detector_finds_traefik_labels(
    tmp_path: Path,
) -> None:
    (tmp_path / "docker-compose.prod.yml").write_text(
        """
        services:
          frontend:
            image: example/frontend
            labels:
              - traefik.enable=true
              - traefik.http.routers.frontend.rule=Host(`example.com`)
        """,
        encoding="utf-8",
    )

    project = FileSystemScanner().scan(tmp_path)
    TechnologyDetector().detect(project)

    assert project.docker.uses_traefik is True

    technology_names = {
        technology.name
        for technology in project.technologies
    }

    assert "Traefik" in technology_names


def test_detector_finds_hugo_from_its_configuration(
    tmp_path: Path,
) -> None:
    (tmp_path / "hugo.toml").write_text(
        'baseURL = "https://example.test/"\n',
        encoding="utf-8",
    )
    (tmp_path / "content").mkdir()
    (tmp_path / "layouts").mkdir()

    project = FileSystemScanner().scan(tmp_path)
    TechnologyDetector().detect(project)

    assert "Hugo" in project.frameworks
    hugo = next(
        technology
        for technology in project.technologies
        if technology.name == "Hugo"
    )
    assert hugo.category == "static-site-generator"
    assert hugo.evidence == ["hugo.toml"]

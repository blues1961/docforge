from pathlib import Path

from project_assistant.analyzers import ArchitectureAnalyzer
from project_assistant.detectors import TechnologyDetector
from project_assistant.scanners import FileSystemScanner


def test_architecture_analyzer_reads_compose_services(
    tmp_path: Path,
) -> None:
    backend = tmp_path / "backend"
    backend.mkdir()
    (backend / "manage.py").write_text(
        "",
        encoding="utf-8",
    )

    frontend = tmp_path / "frontend"
    frontend.mkdir()
    (frontend / "package.json").write_text(
        """
        {
          "dependencies": {
            "react": "^18.3.1"
          },
          "devDependencies": {
            "vite": "^5.4.2"
          }
        }
        """,
        encoding="utf-8",
    )

    (tmp_path / "docker-compose.prod.yml").write_text(
        """
services:
  db:
    image: postgres:16-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data
  backend:
    build:
      context: ./backend
    depends_on:
      - db
    networks:
      - appnet
      - edge
    healthcheck:
      test: ["CMD", "true"]
    labels:
      - traefik.enable=true
      - traefik.http.routers.api.rule=Host(`api.example.com`)
  frontend:
    build: ./frontend
    depends_on:
      - backend
    networks:
      - appnet
      - edge

networks:
  appnet:
  edge:
    external: true

volumes:
  pgdata:
""",
        encoding="utf-8",
    )

    project = FileSystemScanner().scan(tmp_path)
    TechnologyDetector().detect(project)

    facts = ArchitectureAnalyzer().analyze(project)

    assert facts.external_networks == ["edge"]
    assert facts.database_services == ["db"]
    assert facts.backend_services == ["backend"]
    assert facts.frontend_services == ["frontend"]

    backend_facts = next(
        service
        for service in facts.services
        if service.name == "backend"
    )

    assert backend_facts.depends_on == ["db"]
    assert backend_facts.healthcheck is True
    assert backend_facts.traefik_routes == [
        "Host(`api.example.com`)"
    ]

import json
from pathlib import Path

from docforge.detectors import TechnologyDetector
from docforge.knowledge import ProjectKnowledgeBuilder
from docforge.manual_blueprint import ManualBlueprintRegistry
from docforge.manual_django_react import DjangoReactManualKnowledgeBuilder
from docforge.manual_prompt import DjangoReactManualPromptBuilder
from docforge.manual_service import ManualPreparationService
from docforge.profiles import ProfileDetector
from docforge.scanners import FileSystemScanner


def _create_django_react_project(
    root: Path,
    *,
    admin_enabled: bool = True,
) -> None:
    (root / "backend" / "App").mkdir(parents=True)
    (root / "backend" / "api" / "management" / "commands").mkdir(parents=True)
    (root / "frontend" / "src").mkdir(parents=True)
    (root / "scripts").mkdir()

    (root / ".gitignore").write_text(
        ".docforge/\n.venv/\n__pycache__/\n*.pyc\n",
        encoding="utf-8",
    )
    (root / ".env.template.example").write_text(
        "APP_NAME=\nAPP_SLUG=\nAPP_DEPOT=\nAPP_NO=\nADMIN_USERNAME=\nADMIN_PASSWORD=\nADMIN_EMAIL=\n",
        encoding="utf-8",
    )
    (root / ".env.dev").write_text(
        "APP_ENV=dev\nAPP_NAME=Contact\nAPP_SLUG=contact\nAPP_DEPOT=contact\nAPP_NO=3\nPOSTGRES_USER=contact_pg_user\nPOSTGRES_DB=contact_pg_db\nDEV_DB_PORT=5435\nDEV_VITE_PORT=5176\nDEV_API_PORT=8004\nVITE_API_BASE=/api\nDJANGO_DEBUG=true\nDJANGO_ALLOWED_HOSTS=localhost,127.0.0.1\nDJANGO_CSRF_TRUSTED_ORIGINS=http://localhost:5176\nCALENDRIER_API_BASE=http://host.docker.internal:8003/api\nCALENDRIER_API_TIMEOUT=5\n",
        encoding="utf-8",
    )
    (root / ".env.prod").write_text(
        "APP_ENV=prod\nAPP_NAME=Contact\nAPP_SLUG=contact\nAPP_DEPOT=contact\nAPP_NO=3\nAPP_HOST=contact.example.test\nPOSTGRES_USER=contact_pg_user\nPOSTGRES_DB=contact_pg_db\nVITE_API_BASE=/api\nDJANGO_DEBUG=false\nDJANGO_ALLOWED_HOSTS=contact.example.test,backend\nDJANGO_CSRF_TRUSTED_ORIGINS=https://contact.example.test\nCALENDRIER_API_BASE=https://cal.example.test/api\nCALENDRIER_API_TIMEOUT=5\n",
        encoding="utf-8",
    )
    (root / ".env").symlink_to(".env.dev")
    (root / ".env.local").write_text(
        "POSTGRES_PASSWORD=supersecret\nDJANGO_SECRET_KEY=super-secret-key\nCONTACT_API_TOKEN=very-secret-token\n",
        encoding="utf-8",
    )

    (root / "docker-compose.dev.yml").write_text(
        """
services:
  db:
    image: postgres:16
    env_file:
      - .env.dev
      - .env.local
    ports:
      - "${DEV_DB_PORT}:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $$POSTGRES_USER"]
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    command: /app/entrypoint.sh python manage.py runserver 0.0.0.0:8000
    env_file:
      - .env.dev
      - .env.local
    volumes:
      - ./backend:/app
    ports:
      - "${DEV_API_PORT}:8000"
    depends_on:
      - db
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    command: npm run dev -- --host
    env_file:
      - .env.dev
      - .env.local
    volumes:
      - ./frontend:/app
    ports:
      - "${DEV_VITE_PORT}:5173"
    depends_on:
      - backend
""",
        encoding="utf-8",
    )
    (root / "docker-compose.prod.yml").write_text(
        """
services:
  db:
    image: postgres:16-alpine
    env_file:
      - .env
      - .env.local
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - internal
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    env_file:
      - .env
      - .env.local
    depends_on:
      - db
    networks:
      - internal
      - edge
    labels:
      - "traefik.http.routers.contact-api.rule=Host(`${APP_HOST}`) && PathPrefix(`/api`)"
      - "traefik.http.routers.contact-admin.rule=Host(`${APP_HOST}`) && PathPrefix(`/admin`)"
      - "traefik.http.routers.contact-static.rule=Host(`${APP_HOST}`) && PathPrefix(`/static`)"
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    env_file:
      - .env
      - .env.local
    depends_on:
      - backend
    networks:
      - internal
      - edge
    labels:
      - "traefik.http.routers.contact-frontend.rule=Host(`${APP_HOST}`)"
volumes:
  postgres_data:
networks:
  internal:
  edge:
    external: true
""",
        encoding="utf-8",
    )
    (root / "Makefile").write_text(
        ".DEFAULT_GOAL := help\nSCRIPTS_DIR := ./scripts\n.PHONY: help init dev prod up down restart rebuild logs ps check migrate backup restore\n\ninit:\n\t$(SCRIPTS_DIR)/init.sh\n\ndev:\n\t$(SCRIPTS_DIR)/env-switch.sh dev\n\nprod:\n\t$(SCRIPTS_DIR)/env-switch.sh prod\n\nup:\n\t$(SCRIPTS_DIR)/up.sh\n\ndown:\n\t$(SCRIPTS_DIR)/down.sh\n\nrestart:\n\t$(SCRIPTS_DIR)/restart.sh\n\nrebuild:\n\t$(SCRIPTS_DIR)/rebuild.sh $(SERVICE)\n\nlogs:\n\t$(SCRIPTS_DIR)/logs.sh $(SERVICE)\n\nps:\n\t$(SCRIPTS_DIR)/ps.sh\n\ncheck:\n\t$(SCRIPTS_DIR)/check-invariants.sh\n\nmigrate:\n\t$(SCRIPTS_DIR)/migrate.sh\n\nbackup:\n\t$(SCRIPTS_DIR)/backup-db.sh\n\nrestore:\n\t$(SCRIPTS_DIR)/restore-db.sh $(FILE)\n",
        encoding="utf-8",
    )

    for name, content in {
        "init.sh": "#!/usr/bin/env bash\n./scripts/generate-env.sh\n./scripts/up.sh\n",
        "env-switch.sh": "#!/usr/bin/env bash\nln -sf .env.$1 .env\n",
        "up.sh": "#!/usr/bin/env bash\ndocker compose --env-file .env --env-file .env.local -f docker-compose.${APP_ENV}.yml up -d\n",
        "down.sh": "#!/usr/bin/env bash\ndocker compose --env-file .env --env-file .env.local -f docker-compose.${APP_ENV}.yml down\n",
        "restart.sh": "#!/usr/bin/env bash\n./scripts/down.sh\n./scripts/up.sh\n",
        "rebuild.sh": "#!/usr/bin/env bash\ndocker compose --env-file .env --env-file .env.local -f docker-compose.${APP_ENV}.yml build \"$@\"\n",
        "logs.sh": "#!/usr/bin/env bash\ndocker compose --env-file .env --env-file .env.local -f docker-compose.${APP_ENV}.yml logs -f \"$@\"\n",
        "ps.sh": "#!/usr/bin/env bash\ndocker compose --env-file .env --env-file .env.local -f docker-compose.${APP_ENV}.yml ps\n",
        "check-invariants.sh": "#!/usr/bin/env bash\necho ok\n",
        "migrate.sh": "#!/usr/bin/env bash\ndocker compose --env-file .env --env-file .env.local -f docker-compose.${APP_ENV}.yml exec backend python manage.py migrate\ndocker compose --env-file .env --env-file .env.local -f docker-compose.${APP_ENV}.yml exec backend python manage.py ensure_admin\n",
        "backup-db.sh": "#!/usr/bin/env bash\ndocker compose --env-file .env --env-file .env.local -f docker-compose.${APP_ENV}.yml exec -T db pg_dump -U \"$POSTGRES_USER\" \"$POSTGRES_DB\"\n",
        "restore-db.sh": "#!/usr/bin/env bash\ngunzip -c \"$1\" | docker compose --env-file .env --env-file .env.local -f docker-compose.${APP_ENV}.yml exec -T db psql -U \"$POSTGRES_USER\" \"$POSTGRES_DB\"\n",
        "generate-env.sh": "#!/usr/bin/env bash\nensure_local_key \"POSTGRES_PASSWORD\"\nensure_local_key \"DJANGO_SECRET_KEY\"\nensure_local_key \"CONTACT_API_TOKEN\"\nensure_local_key \"CALENDRIER_API_TOKEN\"\n",
    }.items():
        (root / "scripts" / name).write_text(content, encoding="utf-8")

    (root / "backend" / "requirements.txt").write_text(
        "Django\ndjangorestframework\ndjangorestframework-simplejwt\npsycopg[binary]\nwhitenoise\n",
        encoding="utf-8",
    )
    (root / "backend" / "Dockerfile.dev").write_text("FROM python:3.11\n", encoding="utf-8")
    (root / "backend" / "Dockerfile.prod").write_text("FROM python:3.11\n", encoding="utf-8")
    (root / "frontend" / "Dockerfile.dev").write_text("FROM node:20\n", encoding="utf-8")
    (root / "frontend" / "Dockerfile").write_text("FROM nginx:alpine\n", encoding="utf-8")

    admin_block = 'path("admin/", admin.site.urls),\n' if admin_enabled else ''
    installed_admin = '    "django.contrib.admin",\n' if admin_enabled else ''

    (root / "backend" / "App" / "settings.py").write_text(
        f'''import os\nimport sys\nfrom datetime import timedelta\nfrom pathlib import Path\n\nBASE_DIR = Path(__file__).resolve().parent.parent\nSECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-only")\nDEBUG = os.getenv("APP_ENV", "dev") == "dev"\nINSTALLED_APPS = [\n{installed_admin}    "django.contrib.auth",\n    "django.contrib.contenttypes",\n    "django.contrib.sessions",\n    "django.contrib.messages",\n    "django.contrib.staticfiles",\n    "rest_framework",\n    "rest_framework_simplejwt.token_blacklist",\n    "api",\n]\nROOT_URLCONF = "App.urls"\nif "test" in sys.argv:\n    DATABASES = {{"default": {{"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "test.sqlite3"}}}}\nelse:\n    DATABASES = {{"default": {{"ENGINE": "django.db.backends.postgresql", "NAME": os.getenv("POSTGRES_DB"), "USER": os.getenv("POSTGRES_USER"), "PASSWORD": os.getenv("POSTGRES_PASSWORD"), "HOST": os.getenv("POSTGRES_HOST", "db"), "PORT": os.getenv("POSTGRES_PORT", "5432")}}}}\nREST_FRAMEWORK = {{"DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",), "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",)}}\nSIMPLE_JWT = {{"ACCESS_TOKEN_LIFETIME": timedelta(minutes=30)}}\nCSRF_TRUSTED_ORIGINS = [origin.strip() for origin in os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if origin.strip()]\nif os.getenv("APP_HOST"):\n    CSRF_TRUSTED_ORIGINS.append(f"https://{{os.getenv('APP_HOST')}}")\n''',
        encoding="utf-8",
    )
    (root / "backend" / "App" / "urls.py").write_text(
        f'from django.contrib import admin\nfrom django.urls import include, path\n\nurlpatterns = [\n    {admin_block}    path("api/", include("api.urls")),\n]\n',
        encoding="utf-8",
    )
    (root / "backend" / "api" / "models.py").write_text(
        'from django.conf import settings\nfrom django.db import models\n\nclass Contact(models.Model):\n    class Visibility(models.TextChoices):\n        PUBLIC = "public", "Public"\n        PRIVATE = "private", "Privé"\n\n    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="contacts")\n    visibility = models.CharField(max_length=16, choices=Visibility.choices, default=Visibility.PUBLIC)\n    name = models.CharField(max_length=255, blank=True, default="")\n    email = models.EmailField(blank=True, default="")\n    birthday = models.DateField(blank=True, null=True)\n    encrypted_payload = models.TextField(blank=True, default="")\n',
        encoding="utf-8",
    )
    (root / "backend" / "api" / "views.py").write_text(
        '''import hmac\nimport os\n\nfrom django.contrib.auth import get_user_model\nfrom rest_framework import viewsets\nfrom rest_framework.decorators import action, api_view, permission_classes\nfrom rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated\nfrom rest_framework.response import Response\nfrom rest_framework.views import APIView\n\nfrom .models import Contact\n\nUser = get_user_model()\n\n\n@api_view(["GET"])\n@permission_classes([AllowAny])\ndef health(request):\n    return Response({"status": "ok"})\n\n\nclass WhoAmIView(APIView):\n    permission_classes = [IsAuthenticated]\n\n    def get(self, request):\n        return Response({"username": request.user.username})\n\n\nclass LogoutView(APIView):\n    permission_classes = [IsAuthenticated]\n\n    def post(self, request):\n        return Response(status=204)\n\n\nclass UserViewSet(viewsets.ModelViewSet):\n    permission_classes = [IsAdminUser]\n    queryset = User.objects.all()\n\n    @action(detail=True, methods=["post"])\n    def reset_password(self, request, pk=None):\n        return Response({"ok": True})\n\n\nclass ContactViewSet(viewsets.ModelViewSet):\n    permission_classes = [IsAuthenticated]\n    queryset = Contact.objects.all()\n\n    @action(detail=True, methods=["post"])\n    def sync_birthday(self, request, pk=None):\n        return Response({"ok": True})\n\n\nclass ContactIntegrationListCreateView(APIView):\n    permission_classes = [AllowAny]\n\n    def get(self, request):\n        configured_token = str(os.getenv("CONTACT_API_TOKEN") or "").strip()\n        hmac.compare_digest(configured_token, configured_token)\n        return Response({"token": bool(configured_token)})\n\n    def post(self, request):\n        return Response({"ok": True}, status=201)\n\n\nclass ContactIntegrationDetailView(APIView):\n    permission_classes = [AllowAny]\n\n    def get(self, request, pk):\n        return Response({"id": pk})\n''',
        encoding="utf-8",
    )
    (root / "backend" / "api" / "urls.py").write_text(
        'from django.urls import include, path\nfrom rest_framework.routers import DefaultRouter\nfrom rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView\n\nfrom .views import ContactIntegrationDetailView, ContactIntegrationListCreateView, ContactViewSet, LogoutView, UserViewSet, WhoAmIView, health\n\nrouter = DefaultRouter()\nrouter.register("contacts", ContactViewSet, basename="contact")\nrouter.register("users", UserViewSet, basename="user")\n\nurlpatterns = [\n    path("health/", health),\n    path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),\n    path("auth/logout/", LogoutView.as_view(), name="logout"),\n    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),\n    path("auth/whoami/", WhoAmIView.as_view(), name="whoami"),\n    path("integrations/contacts/", ContactIntegrationListCreateView.as_view(), name="integration-contacts"),\n    path("integrations/contacts/<int:pk>/", ContactIntegrationDetailView.as_view(), name="integration-contact-detail"),\n    path("", include(router.urls)),\n]\n',
        encoding="utf-8",
    )
    (root / "backend" / "api" / "management" / "commands" / "ensure_admin.py").write_text(
        'import os\nfrom django.core.management.base import BaseCommand\n\nclass Command(BaseCommand):\n    help = "Crée ou met à jour le compte administrateur initial à partir des variables ADMIN_*."\n\n    def handle(self, *args, **options):\n        username = os.getenv("ADMIN_USERNAME", "").strip()\n        email = os.getenv("ADMIN_EMAIL", "").strip()\n        password = os.getenv("ADMIN_PASSWORD", "")\n        if not username or not email or not password:\n            return\n',
        encoding="utf-8",
    )

    (root / "frontend" / "package.json").write_text(
        '{"type":"module","scripts":{"dev":"vite","build":"vite build","test":"node --test src/*.test.mjs"},"dependencies":{"react":"^18.0.0","react-dom":"^18.0.0","vite":"^5.0.0","@vitejs/plugin-react":"^4.0.0"}}',
        encoding="utf-8",
    )
    (root / "frontend" / "vite.config.js").write_text(
        'import { defineConfig } from "vite";\nimport react from "@vitejs/plugin-react";\nexport default defineConfig({ plugins: [react()], server: { host: "0.0.0.0", proxy: { "/api": { target: "http://backend:8000", changeOrigin: true }, "/admin": { target: "http://backend:8000", changeOrigin: true } } } });\n',
        encoding="utf-8",
    )
    (root / "frontend" / "src" / "main.jsx").write_text(
        'import React from "react";\nimport { createRoot } from "react-dom/client";\nimport App from "./App.jsx";\ncreateRoot(document.getElementById("root")).render(<App />);\n',
        encoding="utf-8",
    )
    (root / "frontend" / "src" / "api.js").write_text(
        'const API_BASE = import.meta.env.VITE_API_BASE || "/api";\nasync function request(path, options = {}) { return fetch(`${API_BASE}${path}`, { headers: { ...(options.token ? { Authorization: `Bearer ${options.token}` } : {}) } }); }\nexport function login(username, password) { return request("/auth/login/", { method: "POST", body: { username, password } }); }\nexport function logout(token, refresh) { return request("/auth/logout/", { method: "POST", token, body: { refresh } }); }\nexport function whoAmI(token) { return request("/auth/whoami/", { token }); }\nexport function getContacts(token) { return request("/contacts/", { token }); }\nexport function createContact(token, payload) { return request("/contacts/", { method: "POST", token, body: payload }); }\nexport function updateContact(token, contactId, payload) { return request(`/contacts/${contactId}/`, { method: "PATCH", token, body: payload }); }\nexport function deleteContact(token, contactId) { return request(`/contacts/${contactId}/`, { method: "DELETE", token }); }\nexport function syncContactBirthday(token, contactId, payload) { return request(`/contacts/${contactId}/sync_birthday/`, { method: "POST", token, body: payload }); }\nexport function getUsers(token) { return request("/users/", { token }); }\nexport function createUser(token, payload) { return request("/users/", { method: "POST", token, body: payload }); }\nexport function updateUser(token, userId, payload) { return request(`/users/${userId}/`, { method: "PATCH", token, body: payload }); }\nexport function resetUserPassword(token, userId, password) { return request(`/users/${userId}/reset_password/`, { method: "POST", token, body: { password } }); }\n',
        encoding="utf-8",
    )
    (root / "frontend" / "src" / "App.jsx").write_text(
        'import React, { useEffect, useState } from "react";\nimport { createContact, createUser, deleteContact, getContacts, getUsers, login, logout, resetUserPassword, syncContactBirthday, updateContact, updateUser, whoAmI } from "./api.js";\nimport { decryptPrivateFields } from "./crypto.js";\nconst SESSION_STORAGE_KEY = "contact.session";\nfunction AdminPanel() { return <section><h2>Utilisateurs</h2></section>; }\nexport default function App() { const [theme, setTheme] = useState("dark"); const [session, setSession] = useState(window.localStorage.getItem(SESSION_STORAGE_KEY)); const [search, setSearch] = useState(""); const [visibilityFilter, setVisibilityFilter] = useState("all"); useEffect(() => { window.localStorage.setItem("theme", theme); }, [theme]); async function handleLogin() { await login("u", "p"); await whoAmI("token"); await getContacts("token"); await getUsers("token"); await createContact("token", {}); await updateContact("token", 1, {}); await deleteContact("token", 1); await syncContactBirthday("token", 1, {}); await createUser("token", {}); await updateUser("token", 1, {}); await resetUserPassword("token", 1, "pw"); await logout("token", "refresh"); decryptPrivateFields({}); } return <main><h1>Accès privé</h1><h2>Nouveau contact</h2><label>Recherche</label><label>Visibilité</label><button onClick={() => { setTheme(theme === "dark" ? "light" : "dark"); setSearch(search); setVisibilityFilter(visibilityFilter); setSession(session); }}>Thème</button><AdminPanel /></main>; }\n',
        encoding="utf-8",
    )
    (root / "frontend" / "src" / "crypto.js").write_text(
        'const encoder = new TextEncoder();\nconst decoder = new TextDecoder();\nexport const PRIVATE_ENCRYPTION_VERSION = "v1";\nasync function importKeyMaterial(keyMaterial) { return crypto.subtle.importKey("raw", new Uint8Array(), "AES-GCM", false, ["encrypt", "decrypt"]); }\nexport async function deriveVaultKeyMaterial(passphrase, scope = "default") { const baseKey = await crypto.subtle.importKey("raw", encoder.encode(passphrase), "PBKDF2", false, ["deriveBits"]); const derivedBits = await crypto.subtle.deriveBits({ name: "PBKDF2", salt: encoder.encode(`contacts-vault:${scope}:v1`), iterations: 250000, hash: "SHA-256" }, baseKey, 256); return derivedBits; }\nexport async function encryptPrivateFields(fields, keyMaterial) { const key = await importKeyMaterial(keyMaterial); const iv = crypto.getRandomValues(new Uint8Array(12)); const plaintext = encoder.encode(JSON.stringify(fields)); const ciphertext = await crypto.subtle.encrypt({ name: "AES-GCM", iv }, key, plaintext); return JSON.stringify({ version: PRIVATE_ENCRYPTION_VERSION, iv, ciphertext }); }\nexport async function decryptPrivateFields(payload, keyMaterial) { const envelope = typeof payload === "string" ? JSON.parse(payload) : payload; const key = await importKeyMaterial(keyMaterial); const plaintext = await crypto.subtle.decrypt({ name: "AES-GCM", iv: envelope.iv }, key, envelope.ciphertext); return JSON.parse(decoder.decode(plaintext)); }\n',
        encoding="utf-8",
    )


def _build_knowledge(root: Path):
    project = FileSystemScanner().scan(root)
    TechnologyDetector().detect(project)
    profile = ProfileDetector().resolve(project)
    knowledge = ProjectKnowledgeBuilder().build(
        project,
        profile_instance=profile,
    )
    return project, profile, knowledge


def test_django_react_profile_selects_specialized_manual_components(tmp_path: Path) -> None:
    _create_django_react_project(tmp_path)
    _project, profile, _knowledge = _build_knowledge(tmp_path)

    assert profile.name == "django-react"
    assert isinstance(
        profile.build_manual_knowledge_builder(),
        DjangoReactManualKnowledgeBuilder,
    )
    assert profile.build_manual_blueprint().profile_name == "django-react"
    assert isinstance(
        profile.build_manual_prompt_builder(),
        DjangoReactManualPromptBuilder,
    )


def test_django_react_blueprint_is_compact_and_user_oriented() -> None:
    blueprint = ManualBlueprintRegistry().blueprint_for_profile(
        "django-react"
    )

    assert blueprint.profile_name == "django-react"
    assert len(blueprint.sections) == 13
    assert len(blueprint.sections) < 26

    identifiers = [section.identifier for section in blueprint.sections]
    assert identifiers == [
        "presentation",
        "audience-roles",
        "main-features",
        "quick-start",
        "application-usage",
        "administration",
        "installation-configuration",
        "operations",
        "technical-reference",
        "security",
        "troubleshooting",
        "operational-commands-reference",
        "limitations",
    ]
    assert identifiers.index("application-usage") < identifiers.index("installation-configuration")
    assert identifiers.index("installation-configuration") < identifiers.index("technical-reference")
    assert "environment-configuration" not in identifiers
    assert "development-environment" not in identifiers
    assert "production-environment" not in identifiers
    assert "docker-services" not in identifiers
    assert "database" not in identifiers
    assert "migrations" not in identifiers
    assert "tests" not in identifiers
    assert "backup-restore" not in identifiers


def test_django_react_knowledge_separates_compose_environments_and_ports(tmp_path: Path) -> None:
    _create_django_react_project(tmp_path)
    _project, _profile, knowledge = _build_knowledge(tmp_path)

    envs = {item.name: item for item in knowledge.environments.items}
    assert {"dev", "prod"}.issubset(envs)
    assert envs["dev"].compose_file == "docker-compose.dev.yml"
    assert envs["prod"].compose_file == "docker-compose.prod.yml"
    assert any(service.name == "frontend" for service in envs["dev"].services)
    assert any(
        "${DEV_VITE_PORT}:5173" in service.ports
        for service in envs["dev"].services
        if service.name == "frontend"
    )
    assert all(
        not service.ports
        for service in envs["prod"].services
        if service.name == "frontend"
    )
    assert ".env.dev" in envs["dev"].env_files
    assert ".env" in envs["prod"].env_files


def test_django_react_knowledge_detects_variables_without_secret_values(tmp_path: Path) -> None:
    _create_django_react_project(tmp_path)
    _project, _profile, knowledge = _build_knowledge(tmp_path)

    variables = {item.name: item for item in knowledge.environment_variables.variables}
    assert "APP_HOST" in variables
    assert "DJANGO_SECRET_KEY" in variables
    assert "POSTGRES_PASSWORD" in variables
    assert "CONTACT_API_TOKEN" in variables
    assert variables["DJANGO_SECRET_KEY"].sensitive is True
    assert variables["POSTGRES_PASSWORD"].default_value is None
    payload = knowledge.to_json()
    assert "supersecret" not in payload
    assert "super-secret-key" not in payload
    assert "very-secret-token" not in payload


def test_django_react_knowledge_detects_commands_django_react_and_capabilities(tmp_path: Path) -> None:
    _create_django_react_project(tmp_path)
    _project, _profile, knowledge = _build_knowledge(tmp_path)

    command_names = {item.name for item in knowledge.operational_commands.commands}
    assert {
        "init",
        "dev",
        "prod",
        "up",
        "down",
        "restart",
        "rebuild",
        "logs",
        "ps",
        "check",
        "migrate",
        "backup",
        "restore",
    }.issubset(command_names)
    assert ".DEFAULT_GOAL" not in command_names
    assert "SCRIPTS_DIR" not in command_names
    assert "make migrate" in knowledge.django.migration_commands
    assert "python manage.py ensure_admin" in knowledge.django.create_admin_commands
    assert knowledge.django.admin_enabled is True
    assert {"Contact"} == {model.name for model in knowledge.django.models}
    assert "/auth/login/" in knowledge.django.routes
    assert "GET /contacts/" in knowledge.react.api_calls
    assert knowledge.react.dev_command == "npm run dev"
    assert knowledge.react.build_command == "npm run build"
    assert knowledge.react.routes == ["/"]
    assert any(route.full_path == "/api/auth/login/" for route in knowledge.django.resolved_routes)
    assert any(endpoint.path == "/api/users/" and "IsAdminUser" in endpoint.permissions for endpoint in knowledge.django.endpoints)
    visibility_field = next(
        field
        for model in knowledge.django.model_schemas
        if model.name == "Contact"
        for field in model.fields
        if field.name == "visibility"
    )
    assert [choice.value for choice in visibility_field.choices] == ["public", "private"]
    assert knowledge.react.crypto.detected is True
    assert knowledge.react.crypto.key_derivation == "PBKDF2"
    assert any(
        cap.label.startswith("Consulter") and "contact" in cap.label
        for cap in knowledge.capabilities.capabilities
    )


def test_django_react_manual_prepare_is_application_oriented(tmp_path: Path) -> None:
    _create_django_react_project(tmp_path)
    result = ManualPreparationService().prepare(
        tmp_path,
        clean=True,
        mode="both",
    )

    data = json.loads(result.knowledge_file.read_text(encoding="utf-8"))
    payload = json.dumps(data, ensure_ascii=False)
    workflow_ids = {item["identifier"] for item in data["workflows"]}
    command_paths = {item["command_path"] for item in data["commands"]}

    assert "prepare-dev-config" in workflow_ids
    assert "start-development" in workflow_ids
    assert "apply-migrations" in workflow_ids
    assert "backup-database" in workflow_ids
    assert "restore-database" in workflow_ids
    assert "analyze-project" not in workflow_ids
    assert "build-project-knowledge" not in workflow_ids
    assert "docforge analyze" not in payload
    assert "docforge apply" not in payload
    assert "docforge manual prepare" not in payload
    assert "make up" in command_paths
    assert "make migrate" in command_paths
    run_tests = next(item for item in data["workflows"] if item["identifier"] == "run-tests")
    assert run_tests["commands"] == ["node --test src/*.test.mjs"]
    assert run_tests["operational_status"] == "requires-context"
    create_admin = next(item for item in data["workflows"] if item["identifier"] == "create-admin")
    assert create_admin["commands"] == ["make migrate"]
    assert any(item["identifier"] == "API-SCHEMA-MISSING" for item in data["missing_information"])
    rebuild = next(item for item in data["commands"] if item["name"] == "rebuild")
    assert rebuild["parameters"][0]["name"] == "SERVICE"
    restore = next(item for item in data["commands"] if item["name"] == "restore")
    assert restore["parameters"][0]["name"] == "FILE"
    assert any(route["full_path"] == "/api/auth/login/" for route in data["django"]["resolved_routes"])
    assert any(endpoint["path"] == "/api/users/" and "IsAdminUser" in endpoint["permissions"] for endpoint in data["django"]["endpoints"])
    assert data["conflicts"] == []
    assert "project-assistant" not in payload
    assert "/home/" not in payload


def test_django_react_blueprint_and_prompt_and_section_omission(tmp_path: Path) -> None:
    _create_django_react_project(tmp_path, admin_enabled=False)
    result = ManualPreparationService().prepare(
        tmp_path,
        clean=True,
        mode="both",
    )

    prompt = result.full_prompt_file.read_text(encoding="utf-8")
    section_names = [path.name for path in result.section_prompt_files]
    section_contents = {
        path.name: path.read_text(encoding="utf-8")
        for path in result.section_prompt_files
    }
    manifest = json.loads(result.manifest_file.read_text(encoding="utf-8"))

    assert len(section_names) == 13
    assert section_names == [
        "01-presentation.md",
        "02-audience-roles.md",
        "03-main-features.md",
        "04-quick-start.md",
        "05-application-usage.md",
        "06-administration.md",
        "07-installation-configuration.md",
        "08-operations.md",
        "09-technical-reference.md",
        "10-security.md",
        "11-troubleshooting.md",
        "12-operational-commands-reference.md",
        "13-limitations.md",
    ]

    assert "Le manuel concerne l’application analysée" in prompt
    assert "Les commandes DocForge ne sont pas des commandes d’utilisation de l’application analysée." in prompt
    assert "source unique de vérité" in prompt
    assert "aucune connaissance externe" in prompt
    assert "`derived` = fait déduit d’éléments compatibles" in prompt
    assert "`configured` = fait provenant du profil ou de la configuration DocForge" in prompt
    assert "`unresolved` = fait incomplet" in prompt
    assert "utilise uniquement `full_path` lorsque `resolution_status` vaut `resolved`" in prompt
    assert "n’attribue jamais des permissions globales à tous les endpoints" in prompt
    assert "un workflow `requires-context` ne doit jamais être présenté comme immédiatement exécutable" in prompt
    assert "Ne présente jamais `make check` comme une suite de tests" in prompt
    assert "Associe `make migrate` à la création ou mise à jour de l’administrateur uniquement si la chaîne démontrée" in prompt
    assert "respecte les contextes fournis par ManualKnowledge" in prompt
    assert "Utilise `missing_information` et `limitations.items` comme source prioritaire" in prompt
    assert "Pour `react.crypto`, décris uniquement l’implémentation détectée" in prompt
    assert "Le flux de DocForge s’arrête à la production de `manual-knowledge.json` et du prompt de rédaction" in prompt
    assert "Une URL syntaxiquement invalide ou contenant une interpolation déséquilibrée" in prompt
    assert "Les paramètres internes d’une commande ne doivent jamais être présentés comme arguments utilisateur" in prompt
    assert "Lorsqu’une cible alias délègue à des prérequis démontrés" in prompt
    assert "Les helpers internes du Makefile ne doivent pas encombrer la référence principale" in prompt
    assert "Lorsque `conflicts` est vide, n’ajoute pas une phrase de remplissage" in prompt
    assert "Si `capabilities.capabilities` contient des capacités backend ou frontend démontrées" in prompt
    assert "Chaque catégorie d’information doit avoir une section principale" in prompt
    assert "Ne recopie pas intégralement la liste des commandes, des services, des variables, des URLs ou des endpoints" in prompt
    assert "Le démarrage rapide doit contenir uniquement" in prompt
    assert "N’expose pas dans le manuel final un vocabulaire interne comme `workflow structuré`" in prompt
    assert "`PROJECT-VERSION-MISSING` devient une phrase" in prompt
    assert manifest["profile_name"] == "django-react"
    assert any("operational-commands-reference" in item for item in manifest["section_prompts"])
    assert not any("environment-configuration" in name for name in section_names)
    assert not any("development-environment" in name for name in section_names)
    assert not any("production-environment" in name for name in section_names)
    assert not any("docker-services" in name for name in section_names)
    assert not any("database" in name for name in section_names)
    assert not any("migrations" in name for name in section_names)
    assert not any("tests" in name for name in section_names)
    assert not any("backup-restore" in name for name in section_names)

    usage_section = section_contents["05-application-usage.md"]
    install_section = section_contents["07-installation-configuration.md"]
    operations_section = section_contents["08-operations.md"]
    technical_section = section_contents["09-technical-reference.md"]
    command_reference_section = section_contents["12-operational-commands-reference.md"]
    limitations_section = section_contents["13-limitations.md"]

    assert "Cette section vient avant l’infrastructure détaillée" in usage_section
    assert '"react"' in usage_section
    assert '"capabilities"' in usage_section
    assert '"django"' in usage_section
    assert "Cette section regroupe développement et production dans un même chapitre comparatif" in install_section
    assert '"environments"' in install_section
    assert '"environment_variables"' in install_section
    assert "Cette section regroupe démarrage, arrêt, migrations, journaux, diagnostic, tests, sauvegarde, restauration, mise à jour et reconstruction" in operations_section
    assert '"workflows"' in operations_section
    assert '"missing_information"' in operations_section
    assert "Cette section sert de référence technique principale pour l’architecture, les services Docker, la base de données, l’API et le chiffrement côté client." in technical_section
    assert '"django"' in technical_section
    assert '"react"' in technical_section
    assert '"conflicts"' in technical_section
    assert "les détails complets des commandes et paramètres peuvent apparaître" in command_reference_section
    assert '"operational_commands"' in command_reference_section
    assert '"workflows"' in command_reference_section
    assert "Remplace les identifiants techniques par des phrases lisibles destinées au lecteur final." in limitations_section
    assert '"missing_information"' in limitations_section


def test_django_react_manual_json_is_valid_and_does_not_modify_project_files(tmp_path: Path) -> None:
    _create_django_react_project(tmp_path)
    before = {
        path.relative_to(tmp_path).as_posix(): path.read_text(encoding="utf-8")
        for path in tmp_path.rglob("*")
        if path.is_file() and ".docforge" not in path.as_posix()
    }

    result = ManualPreparationService().prepare(
        tmp_path,
        clean=True,
        mode="both",
    )

    json.loads(result.knowledge_file.read_text(encoding="utf-8"))
    json.loads(result.manifest_file.read_text(encoding="utf-8"))

    after = {
        path.relative_to(tmp_path).as_posix(): path.read_text(encoding="utf-8")
        for path in tmp_path.rglob("*")
        if path.is_file() and ".docforge" not in path.as_posix()
    }
    assert before == after


def _create_generalized_django_react_project(root: Path) -> None:
    (root / "backend" / "gestionnaire_mdp").mkdir(parents=True)
    (root / "backend" / "api").mkdir(parents=True)
    (root / "frontend" / "src" / "routes").mkdir(parents=True)
    (root / "frontend" / "src" / "services").mkdir(parents=True)
    (root / "frontend" / "src" / "components").mkdir(parents=True)
    (root / "scripts").mkdir()

    (root / ".gitignore").write_text(".docforge/\n.venv/\n__pycache__/\n*.pyc\n", encoding="utf-8")
    (root / ".env.dev").write_text(
        "APP_ENV=dev\n"
        "APP_HOST=localhost\n"
        "DEV_API_PORT=8002 # 8001 + N\n"
        "DEV_DB_PORT=5433 # 5432 + N\n"
        "DEV_VITE_PORT=5174 # 5173 + N\n"
        'NAME="Gestionnaire MDP"\n'
        'LABEL_HASH="abc#def"\n'
        "EMPTY=\n"
        "VALUE='texte avec espaces'\n"
        "DJANGO_DEBUG=1\n"
        "POSTGRES_DB=mdp\n"
        "POSTGRES_USER=mdp_user\n",
        encoding="utf-8",
    )
    (root / ".env.prod").write_text(
        "APP_ENV=prod\n"
        "APP_HOST=mdp.mon-site.ca\n"
        "DJANGO_DEBUG=0\n"
        "FRONT_ORIGIN=https://mdp.mon-site.ca\n"
        "POSTGRES_DB=mdp\n"
        "POSTGRES_USER=mdp_user\n",
        encoding="utf-8",
    )
    (root / ".env").symlink_to(".env.dev")
    (root / ".env.local").write_text(
        "POSTGRES_PASSWORD=supersecret\nDJANGO_SECRET_KEY=super-secret-key\n",
        encoding="utf-8",
    )

    (root / "docker-compose.dev.yml").write_text(
        """
services:
  db:
    image: postgres:16
    env_file:
      - .env.dev
      - .env.local
    ports:
      - "${DEV_DB_PORT:-5433}:5432"
  backend:
    image: python:3.11
    env_file:
      - .env.dev
      - .env.local
    ports:
      - "${DEV_API_PORT:-8002}:8000"
  frontend:
    image: node:20
    env_file:
      - .env.dev
      - .env.local
    ports:
      - "${DEV_VITE_PORT:-5174}:5173"
""",
        encoding="utf-8",
    )
    (root / "docker-compose.prod.yml").write_text(
        """
services:
  db:
    image: postgres:16-alpine
  backend:
    image: python:3.11
    labels:
      - "traefik.http.routers.mdp-api.rule=Host(`${APP_HOST}`) && PathPrefix(`/api`)"
      - "traefik.http.routers.mdp-admin.rule=Host(`${APP_HOST}`) && PathPrefix(`/admin`)"
  frontend:
    image: nginx:alpine
    labels:
      - "traefik.http.routers.mdp-front.rule=Host(`${APP_HOST}`) && !PathPrefix(`/api/`) && !PathPrefix(`/admin/`)"
""",
        encoding="utf-8",
    )

    (root / "Makefile").write_text(
        """
COMPOSE = docker compose --env-file .env --env-file .env.local -f docker-compose.$(APP_ENV).yml
TREE_IGNORE ?= .git,node_modules,.venv
.PHONY: help dev prod env-check env-check-base env-check-local up down start stop logs rebuild test test-backend test-frontend restore restore-db backup-db backup-dir createsuperuser tree

help: ## Liste les commandes

dev: ## Pointe .env vers .env.dev
	ln -sf .env.dev .env

prod: ## Pointe .env vers .env.prod
	ln -sf .env.prod .env

env-check: env-check-base env-check-local ## Vérifie env + secrets locaux

env-check-base: ## Vérifie .env -> .env.$(APP_ENV)
	@test -f .env

env-check-local: ## Vérifie la présence de .env.local
	@test -f .env.local

up: env-check ## Démarre la stack
	$(COMPOSE) up -d

down: env-check ## Stoppe la stack
	$(COMPOSE) down

start: up ## Alias de up

stop: down ## Alias de down

logs: env-check ## Logs des services
	$(COMPOSE) logs -f $(SERVICE)

rebuild: env-check ## Rebuild des services
	$(COMPOSE) build $(SERVICE)

backup-dir:
	mkdir -p backup

backup-db: env-check backup-dir ## Sauvegarder la base
	$(COMPOSE) exec -T db pg_dump -U "$$POSTGRES_USER" "$$POSTGRES_DB"

restore: ## Alias standard vers restore-db
	$(MAKE) restore-db

restore-db: env-check ## Restaurer la DB depuis BACKUP=<fichier>
	BACKUP_FILE="$${BACKUP:-./backup/latest.sql.gz}"; \
	gunzip -c "$$BACKUP_FILE" | $(COMPOSE) exec -T db psql -U "$$POSTGRES_USER" "$$POSTGRES_DB"

createsuperuser: env-check ## Crée/MAJ admin via ADMIN_*
	$(COMPOSE) exec -T backend python manage.py shell -c 'import os; from django.contrib.auth import get_user_model; U=get_user_model(); u=os.getenv("ADMIN_USERNAME") or "admin"; e=os.getenv("ADMIN_EMAIL") or "admin@example.com"; p=os.getenv("ADMIN_PASSWORD") or "changeme"; obj,_=U.objects.update_or_create(username=u, defaults={"email":e}); obj.set_password(p); obj.is_staff=True; obj.is_superuser=True; obj.save()'

start-backend: env-check ## Démarrer backend
	$(COMPOSE) up -d backend

test: test-backend test-frontend ## Lance la suite de tests principale

test-backend: env-check ## Lance les tests backend Django
	$(COMPOSE) run --rm backend python manage.py test

test-frontend: env-check ## Lance les tests frontend
	$(COMPOSE) run --rm frontend npm run test

tree: ## Arborescence du projet
	tree -I "$(TREE_IGNORE)"
""",
        encoding="utf-8",
    )

    (root / "backend" / "requirements.txt").write_text(
        "Django\ndjangorestframework\ndjangorestframework-simplejwt\n",
        encoding="utf-8",
    )
    (root / "frontend" / "package.json").write_text(
        '{"type":"module","scripts":{"dev":"vite","build":"vite build","test":"vitest run"},"dependencies":{"react":"^18.0.0","react-dom":"^18.0.0"}}',
        encoding="utf-8",
    )
    (root / "frontend" / "vite.config.js").write_text(
        'export default { server: { host: "0.0.0.0" } };\n',
        encoding="utf-8",
    )
    (root / "backend" / "gestionnaire_mdp" / "settings.py").write_text(
        'import os\nimport sys\nfrom pathlib import Path\nBASE_DIR = Path(__file__).resolve().parent.parent\nSECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev")\nINSTALLED_APPS = ["django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes", "django.contrib.sessions", "rest_framework", "api"]\nROOT_URLCONF = "gestionnaire_mdp.urls"\nif "test" in sys.argv:\n    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "test.sqlite3"}}\nelse:\n    DATABASES = {"default": {"ENGINE": "django.db.backends.postgresql", "NAME": os.getenv("POSTGRES_DB"), "USER": os.getenv("POSTGRES_USER"), "PASSWORD": os.getenv("POSTGRES_PASSWORD"), "HOST": os.getenv("POSTGRES_HOST", "db"), "PORT": os.getenv("POSTGRES_PORT", "5432")}}\nREST_FRAMEWORK = {"DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",), "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",)}\n',
        encoding="utf-8",
    )
    (root / "backend" / "gestionnaire_mdp" / "urls.py").write_text(
        'from django.contrib import admin\nfrom django.urls import include, path\nurlpatterns = [path("admin/", admin.site.urls), path("api/", include("api.urls"))]\n',
        encoding="utf-8",
    )
    (root / "backend" / "api" / "models.py").write_text(
        'from django.db import models\nclass Category(models.Model):\n    name = models.CharField(max_length=120, unique=True)\nclass PasswordEntry(models.Model):\n    title = models.CharField(max_length=120)\n    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)\nclass SecretBundle(models.Model):\n    label = models.CharField(max_length=120, default="bundle")\n',
        encoding="utf-8",
    )
    (root / "backend" / "api" / "views.py").write_text(
        'from rest_framework import viewsets\nfrom rest_framework.permissions import IsAuthenticated\nfrom rest_framework.response import Response\nfrom rest_framework.views import APIView\nfrom .models import Category, PasswordEntry, SecretBundle\nclass LoginView(APIView):\n    permission_classes = []\n    def post(self, request):\n        return Response({"ok": True})\nclass WhoAmIView(APIView):\n    permission_classes = [IsAuthenticated]\n    def get(self, request):\n        return Response({"ok": True})\nclass CategoryViewSet(viewsets.ModelViewSet):\n    permission_classes = [IsAuthenticated]\n    queryset = Category.objects.all()\nclass PasswordEntryViewSet(viewsets.ModelViewSet):\n    permission_classes = [IsAuthenticated]\n    queryset = PasswordEntry.objects.all()\nclass SecretBundleViewSet(viewsets.ModelViewSet):\n    permission_classes = [IsAuthenticated]\n    queryset = SecretBundle.objects.all()\n',
        encoding="utf-8",
    )
    (root / "backend" / "api" / "urls.py").write_text(
        'from django.urls import path, include\nfrom rest_framework.routers import DefaultRouter\nfrom .views import CategoryViewSet, LoginView, PasswordEntryViewSet, SecretBundleViewSet, WhoAmIView\nrouter = DefaultRouter()\nrouter.register("categories", CategoryViewSet, basename="category")\nrouter.register("passwords", PasswordEntryViewSet, basename="password")\nrouter.register("secrets", SecretBundleViewSet, basename="secret")\nurlpatterns = [path("auth/login/", LoginView.as_view()), path("auth/whoami/", WhoAmIView.as_view()), path("", include(router.urls))]\n',
        encoding="utf-8",
    )
    (root / "frontend" / "src" / "main.jsx").write_text(
        'import React from "react";\nimport AppRoutes from "./routes/AppRoutes.jsx";\nexport default function Main() { return <AppRoutes />; }\n',
        encoding="utf-8",
    )
    (root / "frontend" / "src" / "routes" / "AppRoutes.jsx").write_text(
        'import React from "react";\nimport { BrowserRouter, Link, Route, Routes } from "react-router-dom";\nimport { listCategories, listPasswords, whoAmI } from "../services/http.js";\nexport default function AppRoutes() { whoAmI(); listCategories(); listPasswords(); return <BrowserRouter><nav><Link to="/vault">Coffre</Link><Link to="/vault/categories">Catégories</Link></nav><Routes><Route path="/login" element={<div>Login</div>} /><Route path="/vault" element={<div>Vault</div>} /><Route path="/vault/new" element={<div>New</div>} /><Route path="/vault/categories" element={<div>Categories</div>} /></Routes></BrowserRouter>; }\n',
        encoding="utf-8",
    )
    (root / "frontend" / "src" / "services" / "http.js").write_text(
        'export function whoAmI() { return fetch("/api/auth/whoami/"); }\nexport function listCategories() { return fetch("/api/categories/"); }\nexport function listPasswords() { return fetch("/api/passwords/"); }\n',
        encoding="utf-8",
    )


def test_django_react_generalization_env_parsing_and_contextual_values(tmp_path: Path) -> None:
    _create_generalized_django_react_project(tmp_path)
    _project, _profile, knowledge = _build_knowledge(tmp_path)

    variables = {item.name: item for item in knowledge.environment_variables.variables}
    assert variables["DEV_API_PORT"].default_value == "8002"
    assert variables["DEV_API_PORT"].comment == "8001 + N"
    assert variables["DEV_DB_PORT"].default_value == "5433"
    assert variables["DEV_VITE_PORT"].default_value == "5174"
    assert any(value.environment == "prod" and value.value == "mdp.mon-site.ca" for value in variables["APP_HOST"].values)
    assert any(value.environment == "dev" and value.value == "localhost" for value in variables["APP_HOST"].values)
    assert variables["NAME"].default_value == "Gestionnaire MDP"
    assert variables["LABEL_HASH"].default_value == "abc#def"
    assert variables["EMPTY"].default_value == ""
    assert variables["VALUE"].default_value == "texte avec espaces"


def test_django_react_generalization_make_parameters_and_aliases(tmp_path: Path) -> None:
    _create_generalized_django_react_project(tmp_path)
    result = ManualPreparationService().prepare(tmp_path, clean=True, mode="both")
    data = json.loads(result.knowledge_file.read_text(encoding="utf-8"))

    commands = {item["name"]: item for item in data["operational_commands"]["commands"]}
    public_commands = {item["name"]: item for item in data["commands"]}

    assert commands["test"]["prerequisites"] == ["test-backend", "test-frontend"]
    assert commands["start"]["prerequisites"] == ["up"]
    assert commands["stop"]["prerequisites"] == ["down"]
    assert commands["logs"]["parameters"][0]["name"] == "SERVICE"
    assert commands["rebuild"]["parameters"][0]["name"] == "SERVICE"
    assert commands["tree"]["parameters"][0]["name"] == "TREE_IGNORE"
    assert commands["tree"]["parameters"][0]["required"] is False
    assert "COMPOSE" not in {item["name"] for item in commands["logs"]["parameters"]}
    assert "MAKE" not in {item["name"] for item in commands["restore"]["parameters"]}
    assert "MAKEFILE_LIST" not in {item["name"] for item in commands["help"]["parameters"]}
    assert commands["backup-dir"]["visibility"] == "internal"
    assert "backup-dir" not in public_commands


def test_django_react_generalization_workflows_capabilities_and_security(tmp_path: Path) -> None:
    _create_generalized_django_react_project(tmp_path)
    result = ManualPreparationService().prepare(tmp_path, clean=True, mode="both")
    data = json.loads(result.knowledge_file.read_text(encoding="utf-8"))

    workflow_ids = {item["identifier"] for item in data["workflows"]}
    run_tests = next(item for item in data["workflows"] if item["identifier"] == "run-tests")
    create_admin = next(item for item in data["workflows"] if item["identifier"] == "create-admin")
    missing_ids = {item["identifier"] for item in data["missing_information"]}
    endpoints = {(item["environment"], item["service"], item["url"]) for item in data["service_endpoints"]["endpoints"]}

    assert workflow_ids >= {"run-tests", "create-admin", "open-django-admin", "open-frontend"}
    assert run_tests["commands"] == ["make test"]
    assert run_tests["operational_status"] == "operational"
    assert create_admin["commands"] == ["make createsuperuser"]
    assert "BACKEND-TEST-COMMAND-MISSING" not in missing_ids
    assert "VISIBILITY-VALUES-MISSING" not in missing_ids
    assert any(cap["label"].startswith("Consulter") and "catég" in cap["label"].casefold() for cap in data["capabilities"]["capabilities"])
    assert any(cap["label"].startswith("Créer") and "mots de passe" in cap["label"].casefold() for cap in data["capabilities"]["capabilities"])
    assert ("prod", "frontend", "https://mdp.mon-site.ca") in endpoints
    assert ("prod", "backend", "https://mdp.mon-site.ca/api/") in endpoints
    assert not any("${APP_HOST}" in url for _, _, url in endpoints)
    assert any(risk["identifier"] == "ADMIN-CREDENTIAL-FALLBACK-DETECTED" for risk in data["security"]["risks"])
    assert "changeme" not in json.dumps(data["security"], ensure_ascii=False)


def test_django_react_generalization_recursive_react_and_django_detection(tmp_path: Path) -> None:
    _create_generalized_django_react_project(tmp_path)
    _project, _profile, knowledge = _build_knowledge(tmp_path)

    assert knowledge.django.settings_files == ["backend/gestionnaire_mdp/settings.py"]
    assert knowledge.django.settings_module == "gestionnaire_mdp.settings"
    assert knowledge.django.urlconf_module == "gestionnaire_mdp.urls"
    assert knowledge.django.admin_enabled is True
    assert any(route.full_path == "/api/auth/login/" for route in knowledge.django.resolved_routes)
    assert any(endpoint.path == "/api/categories/" for endpoint in knowledge.django.endpoints)
    assert any(path.endswith("frontend/src/routes/AppRoutes.jsx") for path in knowledge.react.source_paths)
    assert any(path.endswith("frontend/src/services/http.js") for path in knowledge.react.source_paths)
    assert "frontend/src/api.js" not in knowledge.react.source_paths
    assert knowledge.react.crypto.detected is False
    assert any(route == "/vault" for route in knowledge.react.routes)
    assert any(call == "GET /api/categories/" for call in knowledge.react.api_calls)


def test_django_react_invalid_frontend_endpoint_is_not_operational(tmp_path: Path) -> None:
    _create_generalized_django_react_project(tmp_path)
    compose_path = tmp_path / "docker-compose.dev.yml"
    compose_path.write_text(compose_path.read_text(encoding="utf-8").replace('${DEV_VITE_PORT:-5174}', '${DEV_VITE_PORT'), encoding="utf-8")

    result = ManualPreparationService().prepare(tmp_path, clean=True, mode="both")
    data = json.loads(result.knowledge_file.read_text(encoding="utf-8"))

    frontend_endpoints = [item for item in data["service_endpoints"]["endpoints"] if item["service"] == "frontend" and item["environment"] == "dev"]
    workflow_ids = {item["identifier"] for item in data["workflows"]}
    limitation_ids = {item["identifier"] for item in data["limitations"]["items"]}

    assert frontend_endpoints[0]["validity"] == "invalid"
    assert "open-frontend" not in workflow_ids
    assert "INVALID-SERVICE-ENDPOINTS" in limitation_ids

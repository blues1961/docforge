from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path

from docforge.models import Project


@dataclass(slots=True)
class ApiRoute:
    path: str
    source: str
    name: str | None = None
    view: str | None = None
    kind: str = "path"
    methods: list[str] = field(default_factory=list)


@dataclass(slots=True)
class RouterRegistration:
    prefix: str
    viewset: str
    source: str
    basename: str | None = None


@dataclass(slots=True)
class ApiFacts:
    route_files: list[str] = field(default_factory=list)
    routes: list[ApiRoute] = field(default_factory=list)
    router_registrations: list[RouterRegistration] = field(
        default_factory=list
    )
    included_modules: list[str] = field(default_factory=list)


class ApiAnalyzer:
    def analyze(self, project: Project) -> ApiFacts:
        facts = ApiFacts()

        url_files = sorted(
            relative_path
            for relative_path in project.files
            if Path(relative_path).name == "urls.py"
        )

        for relative_path in url_files:
            path = project.root / relative_path
            self._analyze_url_file(
                path=path,
                relative_path=relative_path,
                facts=facts,
            )

        facts.route_files = url_files
        facts.routes.sort(
            key=lambda route: (
                route.path,
                route.name or "",
                route.source,
            )
        )
        facts.router_registrations.sort(
            key=lambda registration: (
                registration.prefix,
                registration.viewset,
            )
        )
        facts.included_modules = sorted(
            set(facts.included_modules)
        )

        self._infer_methods(project, facts)

        return facts

    def _analyze_url_file(
        self,
        *,
        path: Path,
        relative_path: str,
        facts: ApiFacts,
    ) -> None:
        try:
            source = path.read_text(
                encoding="utf-8",
                errors="ignore",
            )
            tree = ast.parse(source)
        except (OSError, SyntaxError):
            return

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue

            function_name = self._call_name(node.func)

            if function_name in {"path", "re_path"}:
                route = self._parse_path_call(
                    node=node,
                    source=relative_path,
                    kind=function_name,
                    facts=facts,
                )

                if route is not None:
                    facts.routes.append(route)

            elif function_name.endswith(".register"):
                registration = self._parse_router_register(
                    node=node,
                    source=relative_path,
                )

                if registration is not None:
                    facts.router_registrations.append(
                        registration
                    )

    def _parse_path_call(
        self,
        *,
        node: ast.Call,
        source: str,
        kind: str,
        facts: ApiFacts,
    ) -> ApiRoute | None:
        if not node.args:
            return None

        route_path = self._literal_string(node.args[0])

        if route_path is None:
            return None

        view = (
            self._expression_name(node.args[1])
            if len(node.args) > 1
            else None
        )

        route_name = self._keyword_string(node, "name")

        if view and view.startswith("include("):
            module = view.removeprefix("include(").removesuffix(")")

            if module:
                facts.included_modules.append(module)

        return ApiRoute(
            path=self._normalize_path(route_path),
            source=source,
            name=route_name,
            view=view,
            kind=kind,
        )

    def _parse_router_register(
        self,
        *,
        node: ast.Call,
        source: str,
    ) -> RouterRegistration | None:
        if len(node.args) < 2:
            return None

        prefix = self._literal_string(node.args[0])
        viewset = self._expression_name(node.args[1])

        if prefix is None or viewset is None:
            return None

        basename = self._keyword_string(node, "basename")

        return RouterRegistration(
            prefix=self._normalize_path(prefix),
            viewset=viewset,
            source=source,
            basename=basename,
        )

    def _infer_methods(
        self,
        project: Project,
        facts: ApiFacts,
    ) -> None:
        class_methods = self._collect_class_methods(project)

        for registration in facts.router_registrations:
            class_name = registration.viewset.split(".")[-1]
            methods = class_methods.get(class_name, set())

            registration_methods = self._viewset_http_methods(
                methods
            )

            facts.routes.extend(
                self._routes_from_router_registration(
                    registration,
                    registration_methods,
                )
            )

        for route in facts.routes:
            if route.methods:
                continue

            view_name = self._clean_view_name(route.view)

            if not view_name:
                continue

            methods = class_methods.get(view_name, set())
            route.methods = self._class_http_methods(methods)

    def _collect_class_methods(
        self,
        project: Project,
    ) -> dict[str, set[str]]:
        result: dict[str, set[str]] = {}

        python_files = [
            relative_path
            for relative_path in project.files
            if relative_path.endswith(".py")
            and (
                "/views" in relative_path
                or relative_path.endswith("views.py")
                or relative_path.endswith("viewsets.py")
            )
        ]

        for relative_path in python_files:
            path = project.root / relative_path

            try:
                tree = ast.parse(
                    path.read_text(
                        encoding="utf-8",
                        errors="ignore",
                    )
                )
            except (OSError, SyntaxError):
                continue

            for node in tree.body:
                if not isinstance(node, ast.ClassDef):
                    continue

                methods = {
                    item.name
                    for item in node.body
                    if isinstance(
                        item,
                        (ast.FunctionDef, ast.AsyncFunctionDef),
                    )
                }

                result[node.name] = methods

        return result

    @staticmethod
    def _routes_from_router_registration(
        registration: RouterRegistration,
        methods: list[str],
    ) -> list[ApiRoute]:
        base_path = registration.prefix.strip("/")
        list_methods = [
            method
            for method in methods
            if method in {"GET", "POST"}
        ]
        detail_methods = [
            method
            for method in methods
            if method in {
                "GET",
                "PUT",
                "PATCH",
                "DELETE",
            }
        ]

        routes: list[ApiRoute] = []

        if list_methods:
            routes.append(
                ApiRoute(
                    path=f"/{base_path}/",
                    source=registration.source,
                    name=registration.basename,
                    view=registration.viewset,
                    kind="router-list",
                    methods=list_methods,
                )
            )

        if detail_methods:
            routes.append(
                ApiRoute(
                    path=f"/{base_path}/{{id}}/",
                    source=registration.source,
                    name=registration.basename,
                    view=registration.viewset,
                    kind="router-detail",
                    methods=detail_methods,
                )
            )

        return routes

    @staticmethod
    def _viewset_http_methods(
        methods: set[str],
    ) -> list[str]:
        mapping = {
            "list": "GET",
            "retrieve": "GET",
            "create": "POST",
            "update": "PUT",
            "partial_update": "PATCH",
            "destroy": "DELETE",
        }

        inferred = [
            http_method
            for method_name, http_method in mapping.items()
            if method_name in methods
        ]

        if inferred:
            return list(dict.fromkeys(inferred))

        # Les ModelViewSet hérités peuvent ne redéfinir aucune méthode.
        return ["GET", "POST", "PUT", "PATCH", "DELETE"]

    @staticmethod
    def _class_http_methods(
        methods: set[str],
    ) -> list[str]:
        mapping = {
            "get": "GET",
            "post": "POST",
            "put": "PUT",
            "patch": "PATCH",
            "delete": "DELETE",
        }

        return [
            http_method
            for method_name, http_method in mapping.items()
            if method_name in methods
        ]

    @staticmethod
    def _clean_view_name(view: str | None) -> str | None:
        if not view:
            return None

        value = view

        for suffix in (
            ".as_view()",
            ".as_view",
        ):
            value = value.removesuffix(suffix)

        if "(" in value:
            value = value.split("(", 1)[0]

        return value.split(".")[-1] or None

    @staticmethod
    def _keyword_string(
        node: ast.Call,
        keyword_name: str,
    ) -> str | None:
        for keyword in node.keywords:
            if keyword.arg == keyword_name:
                return ApiAnalyzer._literal_string(
                    keyword.value
                )

        return None

    @staticmethod
    def _literal_string(node: ast.AST) -> str | None:
        if isinstance(node, ast.Constant) and isinstance(
            node.value,
            str,
        ):
            return node.value

        return None

    @classmethod
    def _expression_name(cls, node: ast.AST) -> str | None:
        if isinstance(node, ast.Name):
            return node.id

        if isinstance(node, ast.Attribute):
            parent = cls._expression_name(node.value)

            if parent:
                return f"{parent}.{node.attr}"

            return node.attr

        if isinstance(node, ast.Call):
            function_name = cls._call_name(node.func)

            if function_name == "include" and node.args:
                value = cls._expression_name(node.args[0])

                if value is None:
                    value = cls._literal_string(node.args[0])

                return f"include({value or 'inconnu'})"

            arguments = ", ".join(
                filter(
                    None,
                    (
                        cls._expression_name(argument)
                        or cls._literal_string(argument)
                        for argument in node.args
                    ),
                )
            )

            return f"{function_name}({arguments})"

        if isinstance(node, ast.Constant):
            return str(node.value)

        return None

    @classmethod
    def _call_name(cls, node: ast.AST) -> str:
        return cls._expression_name(node) or ""

    @staticmethod
    def _normalize_path(value: str) -> str:
        cleaned = value.strip()

        if not cleaned:
            return "/"

        cleaned = cleaned.replace(
            "<int:pk>",
            "{id}",
        ).replace(
            "<uuid:pk>",
            "{id}",
        ).replace(
            "<str:pk>",
            "{id}",
        )

        cleaned = cleaned.replace("^", "").replace("$", "")

        if not cleaned.startswith("/"):
            cleaned = "/" + cleaned

        return cleaned

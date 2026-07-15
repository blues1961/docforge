from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path

from project_assistant.models import Project


@dataclass(slots=True)
class CliParameterFacts:
    name: str
    kind: str
    type_annotation: str | None = None
    required: bool = True
    default: str | None = None
    flags: list[str] = field(default_factory=list)
    help: str | None = None


@dataclass(slots=True)
class CliCommandFacts:
    name: str
    function_name: str
    module: str
    group: str | None = None
    help: str | None = None
    parameters: list[CliParameterFacts] = field(
        default_factory=list
    )


@dataclass(slots=True)
class CliFacts:
    framework: str | None = None
    entry_points: dict[str, str] = field(default_factory=dict)
    command_files: list[str] = field(default_factory=list)
    commands: list[CliCommandFacts] = field(default_factory=list)

    @property
    def command_count(self) -> int:
        return len(self.commands)


class CliAnalyzer:
    def analyze(
        self,
        project: Project,
        *,
        entry_points: dict[str, str] | None = None,
    ) -> CliFacts:
        commands: list[CliCommandFacts] = []
        command_files: list[str] = []

        for path in self._python_files(project.root):
            try:
                source = path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )
                tree = ast.parse(source, filename=str(path))
            except (OSError, SyntaxError):
                continue

            file_commands = self._commands_from_tree(
                tree,
                path=path,
                root=project.root,
            )

            if file_commands:
                command_files.append(
                    path.relative_to(project.root).as_posix()
                )
                commands.extend(file_commands)

        commands.sort(
            key=lambda item: (
                item.group or "",
                item.name,
                item.module,
            )
        )

        return CliFacts(
            framework="Typer" if commands else None,
            entry_points=dict(
                sorted((entry_points or {}).items())
            ),
            command_files=sorted(set(command_files)),
            commands=commands,
        )

    @staticmethod
    def _python_files(root: Path) -> list[Path]:
        package = root / "project_assistant"

        if not package.is_dir():
            return []

        return sorted(
            path
            for path in package.rglob("*.py")
            if "__pycache__" not in path.parts
        )

    def _commands_from_tree(
        self,
        tree: ast.AST,
        *,
        path: Path,
        root: Path,
    ) -> list[CliCommandFacts]:
        results: list[CliCommandFacts] = []
        module = path.relative_to(root).with_suffix(
            ""
        ).as_posix().replace("/", ".")

        for node in ast.walk(tree):
            if not isinstance(
                node,
                (ast.FunctionDef, ast.AsyncFunctionDef),
            ):
                continue

            command_decorator = self._command_decorator(
                node.decorator_list
            )

            if command_decorator is None:
                continue

            owner, explicit_name = command_decorator
            command_name = (
                explicit_name
                or node.name.replace("_", "-")
            )

            group = None if owner == "app" else owner

            results.append(
                CliCommandFacts(
                    name=command_name,
                    function_name=node.name,
                    module=module,
                    group=group,
                    help=self._first_docstring_line(node),
                    parameters=self._parameters(node),
                )
            )

        return results

    def _command_decorator(
        self,
        decorators: list[ast.expr],
    ) -> tuple[str, str | None] | None:
        for decorator in decorators:
            call = (
                decorator
                if isinstance(decorator, ast.Call)
                else None
            )
            target = call.func if call else decorator

            if not isinstance(target, ast.Attribute):
                continue

            if target.attr != "command":
                continue

            owner = self._expression_name(target.value)

            if not owner:
                continue

            explicit_name = None

            if call and call.args:
                explicit_name = self._literal_string(
                    call.args[0]
                )

            if call:
                for keyword in call.keywords:
                    if keyword.arg == "name":
                        explicit_name = self._literal_string(
                            keyword.value
                        )

            return owner, explicit_name

        return None

    def _parameters(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
    ) -> list[CliParameterFacts]:
        positional = [
            *node.args.posonlyargs,
            *node.args.args,
        ]
        defaults = [
            None
        ] * (len(positional) - len(node.args.defaults)) + list(
            node.args.defaults
        )

        results: list[CliParameterFacts] = []

        for argument, default in zip(
            positional,
            defaults,
            strict=True,
        ):
            if argument.arg in {"self", "cls"}:
                continue

            results.append(
                self._parameter(
                    argument,
                    default,
                )
            )

        for argument, default in zip(
            node.args.kwonlyargs,
            node.args.kw_defaults,
            strict=True,
        ):
            results.append(
                self._parameter(
                    argument,
                    default,
                )
            )

        return results

    def _parameter(
        self,
        argument: ast.arg,
        default: ast.expr | None,
    ) -> CliParameterFacts:
        annotation = (
            ast.unparse(argument.annotation)
            if argument.annotation is not None
            else None
        )

        kind = "parameter"
        required = default is None
        default_value = None
        flags: list[str] = []
        help_text = None

        if isinstance(default, ast.Call):
            callable_name = self._expression_name(
                default.func
            )

            if callable_name.endswith(".Argument"):
                kind = "argument"
            elif callable_name.endswith(".Option"):
                kind = "option"

            if kind in {"argument", "option"}:
                if default.args:
                    first = default.args[0]

                    if self._is_required_marker(first):
                        required = True
                        default_value = None
                    else:
                        default_value = self._safe_unparse(
                            first
                        )
                        required = False

                for value in default.args[1:]:
                    flag = self._literal_string(value)

                    if flag:
                        flags.append(flag)

                for keyword in default.keywords:
                    if keyword.arg == "help":
                        help_text = self._literal_string(
                            keyword.value
                        )
                    elif keyword.arg in {
                        "show_default",
                        "exists",
                    }:
                        continue

        elif default is not None:
            default_value = self._safe_unparse(default)
            required = False

        return CliParameterFacts(
            name=argument.arg,
            kind=kind,
            type_annotation=annotation,
            required=required,
            default=default_value,
            flags=flags,
            help=help_text,
        )

    @staticmethod
    def _first_docstring_line(
        node: ast.FunctionDef | ast.AsyncFunctionDef,
    ) -> str | None:
        docstring = ast.get_docstring(node)

        if not docstring:
            return None

        return docstring.strip().splitlines()[0].strip()

    @staticmethod
    def _is_required_marker(node: ast.expr) -> bool:
        if isinstance(node, ast.Constant):
            return node.value is Ellipsis

        if isinstance(node, ast.Name):
            return node.id == "Ellipsis"

        return False

    @staticmethod
    def _literal_string(
        node: ast.expr,
    ) -> str | None:
        if (
            isinstance(node, ast.Constant)
            and isinstance(node.value, str)
        ):
            return node.value

        return None

    @staticmethod
    def _safe_unparse(
        node: ast.expr,
    ) -> str:
        try:
            return ast.unparse(node)
        except Exception:
            return "<expression>"

    @staticmethod
    def _expression_name(
        node: ast.expr,
    ) -> str:
        if isinstance(node, ast.Name):
            return node.id

        if isinstance(node, ast.Attribute):
            prefix = CliAnalyzer._expression_name(
                node.value
            )

            if prefix:
                return f"{prefix}.{node.attr}"

            return node.attr

        return ""

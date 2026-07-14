def test_cli_module_imports_successfully() -> None:
    from project_assistant.cli import app

    assert app is not None

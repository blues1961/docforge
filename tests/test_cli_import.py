def test_cli_module_imports_successfully() -> None:
    from docforge.cli import app

    assert app is not None

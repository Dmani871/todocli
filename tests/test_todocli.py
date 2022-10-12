"""Tests for `todocli` package."""

from typer.testing import CliRunner

from todocli import __app_name__, __version__, cli

runner = CliRunner()


def test_creation():
    """Tests app creation."""
    result = runner.invoke(cli.app)
    assert result.exit_code == 0


def test_version():
    """Tests app shows version."""
    result = runner.invoke(cli.app, ["--version"])
    assert result.exit_code == 0
    assert f"{__app_name__} v{__version__}\n" in result.stdout


def test_version_short_opt():
    """Tests app shows version shorthand."""
    result = runner.invoke(cli.app, ["-v"])
    assert result.exit_code == 0
    assert f"{__app_name__} v{__version__}\n" in result.stdout

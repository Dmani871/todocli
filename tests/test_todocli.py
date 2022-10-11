"""Tests for `todocli` package."""

from typer.testing import CliRunner

from todocli import cli

runner = CliRunner()


def test_creation():
    """Tests app creation."""
    result = runner.invoke(cli.app)
    assert result.exit_code == 0

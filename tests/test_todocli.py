"""Tests for `todocli` package."""

from todocli import cli
from typer.testing import CliRunner

runner = CliRunner()

def test_creation():
    """Tests app creation."""
    result = runner.invoke(cli.app)
    assert result.exit_code == 0
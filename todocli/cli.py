"""This module provides the To-Do CLI."""
from pathlib import Path
from typing import Optional

import typer

from todocli import __app_name__, __version__, config
from todocli.return_codes import Code

app = typer.Typer()


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()


@app.command()
def init(
    db_path: Path = typer.Option(
        config.DEFAULT_DB_FILE_PATH,
        "--db-path",
        "-db",
        prompt="to-do database location?",
    ),
) -> None:
    """Initialize the to-do database."""
    app_init_error = config.init_app(db_path)
    if app_init_error != Code.SUCCESS:
        typer.secho(
            f'Creating config file failed with "{app_init_error.value}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    else:
        typer.secho(
            f'The to-do database is "{db_path}"',
            fg=typer.colors.GREEN,
        )


def get_todoer():
    pass


@app.command()
def add(
    description: str = typer.Argument(...),
    priority: int = typer.Option(2, min=1, max=3),
    due: str = typer.Option(None),
) -> None:
    toder = get_todoer()
    todo, error = toder.add(description, priority, due)
    if error != Code.SUCCESS:
        typer.secho(
            f'Adding to-do failed with "{error.value}"', fg=typer.colors.RED
        )
        raise typer.Exit(1)

    typer.secho(
        f"""to-do: "{todo['Description']}" was added """
        f"""with priority: {priority}""",
        fg=typer.colors.GREEN,
    )


@app.command(name="complete")
def set_done(todo_id: int = typer.Argument(...)) -> None:
    toder = get_todoer()
    todo, error = toder.set_done(todo_id)
    if error != Code.SUCCESS:
        typer.secho(
            f'Completing to-do failed with "{error.value}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    typer.secho(
        f"""to-do: "{todo['Description']}" was completed """,
        fg=typer.colors.GREEN,
    )


@app.command()
def remove(todo_id: int = typer.Argument(...)) -> None:
    toder = get_todoer()
    todo, error = toder.remove(todo_id)
    if error != Code.SUCCESS:
        typer.secho(
            f'Removing to-do failed with "{error.value}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    typer.secho(
        f"""to-do: "{todo['Description']}" was removed """,
        fg=typer.colors.GREEN,
    )


@app.command()
def clear() -> None:
    toder = get_todoer()
    toder.remove_all()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "-v",
        "--version",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    return

"""This module provides the To-Do CLI."""
from pathlib import Path
from typing import Optional

import typer
from prettytable import PrettyTable

from todocli import __app_name__, __version__, config
from todocli.return_codes import Code
from todocli.todo_manager import TodoManager

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
    db_path = config.get_db_path()
    if db_path == Code.CONFIG_READ_ERROR:
        typer.secho(
            'Config file not found. Please, run "todocli init"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    if not db_path.exists():
        typer.secho(
            'DB path does not exist. Please, run "todocli init"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    return TodoManager(db_path)


@app.command()
def add(
    description: str = typer.Argument(...),
    priority: int = typer.Option(2, min=1, max=3),
    due: str = typer.Option(None),
) -> None:
    """Adds a todo to the to-do database."""
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
    """Set a todo as done in the to-do database using its ID."""
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
    """Removes a todo from the to-do database using its ID."""
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
    """Clears all todos from the to-do database using its ID."""
    toder = get_todoer()
    todo, error = toder.remove_all()
    if error != Code.SUCCESS:
        typer.secho(
            "Failed to clear to-do database",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    typer.secho(
        """Cleared all todos""",
        fg=typer.colors.GREEN,
    )


@app.command()
def list(sort_by: str = typer.Option(None)) -> None:
    """Clears a todo from the to-do database using its ID."""
    toder = get_todoer()
    todos, error = toder.read_todos()
    if error != Code.SUCCESS:
        typer.secho(
            f'Listing to-do failed with "{ error.value}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    if len(todos) == 0:
        typer.secho(
            "There are no tasks in the to-do list yet", fg=typer.colors.RED
        )
        raise typer.Exit(1)

    table = PrettyTable()
    table.field_names = ["Description", "Priority", "Due", "Done"]
    if sort_by and sort_by not in table.field_names:
        typer.secho(
            f"'{sort_by}' is invalid try:{','.join(table.field_names)} ",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    table.sortby = sort_by
    for todo in todos:
        table.add_row(todo.values())
    typer.secho(
        table.get_string(),
        fg=typer.colors.BLUE,
    )


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

import logging
import subprocess
import sys
from os import isatty
from typing import Sequence

import typer
from vimania.db.dal import DAL, Todo, TodoStatus
from vimania.environment import config
from vimania.todos.model import Todos

_log = logging.getLogger("vimania-plugin.todos.cli")

if not _log.handlers:  # avoid adding multiple handler via re-sourcing
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)-15s %(levelname)s %(name)s %(funcName)s:%(lineno)d %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    _log.addHandler(handler)


HELP_DESC = """
awesome todo manager for the command line
"""

app = typer.Typer(help=HELP_DESC)


def _update_tags(
    ids: Sequence[int],
    tags: Sequence[str] = None,
    tags_not: Sequence[str] = None,
    force: bool = False,
):
    todos = Todos(fts_query="").todos
    if tags is None:
        tags = ()
    if tags_not is None:
        tags_not = ()

    with DAL(env_config=config) as dal:
        for id in ids:
            todo = todos[id - 1]
            if force:
                new_tags = set(tags)
            else:
                new_tags = (set(todo.split_tags) | set(tags)) - set(tags_not)
            new_tags = sorted(list(new_tags))
            new_tags = f",{','.join(new_tags)},"
            _log.debug(f"{new_tags=}")
            todo.tags = new_tags
            dal.update_bookmark(todo)


def show_todos(todos: Sequence[Todo], err: bool = True):
    for i, todo in enumerate(todos):
        offset = len(str(i)) + 2

        if todo.flags == TodoStatus.OPEN:
            status = "open"
        elif todo.flags == TodoStatus.PROGRESS:
            status = "in progress"
        elif todo.flags == TodoStatus.DONE:
            status = "done"

        id_formatted = typer.style(
            f"{todo.id}", fg=typer.colors.BRIGHT_BLACK, bold=False
        )
        metadata_formatted = typer.style(
            f"{i}. {todo.todo}", fg=typer.colors.GREEN, bold=True
        )
        typer.echo(f"{metadata_formatted} [{id_formatted}]", err=err)

        typer.secho(f"{' ':>{offset}}Status: {status}", fg=typer.colors.YELLOW, err=err)
        if todo.desc != "":
            typer.secho(f"{' ':>{offset}}{todo.desc}", fg=None, err=err)
        typer.secho(
            f"{' ':>{offset}}{', '.join((tag for tag in todo.split_tags if tag != ''))}",
            fg=typer.colors.BLUE,
            err=err,
        )
        typer.secho("", err=err)


def process(todos: Sequence[Todo]):
    help_text = """
        <n1> <n2>:      opens selection in browser
        p <n1> <n2>:    print id-list of selection
        p:              print all ids
        h:              help
    """
    typer.secho(f"Selection: ", fg=typer.colors.GREEN, err=True)
    selection = [x for x in input().split()]

    try:
        # open in browser if no command letter
        try:
            selection = [int(x) for x in selection]
            for i in selection:
                typer.secho(f"Open in vim: {todos[i].path}")
                subprocess.run(["vim", todos[i].path])
            return
        except ValueError as e:
            pass

        # with command letter
        cmd = str(selection[0])
        selection = sorted([int(x) for x in selection[1:]])
        ids = list()

        if cmd == "p":
            if len(selection) == 0:
                ids = [todo.id for todo in todos]
            else:
                for i in selection:
                    ids.append(todos[i].id)
            typer.echo(",".join((str(x) for x in ids)), err=False)  # stdout for piping

        elif cmd == "h":
            typer.echo(help_text, err=True)
        else:
            typer.secho(f"-E- Invalid command {cmd}\n", err=True)
            typer.echo(help_text, err=True)
    except IndexError as e:
        typer.secho(
            f"-E- Selection {selection} out of range.",
            err=True,
            fg=typer.colors.RED,
        )
        raise typer.Abort()


@app.command()
def search(
    # ctx: typer.Context,
    fts_query: str = typer.Argument("", help="FTS query"),
    tags_exact: str = typer.Option(
        None, "-e", "--exact", help="match exact, comma separated list"
    ),
    tags_all: str = typer.Option(
        None, "-t", "--tags", help="match all, comma separated list"
    ),
    tags_any: str = typer.Option(
        None, "-T", "--Tags", help="match any, comma separated list"
    ),
    tags_all_not: str = typer.Option(
        None, "-n", "--ntags", help="not match all, comma separated list"
    ),
    tags_any_not: str = typer.Option(
        None, "-N", "--Ntags", help="not match any, comma separated list"
    ),
    non_interactive: bool = typer.Option(False, "--np", help="no prompt"),
    order_desc: bool = typer.Option(False, "-o", help="order by age, descending."),
    order_asc: bool = typer.Option(False, "-O", help="order by age, ascending."),
    verbose: bool = typer.Option(False, "-v", "--verbose"),
):
    """
    Searches bookmark database with full text search capabilities (FTS)
    (see: https://www.sqlite.org/fts5.html)

    Title, URL and description are FTS indexed. Tags are not part of FTS.

    Tags must be specified as comma separated list without blanks.
    Correct FTS search syntax: https://www.sqlite.org/fts5.html chapter 3.

    Example:\n
        twtodo search 'security "single-page"'\n
        twtodo search '"https://securit" *'\n
        twtodo search '^security'\n
        twtodo search 'postgres OR sqlite'\n
        twtodo search 'security NOT keycloak'\n
        twtodo search -t tag1,tag2 -n notag1 <searchquery>\n
        twtodo search -e tag1,tag2\n
        twtodo search xxxxx | twtodo update -t x (interactive selection)\n

    \nCommands in interactive mode:\n
        <n1> <n2>:      opens selection in browser\n
        p <n1> <n1>:    prints corresponding id-list of selection\n
        p:              prints all ids\n
        d <n1> <n1>:    delete selection\n

            p <n1> <n2>:    print id-list of selection
            p:              print all ids
            d <n1> <n2>:    delete selection
            h:              help
    """
    if verbose:
        typer.echo(f"Using DB: {config.tw_vimania_db_url}", err=True)

    todos = Todos(fts_query=fts_query).filter(
        tags_all, tags_all_not, tags_any, tags_any_not, tags_exact
    )

    # ordering of results
    if order_desc:
        todos = sorted(todos, key=lambda todo: todo.last_update_ts)
    elif order_asc:
        todos = list(reversed(sorted(todos, key=lambda todo: todo.last_update_ts)))
    else:
        todos = sorted(todos, key=lambda todo: todo.metadata.lower())

    show_todos(todos)
    typer.echo(f"Found: {len(todos)}", err=True)

    if not non_interactive:
        process(todos)


@app.command()
def update(
    # ctx: typer.Context,
    ids: str = typer.Argument(None, help="list of ids, separated by comma, no blanks"),
    tags: str = typer.Option(None, "-t", "--tags", help="add tags to taglist"),
    tags_not: str = typer.Option(None, "-n", "--tags", help="remove tags from taglist"),
    force: bool = typer.Option(
        False, "-f", "--force", help="overwrite taglist with tags"
    ),
    verbose: bool = typer.Option(False, "-v", "--verbose"),
):
    """
    Updates bookmarks with tags, either removes tags, add tags or overwrites entire taglist.

    Gotcha: in order to allow for piped input, ids must be separated by comma with no blanks.

    Example for using piped input:

        twtodo search xxxxx | twtodo update -t <tag>
    """
    if verbose:
        typer.echo(f"Using DB: {config.tw_vimania_db_url}", err=True)
    if tags is not None:
        tags = tags.lower().replace(" ", "").split(",")
    if tags_not is not None:
        tags_not = tags_not.lower().replace(" ", "").split(",")

    # Gotcha: running from IDE looks like pipe
    is_pipe = not isatty(sys.stdin.fileno())
    ids_: Sequence[int] = list()

    if is_pipe:
        ids = sys.stdin.readline()

    try:
        ids = [int(x.strip()) for x in ids.split(",")]
    except ValueError as e:
        typer.secho(f"-E- Wrong input format.", color=typer.colors.RED, err=True)
        raise typer.Abort()

    print(ids)
    _update_tags(ids, tags, tags_not, force=force)


@app.command()
def open(
    # ctx: typer.Context,
    ids: str = typer.Argument(None, help="list of ids, separated by comma, no blanks"),
    verbose: bool = typer.Option(False, "-v", "--verbose"),
):
    """
    Opens bookmarks

    Gotcha: in order to allow for piped input, ids must be separated by comma with no blanks.

    Example for using piped input:

        twtodo search xxxxx | twtodo open
    """
    if verbose:
        typer.echo(f"Using DB: {config.tw_vimania_db_url}", err=True)

    # Gotcha: running from IDE looks like pipe
    is_pipe = not isatty(sys.stdin.fileno())
    ids_: Sequence[int] = list()

    if is_pipe:
        ids = sys.stdin.readline()

    try:
        ids = [int(x.strip()) for x in ids.split(",")]
    except ValueError as e:
        typer.secho(f"-E- Wrong input format.", color=typer.colors.RED, err=True)
        raise typer.Abort()

    print(ids)
    with DAL(env_config=config) as dal:
        for id_ in ids:
            todo = dal.get_bookmark_by_id(id_=id_)
            show_todos((todo,))
            print("open it.")


@app.command()
def show(
    # ctx: typer.Context,
    id_: int = typer.Argument(..., help="id to print"),
    verbose: bool = typer.Option(False, "-v", "--verbose"),
):
    if verbose:
        typer.echo(f"Using DB: {config.tw_vimania_db_url}", err=True)

    # _ = BukuDb(dbfile=config.dbfile).print_rec(index=id_)
    with DAL(env_config=config) as dal:
        todo = dal.get_bookmark_by_id(id_=id_)
        show_todos((todo,))


@app.command()
def tags(
    # ctx: typer.Context,
    tag: str = typer.Argument(
        None,
        help="tag for which related tags should be shown. No input: all tags are printed.",
    ),
    verbose: bool = typer.Option(False, "-v", "--verbose"),
):
    """
    No parameter: Show all tags

    With tag as parameter: Show related tags, i.e. tags which are used in combination with tag.
    """
    if verbose:
        typer.echo(f"Using DB: {config.tw_vimania_db_url}", err=True)

    if tag is not None:
        tag = tag.strip(",").strip().lower()

    with DAL(env_config=config) as dal:
        if tag is None:
            tags = dal.get_all_tags()
        else:
            tags = dal.get_related_tags(tag=tag)
        output = "\n".join(tags)
        typer.echo(f"{output}", err=True)


if __name__ == "__main__":
    _log.debug(config)
    app()

import io

import click


def _make_command(**kwargs):
    @click.command("cli", **kwargs)
    @click.option("--name")
    def cli(name):
        pass

    return cli


def test_exit_code_and_message():
    exc = click.UsageError("Bad usage.")
    assert exc.exit_code == 2
    assert exc.ctx is None
    assert exc.cmd is None
    assert exc.format_message() == "Bad usage."


def test_show_without_ctx_to_file(capsys):
    file = io.StringIO()
    click.UsageError("Bad usage.").show(file=file)
    assert file.getvalue() == "Error: Bad usage.\n"
    assert capsys.readouterr().err == ""


def test_show_with_ctx_to_file(capsys):
    cli = _make_command()
    ctx = click.Context(cli, info_name="cli")
    file = io.StringIO()
    click.UsageError("Bad usage.", ctx=ctx).show(file=file)
    assert file.getvalue() == (
        "Usage: cli [OPTIONS]\nTry 'cli --help' for help.\n\nError: Bad usage.\n"
    )
    assert capsys.readouterr().err == ""


def test_show_hint_uses_longest_help_name():
    cli = _make_command()
    ctx = click.Context(cli, info_name="cli", help_option_names=["-h", "--show-help"])
    file = io.StringIO()
    click.UsageError("Bad usage.", ctx=ctx).show(file=file)
    assert "Try 'cli --show-help' for help.\n" in file.getvalue()


def test_show_no_hint_without_help_option():
    cli = _make_command(add_help_option=False)
    ctx = click.Context(cli, info_name="cli")
    file = io.StringIO()
    click.UsageError("Bad usage.", ctx=ctx).show(file=file)
    assert file.getvalue() == "Usage: cli [OPTIONS]\n\nError: Bad usage.\n"


def test_show_uses_ctx_color():
    cli = _make_command()
    ctx = click.Context(cli, info_name="cli", color=True)
    file = io.StringIO()
    click.UsageError("\x1b[31mred\x1b[0m", ctx=ctx).show(file=file)
    assert file.getvalue().endswith("Error: \x1b[31mred\x1b[0m\n")


def test_raised_from_command(runner):
    @click.command()
    def cli():
        raise click.UsageError("Bad usage.")

    result = runner.invoke(cli)
    assert result.exit_code == 2
    assert result.output == (
        "Usage: cli [OPTIONS]\nTry 'cli --help' for help.\n\nError: Bad usage.\n"
    )

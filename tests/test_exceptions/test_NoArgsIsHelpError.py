import io

import click
from click.exceptions import NoArgsIsHelpError


def _make_command():
    @click.command("cli", no_args_is_help=True)
    @click.option("--name")
    def cli(name):
        """Greet someone."""

    return cli


def test_message_is_help():
    ctx = click.Context(_make_command(), info_name="cli")
    exc = NoArgsIsHelpError(ctx)
    assert isinstance(exc, click.UsageError)
    assert exc.ctx is ctx
    assert exc.format_message() == ctx.get_help()


def test_show_to_file_without_error_prefix(capsys):
    ctx = click.Context(_make_command(), info_name="cli")
    file = io.StringIO()
    NoArgsIsHelpError(ctx).show(file=file)
    assert file.getvalue() == f"{ctx.get_help()}\n"
    assert capsys.readouterr().err == ""


def test_show_defaults_to_stderr(capsys):
    ctx = click.Context(_make_command(), info_name="cli")
    NoArgsIsHelpError(ctx).show()
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == f"{ctx.get_help()}\n"
    assert "Error:" not in captured.err


def test_raised_by_command(runner):
    cli = _make_command()
    result = runner.invoke(cli, [])
    assert result.exit_code == 2
    assert result.output.startswith("Usage: cli [OPTIONS]\n")
    assert "Greet someone." in result.output
    assert "Error:" not in result.output

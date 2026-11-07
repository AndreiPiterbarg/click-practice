import click
from click.exceptions import Exit


def test_default_code():
    exc = Exit()
    assert isinstance(exc, RuntimeError)
    assert exc.exit_code == 0


def test_code():
    assert Exit(3).exit_code == 3


def test_abort_is_runtime_error():
    assert isinstance(click.Abort(), RuntimeError)


def test_exit_from_command(runner):
    @click.command()
    def cli():
        raise Exit(3)

    result = runner.invoke(cli)
    assert result.exit_code == 3
    assert result.output == ""


def test_abort_from_command(runner):
    @click.command()
    def cli():
        raise click.Abort()

    result = runner.invoke(cli)
    assert result.exit_code == 1
    assert result.output == "Aborted!\n"

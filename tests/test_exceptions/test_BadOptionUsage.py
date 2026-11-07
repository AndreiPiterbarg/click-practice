import click


def test_attributes():
    exc = click.BadOptionUsage("--name", "Option requires a value.")
    assert isinstance(exc, click.UsageError)
    assert exc.exit_code == 2
    assert exc.option_name == "--name"
    assert exc.message == "Option requires a value."
    assert exc.format_message() == "Option requires a value."
    assert exc.ctx is None


def test_ctx():
    @click.command()
    def cli():
        pass

    ctx = click.Context(cli)
    exc = click.BadOptionUsage("--name", "Bad.", ctx=ctx)
    assert exc.ctx is ctx
    assert exc.cmd is cli


def test_raised_by_parser(runner):
    @click.command()
    @click.option("--name")
    def cli(name):
        pass

    result = runner.invoke(cli, ["--name"], standalone_mode=False)
    exc = result.exception
    assert isinstance(exc, click.BadOptionUsage)
    assert exc.option_name == "--name"
    assert exc.format_message() == "Option '--name' requires an argument."

    result = runner.invoke(cli, ["--name"])
    assert result.exit_code == 2
    assert "Error: Option '--name' requires an argument.\n" in result.output

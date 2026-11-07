import click


def test_attributes():
    exc = click.BadArgumentUsage("Wrong number of values.")
    assert isinstance(exc, click.UsageError)
    assert exc.exit_code == 2
    assert exc.format_message() == "Wrong number of values."


def test_raised_by_parser(runner):
    @click.command()
    @click.argument("point", nargs=2)
    def cli(point):
        pass

    result = runner.invoke(cli, ["1"], standalone_mode=False)
    exc = result.exception
    assert isinstance(exc, click.BadArgumentUsage)
    assert exc.format_message() == "Argument 'point' takes 2 values."

    result = runner.invoke(cli, ["1"])
    assert result.exit_code == 2
    assert "Error: Argument 'point' takes 2 values.\n" in result.output

import pytest

import click


def test_is_usage_error():
    exc = click.BadParameter("bad")
    assert isinstance(exc, click.UsageError)
    assert exc.exit_code == 2
    assert exc.param is None
    assert exc.param_hint is None


def test_without_param_or_hint():
    exc = click.BadParameter("must be positive")
    assert exc.format_message() == "Invalid value: must be positive"
    assert str(exc) == "must be positive"


def test_with_param_hint_string():
    exc = click.BadParameter("must be positive", param_hint="'--count'")
    assert exc.format_message() == "Invalid value for '--count': must be positive"


@pytest.mark.parametrize(
    "param_hint",
    [
        pytest.param(["--count", "-c"], id="list"),
        pytest.param(("--count", "-c"), id="tuple"),
    ],
)
def test_with_param_hint_sequence(param_hint):
    exc = click.BadParameter("must be positive", param_hint=param_hint)
    assert exc.format_message() == (
        "Invalid value for '--count' / '-c': must be positive"
    )


def test_with_param():
    param = click.Option(["--count", "-c"])
    exc = click.BadParameter("must be positive", param=param)
    assert exc.format_message() == (
        "Invalid value for '--count' / '-c': must be positive"
    )


def test_param_hint_takes_precedence_over_param():
    param = click.Option(["--count"])
    exc = click.BadParameter("must be positive", param=param, param_hint="COUNT")
    assert exc.format_message() == "Invalid value for COUNT: must be positive"


def test_raised_from_callback(runner):
    def validate(ctx, param, value):
        if value < 0:
            raise click.BadParameter("must be positive")
        return value

    @click.command()
    @click.option("--count", type=int, callback=validate)
    def cli(count):
        pass

    result = runner.invoke(cli, ["--count", "-1"])
    assert result.exit_code == 2
    assert "Error: Invalid value for '--count': must be positive\n" in result.output


def test_raised_from_callback_without_param_hint_lookup(runner):
    def validate(ctx, param, value):
        raise click.BadParameter("nope", ctx=ctx, param_hint=["NAME", "--name"])

    @click.command()
    @click.option("--name", callback=validate)
    def cli(name):
        pass

    result = runner.invoke(cli, ["--name", "x"])
    assert result.exit_code == 2
    assert "Error: Invalid value for 'NAME' / '--name': nope\n" in result.output

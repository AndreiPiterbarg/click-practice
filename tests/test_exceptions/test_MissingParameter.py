import pytest

import click


def test_is_bad_parameter():
    exc = click.MissingParameter()
    assert isinstance(exc, click.BadParameter)
    assert exc.exit_code == 2
    assert exc.message == ""
    assert exc.param_type is None


def test_no_info():
    exc = click.MissingParameter(param_type="parameter")
    assert exc.format_message() == "Missing parameter."


@pytest.mark.parametrize(
    ("param_type", "expect"),
    [
        ("argument", "Missing argument 'NAME'."),
        ("option", "Missing option 'NAME'."),
        ("parameter", "Missing parameter 'NAME'."),
        ("value", "Missing value 'NAME'."),
    ],
)
def test_param_type(param_type, expect):
    exc = click.MissingParameter(param_hint="'NAME'", param_type=param_type)
    assert exc.format_message() == expect


def test_param_hint_sequence():
    exc = click.MissingParameter(param_hint=["--name", "-n"], param_type="option")
    assert exc.format_message() == "Missing option '--name' / '-n'."


def test_message_without_param():
    exc = click.MissingParameter(
        "Set it in the config.", param_hint="'--name'", param_type="option"
    )
    assert exc.format_message() == "Missing option '--name'. Set it in the config."


def test_param_type_from_option():
    param = click.Option(["--name", "-n"])
    exc = click.MissingParameter(param=param)
    assert exc.format_message() == "Missing option '--name' / '-n'."


def test_param_type_from_argument():
    param = click.Argument(["name"])
    exc = click.MissingParameter(param=param)
    assert exc.format_message() == "Missing argument 'NAME'."


def test_explicit_param_type_overrides_param():
    param = click.Option(["--name"])
    exc = click.MissingParameter(param=param, param_type="argument")
    assert exc.format_message() == "Missing argument '--name'."


def test_param_hint_overrides_param():
    param = click.Option(["--name"])
    exc = click.MissingParameter(param=param, param_hint="NAME")
    assert exc.format_message() == "Missing option NAME."


def test_type_missing_message():
    param = click.Option(["--color"], type=click.Choice(["red", "blue"]))
    exc = click.MissingParameter(param=param)
    assert exc.format_message() == (
        "Missing option '--color'. Choose from:\n\tred,\n\tblue"
    )


def test_type_missing_message_appended_to_message():
    param = click.Option(["--color"], type=click.Choice(["red", "blue"]))
    exc = click.MissingParameter("Pick one", param=param)
    assert exc.format_message() == (
        "Missing option '--color'. Pick one. Choose from:\n\tred,\n\tblue"
    )


def test_str_with_message():
    exc = click.MissingParameter("Set it in the config.")
    assert str(exc) == "Set it in the config."


def test_str_without_message():
    param = click.Option(["--name"])
    exc = click.MissingParameter(param=param)
    assert str(exc) == "Missing parameter: name"


def test_raised_for_required_option(runner):
    @click.command()
    @click.option("--name", required=True)
    def cli(name):
        pass

    result = runner.invoke(cli, standalone_mode=False)
    exc = result.exception
    assert isinstance(exc, click.MissingParameter)
    assert exc.param is not None
    assert exc.param.name == "name"
    assert str(exc) == "Missing parameter: name"

    result = runner.invoke(cli)
    assert result.exit_code == 2
    assert "Error: Missing option '--name'.\n" in result.output


def test_raised_for_required_argument(runner):
    @click.command()
    @click.argument("name")
    def cli(name):
        pass

    result = runner.invoke(cli)
    assert result.exit_code == 2
    assert "Error: Missing argument 'NAME'.\n" in result.output

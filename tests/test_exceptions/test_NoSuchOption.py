import pytest

import click


def test_is_usage_error():
    exc = click.NoSuchOption("--missing")
    assert isinstance(exc, click.UsageError)
    assert exc.exit_code == 2


def test_default_message():
    exc = click.NoSuchOption("--missing")
    assert exc.option_name == "--missing"
    assert exc.message == "No such option '--missing'."
    assert exc.format_message() == "No such option '--missing'."
    assert str(exc) == "No such option '--missing'."


def test_custom_message():
    exc = click.NoSuchOption("--missing", message="Nope.")
    assert exc.option_name == "--missing"
    assert exc.message == "Nope."
    assert exc.format_message() == "Nope."


@pytest.mark.parametrize("possibilities", [None, []])
def test_no_possibilities(possibilities):
    exc = click.NoSuchOption("--nam", possibilities=possibilities)
    assert exc.possibilities is None
    assert exc.format_message() == "No such option '--nam'."


def test_no_close_matches():
    exc = click.NoSuchOption("--zzz", possibilities=["--name", "--count"])
    assert exc.possibilities == []
    assert exc.format_message() == "No such option '--zzz'."


def test_single_close_match():
    exc = click.NoSuchOption("--nam", possibilities=["--name", "--count"])
    assert exc.possibilities == ["--name"]
    assert exc.format_message() == "No such option '--nam'. Did you mean '--name'?"


def test_multiple_close_matches_sorted():
    exc = click.NoSuchOption("--nam", possibilities=["--names", "--name"])
    assert exc.format_message() == (
        "No such option '--nam'. (Did you mean one of: '--name', '--names'?)"
    )


def test_suggestions_appended_to_custom_message():
    exc = click.NoSuchOption("--nam", message="Unknown.", possibilities=["--name"])
    assert exc.format_message() == "Unknown. Did you mean '--name'?"


def test_raised_by_parser(runner):
    @click.command()
    @click.option("--name")
    def cli(name):
        pass

    result = runner.invoke(cli, ["--nam", "x"], standalone_mode=False)
    exc = result.exception
    assert isinstance(exc, click.NoSuchOption)
    assert exc.option_name == "--nam"
    assert exc.possibilities == ["--name"]
    assert exc.cmd is cli

    result = runner.invoke(cli, ["--nam", "x"])
    assert result.exit_code == 2
    assert "Error: No such option '--nam'. Did you mean '--name'?\n" in result.output

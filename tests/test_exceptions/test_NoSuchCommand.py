import pytest

import click


def _make_group():
    cli = click.Group("cli")

    @cli.command()
    def push():
        pass

    @cli.command()
    def declare():
        pass

    @cli.command()
    def refine():
        pass

    return cli


def test_is_usage_error():
    exc = click.NoSuchCommand("missing")
    assert isinstance(exc, click.UsageError)
    assert exc.exit_code == 2


def test_default_message():
    exc = click.NoSuchCommand("missing")
    assert exc.command_name == "missing"
    assert exc.message == "No such command 'missing'."
    assert exc.format_message() == "No such command 'missing'."
    assert str(exc) == "No such command 'missing'."


def test_default_message_quotes_name():
    exc = click.NoSuchCommand("it's")
    assert exc.message == 'No such command "it\'s".'


def test_custom_message():
    exc = click.NoSuchCommand("missing", message="Nope.")
    assert exc.command_name == "missing"
    assert exc.message == "Nope."
    assert exc.format_message() == "Nope."


@pytest.mark.parametrize("possibilities", [None, []])
def test_no_possibilities(possibilities):
    exc = click.NoSuchCommand("pus", possibilities=possibilities)
    assert exc.possibilities is None
    assert exc.format_message() == "No such command 'pus'."


def test_no_close_matches():
    exc = click.NoSuchCommand("zzz", possibilities=["push", "declare"])
    assert exc.possibilities == []
    assert exc.format_message() == "No such command 'zzz'."


def test_single_close_match():
    exc = click.NoSuchCommand("pus", possibilities=["push", "declare"])
    assert exc.possibilities == ["push"]
    assert exc.format_message() == "No such command 'pus'. Did you mean 'push'?"


def test_multiple_close_matches_sorted():
    exc = click.NoSuchCommand("decline", possibilities=["refine", "push", "declare"])
    assert exc.possibilities == ["declare", "refine"]
    assert exc.format_message() == (
        "No such command 'decline'. (Did you mean one of: 'declare', 'refine'?)"
    )


def test_suggestions_appended_to_custom_message():
    exc = click.NoSuchCommand("pus", message="Unknown.", possibilities=["push"])
    assert exc.format_message() == "Unknown. Did you mean 'push'?"


@pytest.mark.parametrize(
    "possibilities",
    [
        pytest.param(("push", "declare"), id="tuple"),
        pytest.param({"push": None, "declare": None}, id="dict"),
        pytest.param((n for n in ["push", "declare"]), id="generator"),
    ],
)
def test_possibilities_iterable(possibilities):
    exc = click.NoSuchCommand("pus", possibilities=possibilities)
    assert exc.possibilities == ["push"]


def test_ctx_sets_cmd():
    cli = _make_group()
    ctx = click.Context(cli, info_name="cli")
    exc = click.NoSuchCommand("missing", ctx=ctx)
    assert exc.ctx is ctx
    assert exc.cmd is cli


def test_no_ctx():
    exc = click.NoSuchCommand("missing")
    assert exc.ctx is None
    assert exc.cmd is None


def test_show_without_ctx(capsys):
    click.NoSuchCommand("pus", possibilities=["push"]).show()
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "Error: No such command 'pus'. Did you mean 'push'?\n"


def test_show_with_ctx(capsys):
    cli = _make_group()
    ctx = click.Context(cli, info_name="cli")
    click.NoSuchCommand("pus", possibilities=["push"], ctx=ctx).show()
    captured = capsys.readouterr()
    assert captured.err == (
        "Usage: cli [OPTIONS] COMMAND [ARGS]...\n"
        "Try 'cli --help' for help.\n"
        "\n"
        "Error: No such command 'pus'. Did you mean 'push'?\n"
    )


def test_raised_by_group(runner):
    cli = _make_group()
    result = runner.invoke(cli, ["pus"], standalone_mode=False)
    exc = result.exception
    assert isinstance(exc, click.NoSuchCommand)
    assert exc.command_name == "pus"
    assert exc.possibilities == ["push"]
    assert exc.cmd is cli
    assert exc.ctx is not None
    assert exc.ctx.command is cli


def test_raised_by_group_standalone(runner):
    cli = _make_group()
    result = runner.invoke(cli, ["pus"])
    assert result.exit_code == 2
    assert result.output == (
        "Usage: cli [OPTIONS] COMMAND [ARGS]...\n"
        "Try 'cli --help' for help.\n"
        "\n"
        "Error: No such command 'pus'. Did you mean 'push'?\n"
    )


def test_raised_by_nested_group(runner):
    cli = click.Group("cli")
    sub = _make_group()
    sub.name = "sub"
    cli.add_command(sub)
    result = runner.invoke(cli, ["sub", "pus"], standalone_mode=False)
    exc = result.exception
    assert isinstance(exc, click.NoSuchCommand)
    assert exc.cmd is sub
    assert exc.ctx.command_path == "cli sub"


def test_uses_normalized_name(runner):
    cli = _make_group()
    cli.context_settings = {"token_normalize_func": str.lower}
    result = runner.invoke(cli, ["PUS"], standalone_mode=False)
    exc = result.exception
    assert isinstance(exc, click.NoSuchCommand)
    assert exc.command_name == "pus"
    assert exc.possibilities == ["push"]


def test_raised_by_command_collection(runner):
    cli = click.CommandCollection(sources=[_make_group()])
    result = runner.invoke(cli, ["pus"], standalone_mode=False)
    exc = result.exception
    assert isinstance(exc, click.NoSuchCommand)
    assert exc.command_name == "pus"
    assert exc.cmd is cli


def test_command_collection_suggests_source_commands(runner):
    cli = click.CommandCollection(sources=[_make_group()])
    result = runner.invoke(cli, ["pus"], standalone_mode=False)
    exc = result.exception
    assert isinstance(exc, click.NoSuchCommand)
    assert exc.possibilities == ["push"]


def test_lazy_group_suggests_listed_commands(runner):
    @click.command()
    def push():
        pass

    class LazyGroup(click.Group):
        def list_commands(self, ctx):
            return ["push"]

        def get_command(self, ctx, cmd_name):
            if cmd_name == "push":
                return push
            return None

    result = runner.invoke(LazyGroup("cli"), ["pus"], standalone_mode=False)
    exc = result.exception
    assert isinstance(exc, click.NoSuchCommand)
    assert exc.possibilities == ["push"]


def test_not_raised_when_resilient_parsing():
    cli = _make_group()
    ctx = click.Context(cli, resilient_parsing=True)
    assert cli.resolve_command(ctx, ["pus"]) == (None, None, [])

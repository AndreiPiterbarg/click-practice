import pytest

import click


@pytest.fixture
def sources():
    @click.group()
    def group_a():
        pass

    @group_a.command()
    def alpha():
        """Alpha help."""
        click.echo("alpha called")

    @group_a.command()
    def shared():
        click.echo("shared from a")

    @click.group()
    def group_b():
        pass

    @group_b.command()
    def beta():
        """Beta help."""
        click.echo("beta called")

    @group_b.command()
    def shared():  # noqa: F811
        click.echo("shared from b")

    return group_a, group_b


@pytest.mark.parametrize(
    ("name", "expect"), [("alpha", "alpha called"), ("beta", "beta called")]
)
def test_basic_lookup(runner, sources, name, expect):
    cli = click.CommandCollection(sources=list(sources))
    result = runner.invoke(cli, [name])
    assert not result.exception
    assert result.exit_code == 0
    assert result.output == f"{expect}\n"


def test_own_command_takes_precedence(runner, sources):
    cli = click.CommandCollection(sources=list(sources))

    @cli.command()
    def shared():
        click.echo("shared from collection")

    @cli.command()
    def alpha():
        click.echo("alpha from collection")

    result = runner.invoke(cli, ["shared"])
    assert not result.exception
    assert result.output == "shared from collection\n"

    result = runner.invoke(cli, ["alpha"])
    assert not result.exception
    assert result.output == "alpha from collection\n"


@pytest.mark.parametrize(
    ("order", "expect"), [((0, 1), "shared from a"), ((1, 0), "shared from b")]
)
def test_earlier_source_takes_precedence(runner, sources, order, expect):
    cli = click.CommandCollection(sources=[sources[i] for i in order])
    result = runner.invoke(cli, ["shared"])
    assert not result.exception
    assert result.output == f"{expect}\n"


def test_get_command_checks_sources_in_order(sources):
    group_a, group_b = sources
    cli = click.CommandCollection(sources=[group_a, group_b])

    with click.Context(cli) as ctx:
        assert cli.get_command(ctx, "shared") is group_a.commands["shared"]
        assert cli.get_command(ctx, "beta") is group_b.commands["beta"]
        assert cli.get_command(ctx, "missing") is None


def test_list_commands_sorted_union(sources):
    cli = click.CommandCollection(sources=list(sources))

    @cli.command()
    def zeta():
        pass

    @cli.command()
    def shared():
        pass

    with click.Context(cli) as ctx:
        assert cli.list_commands(ctx) == ["alpha", "beta", "shared", "zeta"]


def test_help_lists_commands_from_all_sources(runner, sources):
    cli = click.CommandCollection(sources=list(sources), help="Collection help.")

    @cli.command()
    def own():
        """Own help."""

    result = runner.invoke(cli, ["--help"])
    assert not result.exception
    assert result.exit_code == 0
    assert "Collection help." in result.output
    commands = result.output.split("Commands:\n", 1)[1].splitlines()
    names = [line.split()[0] for line in commands if line.strip()]
    assert names == ["alpha", "beta", "own", "shared"]
    assert "Alpha help." in result.output
    assert "Beta help." in result.output
    assert "Own help." in result.output


def test_add_source(runner, sources):
    group_a, group_b = sources
    cli = click.CommandCollection(sources=[group_a])

    result = runner.invoke(cli, ["beta"])
    assert result.exception
    assert result.exit_code == 2
    assert "No such command 'beta'." in result.output

    cli.add_source(group_b)
    assert cli.sources == [group_a, group_b]

    result = runner.invoke(cli, ["beta"])
    assert not result.exception
    assert result.output == "beta called\n"

    with click.Context(cli) as ctx:
        assert cli.list_commands(ctx) == ["alpha", "beta", "shared"]


def test_unknown_command(runner, sources):
    cli = click.CommandCollection(sources=list(sources))
    result = runner.invoke(cli, ["missing"])
    assert result.exception
    assert result.exit_code == 2
    assert "No such command 'missing'." in result.output


def test_source_callback_not_invoked(runner):
    @click.group()
    def source():
        click.echo("source callback")

    @source.command()
    def sub():
        click.echo("sub called")

    @click.command(cls=click.CommandCollection, sources=[source])
    def cli():
        click.echo("collection callback")

    result = runner.invoke(cli, ["sub"])
    assert not result.exception
    assert result.output.splitlines() == ["collection callback", "sub called"]


def test_source_params_not_added(runner):
    @click.group()
    @click.option("--verbose", is_flag=True)
    def source(verbose):
        click.echo(f"source verbose={verbose}")

    @source.command()
    def sub():
        click.echo("sub called")

    cli = click.CommandCollection(sources=[source])
    assert [p.name for p in cli.params] == []

    result = runner.invoke(cli, ["sub"])
    assert not result.exception
    assert result.output == "sub called\n"

    result = runner.invoke(cli, ["--verbose", "sub"])
    assert result.exception
    assert result.exit_code == 2
    assert "No such option '--verbose'." in result.output


def test_arguments_and_options_pass_through(runner):
    @click.group()
    def source():
        pass

    @source.command()
    @click.argument("name")
    @click.option("--count", type=int, default=1)
    @click.option("--shout", is_flag=True)
    def greet(name, count, shout):
        message = f"hello {name}"

        if shout:
            message = message.upper()

        for _ in range(count):
            click.echo(message)

    cli = click.CommandCollection(sources=[source])

    result = runner.invoke(cli, ["greet", "world"])
    assert not result.exception
    assert result.output == "hello world\n"

    result = runner.invoke(cli, ["greet", "--count", "2", "--shout", "world"])
    assert not result.exception
    assert result.output.splitlines() == ["HELLO WORLD", "HELLO WORLD"]

    result = runner.invoke(cli, ["greet", "--count", "x", "world"])
    assert result.exception
    assert result.exit_code == 2
    assert "'x' is not a valid integer." in result.output

    result = runner.invoke(cli, ["greet"])
    assert result.exception
    assert result.exit_code == 2
    assert "Missing argument 'NAME'." in result.output


def test_chain_invokes_multiple_source_commands(runner, sources):
    cli = click.CommandCollection(sources=list(sources), chain=True)
    result = runner.invoke(cli, ["beta", "alpha", "beta"])
    assert not result.exception
    assert result.output.splitlines() == ["beta called", "alpha called", "beta called"]


def test_chain_with_arguments(runner):
    @click.group()
    def source():
        pass

    @source.command()
    @click.argument("value")
    def first(value):
        click.echo(f"first={value}")

    @source.command()
    @click.option("-n", type=int)
    def second(n):
        click.echo(f"second={n}")

    cli = click.CommandCollection(sources=[source], chain=True)
    result = runner.invoke(cli, ["first", "x", "second", "-n", "3", "first", "y"])
    assert not result.exception
    assert result.output.splitlines() == ["first=x", "second=3", "first=y"]


@pytest.mark.parametrize("nested_chain", [True, False])
def test_chain_rejects_source_group(runner, nested_chain):
    @click.group()
    def source():
        pass

    @source.group(chain=nested_chain)
    def nested():
        pass

    @nested.command()
    def leaf():
        click.echo("leaf called")

    cli = click.CommandCollection("cli", sources=[source], chain=True)
    result = runner.invoke(cli, ["nested", "leaf"])
    assert isinstance(result.exception, RuntimeError)
    assert str(result.exception) == (
        "Found the group 'nested' as subcommand to another group "
        " 'cli' that is in chain mode. This is not supported."
    )
    assert "leaf called" not in result.output


def test_non_chain_allows_source_group(runner):
    @click.group()
    def source():
        pass

    @source.group(chain=True)
    def nested():
        pass

    @nested.command()
    def leaf():
        click.echo("leaf called")

    cli = click.CommandCollection(sources=[source])
    result = runner.invoke(cli, ["nested", "leaf", "leaf"])
    assert not result.exception
    assert result.output.splitlines() == ["leaf called", "leaf called"]


@pytest.mark.parametrize("args", [[], ["--help"], ["missing"]])
def test_empty_sources_matches_empty_group(runner, args):
    collection = click.CommandCollection("cli")
    group = click.Group("cli")
    assert collection.sources == []

    with click.Context(collection) as ctx:
        assert collection.list_commands(ctx) == []
        assert collection.get_command(ctx, "missing") is None

    expect = runner.invoke(group, args)
    result = runner.invoke(collection, args)
    assert result.exit_code == expect.exit_code
    assert result.output == expect.output
    assert type(result.exception) is type(expect.exception)


def test_sources_list_not_shared():
    a = click.CommandCollection()
    b = click.CommandCollection()
    a.add_source(click.Group())
    assert b.sources == []

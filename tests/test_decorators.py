from __future__ import annotations

import importlib.metadata
import typing as t

import pytest

import click


def _noop() -> None:
    pass


def test_command_twice_raises() -> None:
    cmd = click.command()(_noop)

    with pytest.raises(TypeError, match="into a command twice"):
        click.command()(cmd)


@pytest.mark.parametrize("args", [["--yes"], ["-y"]])
def test_confirmation_option_flag_skips_prompt(runner, args) -> None:
    @click.command()
    @click.confirmation_option("--yes", "-y")
    def cli() -> None:
        click.echo("done")

    result = runner.invoke(cli, args)
    assert result.exit_code == 0
    assert result.output == "done\n"


def test_confirmation_option_prompt_accept(runner) -> None:
    @click.command()
    @click.confirmation_option()
    def cli() -> None:
        click.echo("done")

    result = runner.invoke(cli, input="y\n")
    assert result.exit_code == 0
    assert result.output == "Do you want to continue? [y/N]: y\ndone\n"


def test_confirmation_option_prompt_decline_aborts(runner) -> None:
    @click.command()
    @click.confirmation_option()
    def cli() -> None:
        click.echo("done")

    result = runner.invoke(cli, input="n\n")
    assert result.exit_code == 1
    assert "done" not in result.output
    assert "Aborted!" in result.output


def test_confirmation_option_defaults() -> None:
    @click.command()
    @click.confirmation_option()
    def cli() -> None:
        pass

    opt = cli.params[0]
    assert isinstance(opt, click.Option)
    assert opt.opts == ["--yes"]
    assert opt.is_flag
    assert not opt.expose_value
    assert opt.prompt == "Do you want to continue?"
    assert opt.help == "Confirm the action without prompting."


def test_confirmation_option_custom_prompt(runner) -> None:
    @click.command()
    @click.confirmation_option("--force", prompt="Really?")
    def cli() -> None:
        click.echo("done")

    result = runner.invoke(cli, input="n\n")
    assert result.exit_code == 1
    assert result.output.startswith("Really? [y/N]: n\n")

    result = runner.invoke(cli, ["--force"])
    assert result.exit_code == 0
    assert result.output == "done\n"


def test_password_option_prompts_hidden_with_confirmation(runner) -> None:
    @click.command()
    @click.password_option()
    def cli(password: str) -> None:
        click.echo(f"pw={password}")

    result = runner.invoke(cli, input="secret\nsecret\n")
    assert result.exit_code == 0
    assert result.output == "Password: \nRepeat for confirmation: \npw=secret\n"


def test_password_option_mismatch_reprompts(runner) -> None:
    @click.command()
    @click.password_option()
    def cli(password: str) -> None:
        click.echo(f"pw={password}")

    result = runner.invoke(cli, input="one\ntwo\nthree\nthree\n")
    assert result.exit_code == 0
    assert "Error: The two entered values do not match." in result.output
    assert result.output.endswith("pw=three\n")


def test_password_option_from_command_line(runner) -> None:
    @click.command()
    @click.password_option("--pw", "-p")
    def cli(pw: str) -> None:
        click.echo(f"pw={pw}")

    result = runner.invoke(cli, ["-p", "given"])
    assert result.exit_code == 0
    assert result.output == "pw=given\n"


def test_password_option_defaults() -> None:
    @click.command()
    @click.password_option()
    def cli(password: str) -> None:
        pass

    opt = cli.params[0]
    assert isinstance(opt, click.Option)
    assert opt.opts == ["--password"]
    assert opt.prompt == "Password"
    assert opt.confirmation_prompt is True
    assert opt.hide_input is True


def test_password_option_overrides() -> None:
    @click.command()
    @click.password_option(confirmation_prompt=False, hide_input=False)
    def cli(password: str) -> None:
        pass

    opt = cli.params[0]
    assert isinstance(opt, click.Option)
    assert opt.confirmation_prompt is False
    assert opt.hide_input is False


def _fake_version(versions: dict[str, str]) -> t.Callable[[str], str]:
    def version(name: str) -> str:
        if name in versions:
            return versions[name]

        raise importlib.metadata.PackageNotFoundError(name)

    return version


def _build_cli_in_module(
    module_globals: dict[str, t.Any], decorator_source: str
) -> click.Command:
    """Build a command from a namespace with the given module globals, so
    ``version_option`` inspects that namespace when detecting the package.
    """
    namespace: dict[str, t.Any] = {"click": click}
    namespace.update(module_globals)
    source = f"@click.command()\n@{decorator_source}\ndef cli():\n    pass\n"
    exec(compile(source, "<test>", "exec"), namespace)
    return namespace["cli"]


@pytest.mark.parametrize(
    ("module_globals", "package"),
    [
        ({"__name__": "mypkg"}, "mypkg"),
        ({"__name__": "mypkg.sub.mod"}, "mypkg"),
        ({"__name__": "__main__", "__package__": "mypkg"}, "mypkg"),
        ({"__name__": "__main__", "__package__": "mypkg.sub"}, "mypkg"),
    ],
)
def test_version_option_detects_package_name(
    runner, monkeypatch, module_globals, package
) -> None:
    monkeypatch.setattr(
        importlib.metadata, "version", _fake_version({package: "1.2.3"})
    )
    cli = _build_cli_in_module(
        module_globals, "click.version_option(message='%(package)s %(version)s')"
    )

    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert result.output == f"{package} 1.2.3\n"


@pytest.mark.parametrize(
    "package",
    [
        None,
        pytest.param(
            "",
            marks=pytest.mark.xfail(
                strict=True,
                raises=AssertionError,
                reason="'python -m' on a top-level module sets __package__ to ''"
                " and importlib.metadata.version('') raises ValueError",
            ),
        ),
    ],
)
def test_version_option_main_without_package_errors(runner, package) -> None:
    cli = _build_cli_in_module(
        {"__name__": "__main__", "__package__": package}, "click.version_option()"
    )

    result = runner.invoke(cli, ["--version"])
    assert isinstance(result.exception, RuntimeError)
    assert "Could not determine the version for" in str(result.exception)


def test_version_option_detection_skipped_when_version_given(runner) -> None:
    cli = _build_cli_in_module(
        {"__name__": "__main__", "__package__": None},
        "click.version_option('4.5.6', message='%(package)s %(version)s')",
    )

    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert result.output == "None 4.5.6\n"


def test_version_option_detected_name_resolved_via_distributions(
    runner, monkeypatch
) -> None:
    monkeypatch.setattr(
        importlib.metadata, "version", _fake_version({"my-dist": "2.0"})
    )
    monkeypatch.setattr(
        importlib.metadata, "packages_distributions", lambda: {"mypkg": ["my-dist"]}
    )
    cli = _build_cli_in_module(
        {"__name__": "mypkg.cli"},
        "click.version_option(message='%(package)s %(version)s')",
    )

    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert result.output == "my-dist 2.0\n"


def test_version_option_detected_name_multiple_distributions(
    runner, monkeypatch
) -> None:
    monkeypatch.setattr(importlib.metadata, "version", _fake_version({}))
    monkeypatch.setattr(
        importlib.metadata,
        "packages_distributions",
        lambda: {"mypkg": ["dist-a", "dist-b"]},
    )
    cli = _build_cli_in_module({"__name__": "mypkg.cli"}, "click.version_option()")

    result = runner.invoke(cli, ["--version"])
    assert isinstance(result.exception, RuntimeError)
    assert str(result.exception) == (
        "'mypkg' maps to multiple installed distributions (dist-a, dist-b)."
        " Pass 'package_name' to disambiguate."
    )


def test_version_option_detected_name_no_distribution(runner, monkeypatch) -> None:
    monkeypatch.setattr(importlib.metadata, "version", _fake_version({}))
    monkeypatch.setattr(
        importlib.metadata, "packages_distributions", lambda: {"other": ["x"]}
    )
    cli = _build_cli_in_module({"__name__": "mypkg.cli"}, "click.version_option()")

    result = runner.invoke(cli, ["--version"])
    assert isinstance(result.exception, RuntimeError)
    assert str(result.exception) == (
        "'mypkg' is not installed. Try passing 'package_name' instead."
    )


def test_version_option_explicit_values(runner) -> None:
    @click.command()
    @click.version_option(
        "1.0",
        "-V",
        "--show-version",
        package_name="pkg",
        prog_name="tool",
        message="%(prog)s|%(package)s|%(version)s",
    )
    def cli() -> None:
        click.echo("ran")

    for args in (["-V"], ["--show-version"]):
        result = runner.invoke(cli, args, prog_name="ignored")
        assert result.exit_code == 0
        assert result.output == "tool|pkg|1.0\n"

    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 2

    result = runner.invoke(cli, [])
    assert result.exit_code == 0
    assert result.output == "ran\n"


def test_version_option_default_message_uses_root_info_name(runner) -> None:
    @click.group()
    @click.version_option("3.1")
    def cli() -> None:
        pass

    @cli.command()
    def sub() -> None:
        pass

    result = runner.invoke(cli, ["--version"], prog_name="rootprog")
    assert result.exit_code == 0
    assert result.output == "rootprog, version 3.1\n"


def test_version_option_is_eager(runner) -> None:
    @click.command()
    @click.option("--num", type=int)
    @click.version_option("1.0")
    def cli(num: int) -> None:
        pass

    result = runner.invoke(cli, ["--num", "bad", "--version"], prog_name="tool")
    assert result.exit_code == 0
    assert result.output == "tool, version 1.0\n"


def _assert_resilient_parsing_does_not_exit(cli: click.Command, flag: str) -> None:
    ctx = cli.make_context("cli", [flag], resilient_parsing=True)
    assert ctx.resilient_parsing


@pytest.mark.parametrize(
    "decorator",
    [
        click.version_option("1.0"),
        click.custom_version_option(lambda ctx: "custom"),
    ],
    ids=["version_option", "custom_version_option"],
)
def test_version_options_resilient_parsing(capsys, decorator) -> None:
    @click.command()
    @decorator
    def cli() -> None:
        pass

    _assert_resilient_parsing_does_not_exit(cli, "--version")
    assert capsys.readouterr().out == ""


def test_help_option_resilient_parsing(capsys) -> None:
    @click.command(add_help_option=False)
    @click.help_option()
    def cli() -> None:
        pass

    _assert_resilient_parsing_does_not_exit(cli, "--help")
    assert capsys.readouterr().out == ""


def test_help_option_prints_help_and_exits(runner) -> None:
    @click.command(add_help_option=False)
    @click.help_option("--info")
    def cli() -> None:
        """Command docs."""
        click.echo("ran")

    result = runner.invoke(cli, ["--info"])
    assert result.exit_code == 0
    assert "Command docs." in result.output
    assert "--info" in result.output
    assert "Show this message and exit." in result.output
    assert "ran" not in result.output

    result = runner.invoke(cli, [])
    assert result.exit_code == 0
    assert result.output == "ran\n"


def test_version_option_without_caller_frame(runner, monkeypatch) -> None:
    monkeypatch.setattr(click.decorators.inspect, "currentframe", lambda: None)

    @click.command()
    @click.version_option()
    def cli() -> None:
        pass

    result = runner.invoke(cli, ["--version"])
    assert isinstance(result.exception, RuntimeError)
    assert str(result.exception) == (
        "Could not determine the version for None automatically."
    )


def test_help_option_default_name(runner) -> None:
    @click.command(add_help_option=False)
    @click.help_option()
    def cli() -> None:
        """Command docs."""

    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Command docs." in result.output
    assert "--help  Show this message and exit." in result.output

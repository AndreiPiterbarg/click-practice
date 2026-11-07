import io

import click


def test_message_and_str():
    exc = click.ClickException("Something broke.")
    assert exc.exit_code == 1
    assert exc.message == "Something broke."
    assert exc.format_message() == "Something broke."
    assert str(exc) == "Something broke."


def test_show_defaults_to_stderr(capsys):
    click.ClickException("Something broke.").show()
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "Error: Something broke.\n"


def test_show_to_file(capsys):
    file = io.StringIO()
    click.ClickException("Something broke.").show(file=file)
    assert file.getvalue() == "Error: Something broke.\n"
    captured = capsys.readouterr()
    assert captured.err == ""


def test_show_uses_custom_format_message():
    class CustomError(click.ClickException):
        def format_message(self):
            return f"custom: {self.message}"

    file = io.StringIO()
    CustomError("boom").show(file=file)
    assert file.getvalue() == "Error: custom: boom\n"


def test_show_color_cached_from_context():
    @click.command()
    def cli():
        pass

    with click.Context(cli, color=True):
        exc = click.ClickException("\x1b[31mred\x1b[0m")

    assert exc.show_color is True
    file = io.StringIO()
    exc.show(file=file)
    assert file.getvalue() == "Error: \x1b[31mred\x1b[0m\n"


def test_show_strips_color_without_context():
    exc = click.ClickException("\x1b[31mred\x1b[0m")
    assert exc.show_color is None
    file = io.StringIO()
    exc.show(file=file)
    assert file.getvalue() == "Error: red\n"


def test_exit_code_in_standalone_mode(runner):
    @click.command()
    def cli():
        raise click.ClickException("Something broke.")

    result = runner.invoke(cli)
    assert result.exit_code == 1
    assert result.output == "Error: Something broke.\n"

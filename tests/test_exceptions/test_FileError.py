import click


def test_file_error_surrogates():
    message = click.FileError(filename="\udcff").format_message()
    assert message == "Could not open file '�': unknown error"


def test_file_error_attributes():
    exc = click.FileError("data.txt")
    assert exc.exit_code == 1
    assert exc.filename == "data.txt"
    assert exc.ui_filename == "data.txt"
    assert exc.message == "unknown error"
    assert str(exc) == "unknown error"


def test_file_error_hint():
    exc = click.FileError("data.txt", hint="permission denied")
    assert exc.format_message() == ("Could not open file 'data.txt': permission denied")


def test_file_error_raised_by_file_type(runner, tmp_path):
    @click.command()
    @click.argument("f", type=click.File())
    def cli(f):
        pass

    missing = tmp_path / "missing.txt"
    result = runner.invoke(cli, [str(missing)])
    assert result.exit_code == 2
    assert "No such file or directory" in result.output

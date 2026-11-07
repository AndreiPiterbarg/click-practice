import pathlib
import sys

import pytest

import click


class MockMain:
    __slots__ = "__package__"

    def __init__(self, package_name):
        self.__package__ = package_name


@pytest.mark.parametrize(
    ("path", "main", "expected"),
    [
        ("example.py", None, "example.py"),
        (str(pathlib.Path("/foo/bar/example.py")), None, "example.py"),
        ("example", None, "example"),
        (str(pathlib.Path("example/__main__.py")), "example", "python -m example"),
        (str(pathlib.Path("example/cli.py")), "example", "python -m example.cli"),
        (str(pathlib.Path("./example")), "", "example"),
    ],
)
def test_detect_program_name(path, main, expected):
    assert click.utils._detect_program_name(path, _main=MockMain(main)) == expected


def test_detect_program_name_defaults(monkeypatch):
    monkeypatch.setattr(sys, "argv", [str(pathlib.Path("/foo/bar/example.py"))])
    monkeypatch.setitem(sys.modules, "__main__", MockMain(None))
    assert click.utils._detect_program_name() == "example.py"


def test_detect_program_name_default_main_module(monkeypatch):
    monkeypatch.setitem(sys.modules, "__main__", MockMain("example"))
    path = str(pathlib.Path("example/__main__.py"))
    assert click.utils._detect_program_name(path) == "python -m example"


def test_detect_program_name_empty_path_uses_argv(monkeypatch):
    monkeypatch.setattr(sys, "argv", [str(pathlib.Path("example/cli.py"))])
    main = MockMain("example")
    assert click.utils._detect_program_name("", _main=main) == "python -m example.cli"

import pytest

import click.utils


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("text", "text"),
        (42, "42"),
        (None, "None"),
        ("\N{SNOWMAN}".encode(), "\N{SNOWMAN}"),
    ],
)
def test_make_str(value, expected):
    assert click.utils.make_str(value) == expected


def test_make_str_bytes_uses_filesystem_encoding(monkeypatch):
    monkeypatch.setattr("sys.getfilesystemencoding", lambda: "latin-1")
    assert click.utils.make_str(b"\xe9") == "\xe9"


def test_make_str_invalid_bytes_replaced(monkeypatch):
    monkeypatch.setattr("sys.getfilesystemencoding", lambda: "ascii")
    assert click.utils.make_str(b"a\xffb") == "a\ufffdb"

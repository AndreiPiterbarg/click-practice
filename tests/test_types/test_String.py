import sys

import pytest

import click


@pytest.mark.parametrize(
    ("argv_encoding", "fs_encoding", "value", "expect"),
    [
        # Decoded with the argv encoding.
        ("utf-8", "utf-8", b"\xc3\xa9t\xc3\xa9", "\u00e9t\u00e9"),
        # Falls back to the filesystem encoding when it differs.
        ("ascii", "latin-1", b"\xe9t\xe9", "\u00e9t\u00e9"),
        # Both encodings fail, so undecodable bytes are replaced.
        ("ascii", "utf-8", b"t\xff", "t\ufffd"),
        # The encodings match, so there is nothing else to try.
        ("utf-8", "utf-8", b"t\xff", "t\ufffd"),
    ],
)
def test_string_decodes_bytes(monkeypatch, argv_encoding, fs_encoding, value, expect):
    monkeypatch.setattr(click.types, "_get_argv_encoding", lambda: argv_encoding)
    monkeypatch.setattr(sys, "getfilesystemencoding", lambda: fs_encoding)
    assert click.STRING.convert(value, None, None) == expect


def test_string_converts_non_bytes_with_str():
    assert click.STRING.convert(42, None, None) == "42"

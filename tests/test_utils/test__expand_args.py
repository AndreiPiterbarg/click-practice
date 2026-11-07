import glob
import os
import re

import click


def test_expand_args(monkeypatch):
    user = os.path.expanduser("~")
    assert user in click.utils._expand_args(["~"])
    monkeypatch.setenv("CLICK_TEST", "hello")
    assert "hello" in click.utils._expand_args(["$CLICK_TEST"])
    assert "pyproject.toml" in click.utils._expand_args(["*.toml"])
    assert os.path.join("tests", "conftest.py") in click.utils._expand_args(
        ["**/conftest.py"]
    )
    assert "*.not-found" in click.utils._expand_args(["*.not-found"])
    # a bad glob pattern, such as a pytest identifier, should return itself
    assert click.utils._expand_args(["test.py::test_bad"])[0] == "test.py::test_bad"


def test_expand_args_no_user(monkeypatch):
    monkeypatch.setenv("CLICK_TEST", "hello")
    assert click.utils._expand_args(["~", "$CLICK_TEST"], user=False) == [
        "~",
        "hello",
    ]


def test_expand_args_no_env(monkeypatch):
    monkeypatch.setenv("CLICK_TEST", "hello")
    assert click.utils._expand_args(["~", "$CLICK_TEST"], env=False) == [
        os.path.expanduser("~"),
        "$CLICK_TEST",
    ]


def test_expand_args_glob_not_recursive(monkeypatch, tmp_path):
    nested = tmp_path / "a" / "b"
    nested.mkdir(parents=True)
    (nested / "f.txt").write_text("")
    monkeypatch.chdir(tmp_path)
    pattern = os.path.join("**", "f.txt")
    assert click.utils._expand_args([pattern]) == [os.path.join("a", "b", "f.txt")]
    assert click.utils._expand_args([pattern], glob_recursive=False) == [pattern]


def test_expand_args_glob_regex_error(monkeypatch):
    def bad_glob(pattern, recursive):
        raise re.error("bad pattern")

    monkeypatch.setattr(glob, "glob", bad_glob)
    assert click.utils._expand_args(["*.py"]) == ["*.py"]

import pytest

import click.utils


def test_safecall_returns_result():
    def add(a, b=0):
        return a + b

    assert click.utils._safecall(add)(1, b=2) == 3


def test_safecall_swallows_exception():
    calls = []

    def fail():
        calls.append(True)
        raise ValueError("boom")

    assert click.utils._safecall(fail)() is None
    assert calls == [True]


def test_safecall_does_not_swallow_base_exception():
    def interrupt():
        raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        click.utils._safecall(interrupt)()


def test_safecall_preserves_metadata():
    def documented():
        """Docs."""

    wrapped = click.utils._safecall(documented)
    assert wrapped.__name__ == "documented"
    assert wrapped.__doc__ == "Docs."
    assert wrapped.__wrapped__ is documented

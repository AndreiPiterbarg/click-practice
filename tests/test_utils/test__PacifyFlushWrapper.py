import errno
import io

import pytest

import click.utils


class FailingFlush(io.StringIO):
    def __init__(self, error):
        super().__init__()
        self.error = error

    def flush(self):
        raise OSError(self.error, "flush failed")


def test_flush_passes_through():
    flushed = []

    class Recording(io.StringIO):
        def flush(self):
            flushed.append(True)

    click.utils._PacifyFlushWrapper(Recording()).flush()
    assert flushed == [True]


def test_flush_suppresses_broken_pipe():
    click.utils._PacifyFlushWrapper(FailingFlush(errno.EPIPE)).flush()


def test_flush_reraises_other_oserror():
    wrapper = click.utils._PacifyFlushWrapper(FailingFlush(errno.EIO))

    with pytest.raises(OSError) as exc_info:
        wrapper.flush()

    assert exc_info.value.errno == errno.EIO


def test_attributes_are_proxied():
    stream = io.StringIO()
    wrapper = click.utils._PacifyFlushWrapper(stream)
    wrapper.write("hello")
    assert wrapper.getvalue() == "hello"
    assert wrapper.wrapped is stream

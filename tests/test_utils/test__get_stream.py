import pytest

import click.utils


@pytest.mark.parametrize(
    "get_stream", [click.utils._get_binary_stream, click.utils._get_text_stream]
)
def test_unknown_stream_name(get_stream):
    with pytest.raises(TypeError, match="Unknown standard stream 'stdfoo'"):
        get_stream("stdfoo")


def test_get_text_stream_stdin(runner):
    with runner.isolation(input="hello"):
        assert click.utils._get_text_stream("stdin").read() == "hello"


def test_get_text_stream_stdout(runner):
    with runner.isolation() as (out, _, _):
        stream = click.utils._get_text_stream("stdout")
        stream.write("hello")
        stream.flush()
        assert out.getvalue() == b"hello"


def test_get_text_stream_errors(runner):
    with runner.isolation(input=b"a\xffb"):
        stream = click.utils._get_text_stream(
            "stdin", encoding="ascii", errors="replace"
        )
        assert stream.read() == "a\ufffdb"

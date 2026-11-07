import sys

import click


def test_iter_lazyfile(tmpdir):
    expected = list(map(str, range(10)))
    p = tmpdir.mkdir("testdir").join("testfile")
    p.write("\n".join(expected))
    with p.open() as f:
        with click.utils._LazyFile(f.name) as lf:
            for e_line, a_line in zip(expected, lf, strict=False):
                assert e_line == a_line.strip()


def test_lazyfile_dash_reads_stdin(runner):
    @click.command()
    def cli():
        lf = click.utils._LazyFile("-")
        assert not lf.should_close
        with lf as f:
            click.echo(f.read())

        assert not sys.stdin.closed

    result = runner.invoke(cli, input="from stdin")
    assert result.exception is None
    assert result.output == "from stdin\n"


def test_lazyfile_dash_repr_is_stream_repr(runner):
    with runner.isolation():
        lf = click.utils._LazyFile("-", "w")
        assert repr(lf) == repr(lf._f)


def test_lazyfile_repr_unopened(tmp_path):
    path = tmp_path / "out.txt"
    lf = click.utils._LazyFile(path, "w")
    assert repr(lf) == f"<unopened file '{path}' w>"
    assert not path.exists()


def test_lazyfile_repr_opened(tmp_path):
    path = tmp_path / "out.txt"
    with click.utils._LazyFile(path, "w") as lf:
        f = lf.open()
        assert repr(lf) == repr(f)

    assert path.exists()

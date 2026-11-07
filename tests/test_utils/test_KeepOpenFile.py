import click


def test_iter_keepopenfile(tmpdir):
    expected = list(map(str, range(10)))
    p = tmpdir.mkdir("testdir").join("testfile")
    p.write("\n".join(expected))
    with p.open() as f:
        for e_line, a_line in zip(expected, click.utils._KeepOpenFile(f), strict=False):
            assert e_line == a_line.strip()


def test_keepopenfile_repr(tmp_path):
    path = tmp_path / "testfile"
    path.write_text("")
    with path.open() as f:
        assert repr(click.utils._KeepOpenFile(f)) == repr(f)

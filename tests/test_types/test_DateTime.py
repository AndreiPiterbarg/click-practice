import datetime

import click


def test_datetime_passes_through_datetime():
    value = datetime.datetime(2026, 1, 2, 3, 4, 5)
    assert click.DateTime().convert(value, None, None) is value


def test_datetime_default_passes_through(runner):
    default = datetime.datetime(2026, 1, 2, 3, 4, 5)

    @click.command()
    @click.option("--when", type=click.DateTime(["%Y"]), default=default)
    def cli(when):
        click.echo(repr(when))

    result = runner.invoke(cli)
    assert result.exception is None
    assert result.output == f"{default!r}\n"

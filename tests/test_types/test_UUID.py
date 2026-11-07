import uuid

import click


def test_uuid_passes_through_uuid():
    value = uuid.UUID(int=1)
    assert click.UUID.convert(value, None, None) is value


def test_uuid_default_passes_through(runner):
    default = uuid.UUID(int=1)

    @click.command()
    @click.option("--id", "id_", type=click.UUID, default=default)
    def cli(id_):
        click.echo(repr(id_))

    result = runner.invoke(cli)
    assert result.exception is None
    assert result.output == f"{default!r}\n"

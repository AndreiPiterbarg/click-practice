import pytest

import click


@pytest.mark.parametrize(
    ("type", "expect"),
    [
        (click.UNPROCESSED, "UNPROCESSED"),
        (click.STRING, "STRING"),
        (click.DateTime(), "DateTime"),
        (click.INT, "INT"),
        (click.FLOAT, "FLOAT"),
        (click.BOOL, "BOOL"),
        (click.UUID, "UUID"),
        (click.IntRange(0, 5), "<IntRange 0<=x<=5>"),
        (click.IntRange(0, 5, clamp=True), "<IntRange 0<=x<=5 clamped>"),
        (click.IntRange(0, 5, min_open=True, max_open=True), "<IntRange 0<x<5>"),
        (click.IntRange(min=1), "<IntRange x>=1>"),
        (click.IntRange(max=5, max_open=True), "<IntRange x<5>"),
        (click.FloatRange(0.5, 1.5), "<FloatRange 0.5<=x<=1.5>"),
        (click.FloatRange(min=0.5, min_open=True), "<FloatRange x>0.5>"),
    ],
)
def test_type_repr(type, expect):
    assert repr(type) == expect

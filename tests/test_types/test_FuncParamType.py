import pytest

import click


@pytest.mark.parametrize(
    ("error_message", "expected"),
    [
        ("bad value: nope", "bad value: nope"),
        ("", "nope"),
    ],
)
def test_func_param_type_uses_value_error_message(error_message, expected):
    def parse(value):
        raise ValueError(error_message if error_message else "")

    func_type = click.types.FuncParamType(parse)

    with pytest.raises(click.BadParameter) as exc_info:
        func_type.convert("nope", None, None)

    assert expected in exc_info.value.message


class _UndecodableBytes(bytes):
    def __str__(self):
        raise UnicodeDecodeError("ascii", bytes(self), 0, 1, "undecodable")


def test_func_param_type_decodes_undecodable_bytes_value():
    """With an empty ``ValueError`` message the value is shown instead. If
    it can't be turned into a string, its bytes are decoded with replacement.
    """

    def parse(value):
        raise ValueError()

    func_type = click.types.FuncParamType(parse)

    with pytest.raises(click.BadParameter) as exc_info:
        func_type.convert(_UndecodableBytes(b"\xffnope"), None, None)

    assert exc_info.value.message == "\ufffdnope"

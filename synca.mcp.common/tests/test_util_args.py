"""Isolated tests for synca.mcp.common.util.args."""


import pytest
from unittest.mock import MagicMock

from synca.mcp.common import errors
from synca.mcp.common.util import ArgParser


def test_argparser_constructor():
    """Test the ArgParser constructor.

    Verifies that ArgParser initializes with an empty arguments dictionary.
    """
    parser = ArgParser()
    assert isinstance(parser.arguments, dict)
    assert len(parser.arguments) == 0


def test_argparser_add_argument(patches):
    """Test the add_argument method."""
    parser = ArgParser()
    name = "test_name"
    kwargs = {"required": True, "default": "test_value"}
    patched = patches(
        "cast",
        "types",
        prefix="synca.mcp.common.util.args")

    with patched as (m_cast, m_types):
        assert not parser.add_argument(name, **kwargs)

    assert (
        m_cast.call_args
        == [(m_types.ArgConfig, kwargs), {}])
    assert (
        parser.arguments[name]
        == m_cast.return_value)


@pytest.mark.parametrize(
    "args_items",
    [[], [("arg1", "value1")], [("arg1", None)],
     [("arg1", "value1"), ("arg2", "value2")]])
@pytest.mark.parametrize(
    "config_items",
    [[], [("arg1", {})], [("arg2", {})], [("arg1", {}), ("arg3", {})]])
def test_argparser_parse_dict(patches, args_items, config_items):
    """Test the parse_dict method."""
    parser = ArgParser()
    args_dict = dict(args_items)
    parser.arguments = dict(config_items)
    expected_handle_calls = []
    for name, config in config_items:
        expected_handle_calls.append(
            [(args_dict, name, config), {}])
    patched = patches(
        "_handle_argument",
        prefix="synca.mcp.common.util.args.ArgParser")

    with patched as (m_handle,):
        def handle_side_effect(args_dict, name, config):
            if name in args_dict and args_dict[name] is not None:
                return f"HANDLED_{name}"
            return None
        m_handle.side_effect = handle_side_effect
        assert (
            parser.parse_dict(args_dict)
            == ({name: f"HANDLED_{name}"
                 for name, _
                 in config_items
                 if (name in args_dict
                     and args_dict[name] is not None)}
                | {name: value
                   for name, value
                   in args_items
                   if (name not in parser.arguments
                       and value is not None)}))

    assert (
        m_handle.call_args_list
        == expected_handle_calls)


@pytest.mark.parametrize(
    "arg_in_dict",
    [True, False])
@pytest.mark.parametrize(
    "required",
    [True, False])
@pytest.mark.parametrize(
    "has_default",
    [True, False])
def test_argparser_handle_argument(patches, arg_in_dict, required, has_default):
    """Test the _handle_argument method."""
    parser = ArgParser()
    name = "test_arg_name"
    value = MagicMock()
    args_dict = MagicMock()
    config = MagicMock()
    args_dict.get.return_value = value if arg_in_dict else None
    args_dict.__getitem__.return_value = value
    config.get.return_value = required
    config.__contains__.return_value = has_default
    patched = patches(
        "_type_argument",
        prefix="synca.mcp.common.util.args.ArgParser")

    with patched as (m_type,):
        if not arg_in_dict and required:
            with pytest.raises(errors.ArgValueError) as e:
                parser._handle_argument(args_dict, name, config)
        else:
            assert (
                parser._handle_argument(args_dict, name, config)
                == (m_type.return_value if arg_in_dict
                    else (config["default"] if has_default
                          else None)))

    assert (
        args_dict.get.call_args
        == [(name,), {}])
    if not arg_in_dict and required:
        assert "Required argument" in str(e.value)
        assert name in str(e.value)
        assert not m_type.called
    elif arg_in_dict:
        assert (
            m_type.call_args
            == [(args_dict.__getitem__.return_value, name, config), {}])
    else:
        assert not m_type.called


@pytest.mark.parametrize(
    "has_choices",
    [True, False])
@pytest.mark.parametrize(
    "value_in_choices",
    [True, False])
@pytest.mark.parametrize(
    "has_type",
    [True, False])
@pytest.mark.parametrize(
    "error",
    [None, ValueError, TypeError, BaseException])
def test_argparser_type_argument(
        patches, has_choices, value_in_choices, has_type, error):
    """Test the _type_argument method."""
    parser = ArgParser()
    name = MagicMock()
    value = MagicMock()
    config = MagicMock()
    config.__contains__.side_effect = lambda k: (
        (k == "choices" and has_choices)
        or (k == "type" and has_type))
    if has_choices:
        choices = MagicMock()
        config.__getitem__.return_value = choices
        choices.__contains__.return_value = (
            True
            if value_in_choices
            else False)
    type_mock = MagicMock()
    config.__getitem__.side_effect = lambda k: (
        (choices
         if k == "choices"
         else (type_mock
               if k == "type"
               else MagicMock())))
    if error:
        type_mock.side_effect = error("conversion error")
    type_mock.__name__ = "test_type"
    will_raise = bool(
        (has_choices and not value_in_choices)
        or (has_type and error))
    expected_error = (
        errors.ArgValueError
        if ((has_choices
             and not value_in_choices)
            or (error in [ValueError, TypeError]))
        else error)

    if will_raise and expected_error:
        with pytest.raises(expected_error) as e:
            parser._type_argument(value, name, config)
    else:
        assert (
            parser._type_argument(value, name, config)
            == (type_mock.return_value
                if has_type and not error
                else value))

    if has_choices and not value_in_choices:
        assert not type_mock.called
        assert (
            e.value.args[0]
            == f"Argument '{name}' must be one of {choices}, got '{value}'")
    elif has_type and not will_raise:
        assert (
            type_mock.call_args
            == [(value,), {}])
    elif has_type and error:
        if error in [ValueError, TypeError]:
            assert (
                e.value.args[0]
                == (f"Failed to convert '{name}' to "
                    f"{type_mock.__name__}: conversion error"))
        expected_error = (
            errors.ArgValueError
            if error in [ValueError, TypeError]
            else error)
        if expected_error is errors.ArgValueError:
            assert (
                type_mock.call_args
                == [(value,), {}])
    if has_choices and not value_in_choices:
        assert (
            config.__contains__.call_args_list
            == [[("choices", ), {}]])
    else:
        assert (
            config.__contains__.call_args_list
            == [[("choices", ), {}], [("type", ), {}]])
    if has_choices:
        assert (
            choices.__contains__.call_args
            == [(value,), {}])

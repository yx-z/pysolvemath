from typing import TypeVar, Callable, Optional

T = TypeVar("T")

require_not_none = lambda x: x
require_none = lambda x: not x


def require(check_description: str, /, val: T, require_func: Callable[[T], bool] = require_not_none) -> None:
    """
    :param check_description: description of check
    :param val: value to be checked
    :param require_func: check eq_function used to require `val`. Default to `require_not_none`.
    """
    if not require_func(val):
        raise RuntimeError(f"Require {check_description}. But seeing value {val}.")


def or_default_arg(arg_val: Optional[T], /, default_val: T) -> T:
    """
    :param arg_val: current arg_val
    :param default_val: default value to use if `arg_val` is None
    :return: default_arg
    """
    return arg_val if arg_val else default_val

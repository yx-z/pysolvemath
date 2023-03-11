import itertools
from fractions import Fraction
from typing import Callable, Dict, Union
from typing import Tuple, Iterable, List

import numpy as np
from scipy.optimize import fsolve

from .control_flow import or_default_arg, require


def solve_root_at_zero(function: Callable[[Tuple], Tuple], /, *,
                       args: Dict[str, type],
                       init_guess_func: Callable[[int], Tuple[float]],
                       stop_func: Callable[[], bool],
                       max_tries: int,
                       tol: float) -> Dict[str, Union[float, int, Fraction]]:
    """
    :param function: function to solve for `function(vector_params) == 0`
    "param args: <arg_name, type> info
    :param init_guess_func: eq_function that given `dimension`: int, return a list of initial guess of the same dimension
                            Default to `values_from` in `init_guess`.
    :param stop_func: eq_function that return True if solver shall stop.
    :param max_tries: number of tries with different initial guesses, if using `stop_after_tries`.
    :param tol: tolerance to coerce result float to int.
    :return: if solved, return an array of roots in the order of vector_params of `function`.
    :raises: RuntimeError if solution cannot be found
    """
    init_guess_func = or_default_arg(init_guess_func, values_from)
    stop_func = or_default_arg(stop_func, stop_after_tries(max_tries))

    msg = "initial guess empty"
    for guess in init_guess_func(len(args)):
        res, _, flag, msg = fsolve(function, guess, full_output=True)
        # according to scipy doc, flag == 1 means solution found
        if flag == 1:
            coreced = perform_corece(args, res, tol)
            if coreced:
                return coreced
        if stop_func():
            break
    raise RuntimeError(f"solution not found: {msg}")


def values_from(dimension: int, values: List[float] = None) -> Iterable[Tuple[float]]:
    """
    :param dimension: dimension of problem space
    :param values: initial guesses per value
    :return: generating lists, each list has length `dimension` and contains values from one of `values`
             The generation order is stable.
    """
    values = or_default_arg(values, [-1e5, -1.0, 0.0, 1.0, 1e5])
    return itertools.product(*itertools.repeat(values, dimension))


def random_values(dimension: int, *, lower_bound: float = -1e5, upper_bound: float = 1e5) -> Iterable[Tuple[float]]:
    """
    :param dimension: dimension of problem space
    :param lower_bound: inclusive lower bound of generated random value
    :param upper_bound: exclusive upper bound of generated random value
    :return: an infinite generating sequence of random values specified by parameters
    """
    while True:
        yield np.random.uniform(lower_bound, upper_bound, dimension)


def perform_corece(args: Dict[str, type], res: np.ndarray, tol: float) -> Dict[str, Union[float, int, Fraction]]:
    """
    Try to coerce `float` to `int` or `Fraction` for `res`, if its corresponding `arg` is specified.
    Coerce is successful if rounding is within `tol`.
    Return empty dict if any coercion failed.
    """
    require("Tolerance is greater than 0", tol, lambda t: t > 0)

    type_to_round_func = {
        int: round,
        Fraction: lambda x: Fraction(x).limit_denominator(int(1 / tol))
    }

    ans = {}
    for (name, arg_type), result in zip(args.items(), res):
        rounded = type_to_round_func.get(arg_type, float)(result)
        if abs(rounded - result) > tol:
            return {}
        ans[name] = rounded
    return ans


def stop_after_tries(max_tries: int, /) -> Callable[[], bool]:
    """
    :param max_tries: max number of tries to solve (with different initial gusses)
    :return: a stop_func that let solver stop after `max_tries`
    """
    require("max_tries: int must be greater than 0", max_tries, lambda x: x > 0)

    num_tries = 0

    def _stop():
        nonlocal num_tries
        if num_tries > max_tries:
            return True
        num_tries += 1
        return False

    return _stop

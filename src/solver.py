from typing import Callable, Tuple, Dict, Union

import numpy as np
from scipy.optimize import fsolve

from src.control_flow import or_default_arg, require
from src.initial_guess import values_from
from src.stop_solve import stop_after_tries


def solve_root_at_zero(function: Callable[[Tuple], Tuple], /, *,
                       args: Dict[str, type],
                       init_guess_func: Callable[[int], Tuple[float]],
                       stop_func: Callable[[], bool],
                       max_tries: int,
                       tol: float = 1e-3) -> np.ndarray:
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


def perform_corece(args: Dict[str, type], res: np.ndarray, tol: float) -> Dict[str, Union[float, int]]:
    """
    Try coerce `float` to `int` for `res` if its corresponding `arg` is specified as `int`.
    Coerce is successful if rounding is within `tol`.
    Return empty dict if any coercion failed.
    """
    require("Tolerance is greater than 0", tol, lambda t: t > 0)
    ans = {}
    for (name, arg_type), result in zip(args.items(), res):
        if arg_type != int:
            ans[name] = result
            continue
        rounded = round(result)
        if abs(rounded - result) > tol:
            return {}
        ans[name] = rounded
    return ans

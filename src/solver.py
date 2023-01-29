from typing import Callable, Tuple

import numpy as np
from scipy.optimize import fsolve

from src.control_flow import or_default_arg
from src.initial_guess import values_from
from src.stop_solve import stop_after_tries


def solve_root_at_zero(function: Callable[[Tuple], Tuple], /, *,
                       dimension: int,
                       init_guess_func: Callable[[int], Tuple[float]],
                       stop_func: Callable[[], bool],
                       max_tries: int) -> np.ndarray:
    """
    :param function: function to solve for `function(vector_params) == 0`
    "param dimension: dimension of the problem space, i.e. number of unknowns in `function`.
    :param init_guess_func: eq_function that given `dimension`: int, return a list of initial guess of the same dimension
                            Default to `values_from` in `init_guess`.
    :param stop_func: eq_function that return True if solver shall stop.
    :param max_tries: number of tries with different initial guesses, if using `stop_after_tries`.
    :return: if solved, return an array of roots in the order of vector_params of `function`.
    :raises: RuntimeError if solution cannot be found
    """
    init_guess_func = or_default_arg(init_guess_func, values_from)
    stop_func = or_default_arg(stop_func, stop_after_tries(max_tries))

    msg = "initial guess empty"
    for guess in init_guess_func(dimension):
        res, _, flag, msg = fsolve(function, guess, full_output=True)
        if flag == 1:
            # according to scipy doc, flag == 1 means solution found
            return res
        if stop_func():
            break
    raise RuntimeError(f"solution not found: {msg}")

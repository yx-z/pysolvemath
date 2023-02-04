from typing import Callable, Dict, Tuple

from solver import solve_root_at_zero
from src.parsing import check_and_get_arg_names, parse_as_expressions, corece_to_equality, get_solver_function_code, \
    get_solver_function


def solve_equations(eq_function: Callable[..., None], /, *,
                    init_guess_func: Callable[[int], Tuple[float]] = None,
                    stop_func: Callable[[], bool] = None,
                    max_tries: int = 10,
                    tol: float = 1e-3) -> Dict[str, float]:
    """
    :param eq_function: function containing equations. Parameters are unknowns.
    :param init_guess_func: eq_function that given `dimension`: int, return a list of initial guess of the same dimension
                            Default to `values_from` in `init_guess`.
    :param stop_func: eq_function that return True if solver shall stop. Default to stop after `max_tries`.
    :param max_tries: number of tries with different initial guesses, if using `stop_after_tries` / default `stop_func`.
                      Default to 10.
    :param tol: tolerance needed if need to coerce result to int
    :return: if solved, return a dictionary of <variable name, answer value>. Otherwise, return emtpy dictionary.
    """
    args = check_and_get_arg_names(eq_function)

    exprs = parse_as_expressions(eq_function)
    equalties = [corece_to_equality(expr) for expr in exprs]
    function_code = get_solver_function_code(args, equalties)

    function = get_solver_function(function_code)
    return solve_root_at_zero(function, args=args, init_guess_func=init_guess_func, stop_func=stop_func,
                              max_tries=max_tries, tol=tol)

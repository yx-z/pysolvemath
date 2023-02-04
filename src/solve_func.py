import ast
import inspect
from typing import Callable, Optional, Dict, List, Tuple

from control_flow import require, require_none
from solver import solve_root_at_zero


def solve_equations(eq_function: Callable[..., None], /, *,
                    init_guess_func: Callable[[int], Tuple[float]] = None,
                    stop_func: Callable[[], bool] = None,
                    max_tries: int = 10,
                    tol: float = 1e-3) -> Optional[Dict[str, float]]:
    """
    :param eq_function: function containing equations. Parameters are unknowns.
    :param init_guess_func: eq_function that given `dimension`: int, return a list of initial guess of the same dimension
                            Default to `values_from` in `init_guess`.
    :param stop_func: eq_function that return True if solver shall stop. Default to stop after `max_tries`.
    :param max_tries: number of tries with different initial guesses, if using `stop_after_tries` / default `stop_func`.
                      Default to 10.
    :param tol: tolerance needed if need to coerce result to int
    :return: if solved, return a dictionary of <variable name, answer value>. Otherwise, return None.

    example:

    def equations(x, y):
        x + y == 10
        2 * x == 8

    res = solve_equations(equations) # {"x": 4, "y": 6}
    """
    args = check_and_get_arg_names(eq_function)

    exprs = parse_as_expressions(eq_function)
    equalties = [corece_to_equality(expr) for expr in exprs]
    function_code = get_solver_function_code(args, equalties)

    function = get_solver_function(function_code)
    return solve_root_at_zero(function,
                              args=args,
                              init_guess_func=init_guess_func,
                              stop_func=stop_func,
                              max_tries=max_tries)


def check_and_get_arg_names(function: Callable[..., None], /) -> Dict[str, type]:
    """
    :param function: eq_function to check
    :return: <function arguments, type>
    """
    function_name = function.__name__
    args = inspect.getfullargspec(function)
    require(f"no varargs in {function_name} parameters, e.g. def func(*x)", args.varargs, require_none)
    require(f"no keyword-only args in {function_name} parameters, e.g. def func(*, kwonly)", args.kwonlyargs,
            require_none)

    return {a: args.annotations.get(a, float) for a in args.args}


def parse_as_expressions(function: Callable[..., None], /) -> List[ast.Expr]:
    """
    Parse eq_function as expressions.
    :param function: eq_function to be parsed
    :return: list of expressions inside the eq_function
    """
    code = inspect.getsource(function)
    node = ast.parse(code).body[0]
    return [n.value for n in node.body]


def corece_to_equality(expr: ast.Expr) -> Tuple[ast.Expr, ast.Expr]:
    """
    :param expr: expression to be coreced
    :return: (left, right) expressions if check pass
    """
    require("expression is a compare", expr, lambda e: isinstance(e, ast.Compare))
    comp: ast.Compare = expr
    op = comp.ops[0]
    require("expression is an equality check (==)", op, lambda o: isinstance(o, ast.Eq))
    return comp.left, comp.comparators[0]


def get_solver_function_code(args: List[str], equalities: List[Tuple[ast.Expr, ast.Expr]]) -> ast.FunctionDef:
    """
    Given a list of arg names and equalty expressions, convert to a single function that scipy.optimize.fsolve understands.
    """
    dimension = len(args)
    require("number of equations are at least number of unknowns", equalities, lambda e: len(e) >= dimension)

    equal_zeroes = [f"{ast.unparse(lhs)}-{ast.unparse(rhs)}" for lhs, rhs in equalities]
    extra_combined = "+".join(f"({exprs})**2" for exprs in equal_zeroes[dimension - 1:])
    args_joined = "_".join(args)

    func_code = f"""\
def pysolvemath({args_joined}):
    {','.join(args)} = {args_joined}
    return {','.join(equal_zeroes[:dimension - 1] + [extra_combined])}
"""
    return ast.parse(func_code).body[0]


def get_solver_function(function_code: ast.FunctionDef) -> Callable[[Tuple], Tuple]:
    """
    Compile a callable function from ast.FunctionDef tree
    """
    code = compile(ast.Module(body=[function_code], type_ignores=[]), filename=__name__, mode="exec")
    locals = {}
    exec(code, globals(), locals)
    return locals[function_code.name]

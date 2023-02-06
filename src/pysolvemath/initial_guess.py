import itertools
from typing import Tuple, Iterable, List

import numpy as np

from .control_flow import or_default_arg


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

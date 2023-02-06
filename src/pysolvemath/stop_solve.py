from typing import Callable

from .control_flow import require


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

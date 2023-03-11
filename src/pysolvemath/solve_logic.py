def is_even(x):
    return x % 2 == 0


def is_magic(x):
    return x in [1, 2, 3, 4]


def solve_logic_query(knowledge, query):
    pass


solve_logic_query([is_even, is_magic], lambda x: is_even(x) and is_magic(x))  # 2, 4

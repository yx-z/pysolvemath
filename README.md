# pysolvemath
Numeric Solver.

## Usage

### Real-valued Equations

```python
from pysolvemath import solve_equations

def equations(x, y):
    x + y == 10
    2 * x == 8


res = solve_equations(equations)  
# res == {"x": 4.0, "y": 6.0}
```

By default, result are of type `float`, representing arbitrary real numbers.

Caller can use type hint of `int` and `fractions.Fraction` to specify unknown to "corerce" to that type. 

```python
from fractions import Fraction
from pysolvemath import solve_equations

def equations(x: int, y, z: Fraction):
    x + z == 1.5
    x**2 == 9
    y + z == 2

res = solve_equations(equations)
# res == {"x": 3, "y": 3.5, "z": -3/2}
```

As this is a numerical solver, this package only gets one (set of) root depending on starting point.

In the example above, we can also derive `{"x": -3, "y": -2.5, "z": 9/2}`, if we start the root finder from negative `x`.

User can proivde `init_guess_func` to specify the starting point.

# pysolvemath
Numeric Solver

## Example

```python
from pysolvemath import solve_equations


def equations(x, y):
    x + y == 10
    2 * x == 8


res = solve_equations(equations)  # {"x": 4, "y": 6}
```
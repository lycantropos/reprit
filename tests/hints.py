from typing import (Callable,
                    TypeVar)

_T = TypeVar('_T')
Operator = Callable[[_T], _T]

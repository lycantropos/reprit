from typing import (Any as _Any,
                    Callable as _Callable)

from .core.hints import Domain as _Domain

FieldSeeker = _Callable[[_Domain, str], _Any]

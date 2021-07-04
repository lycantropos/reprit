from typing import (Any as _Any,
                    Callable as _Callable)

from .core.hints import Domain as _Domain

ArgumentSerializer = _Callable[[_Any], str]
FieldSeeker = _Callable[[_Domain, str], _Any]

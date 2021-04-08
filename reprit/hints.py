from typing import (Any,
                    Callable)

from .core.hints import Domain as _Domain

FieldSeeker = Callable[[_Domain, str], Any]

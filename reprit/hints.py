from typing import (Any,
                    Callable,
                    TypeVar)

Domain = TypeVar('Domain')
Range = TypeVar('Range')
Map = Callable[[Domain], Range]
Operator = Map[Domain, Domain]
Constructor = Callable[..., Domain]
Initializer = Callable[..., None]
FieldSeeker = Callable[[Domain, str], Any]

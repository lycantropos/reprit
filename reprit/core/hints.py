from typing import (Callable,
                    TypeVar,
                    Union)

Domain = TypeVar('Domain')
Range = TypeVar('Range')
Map = Callable[[Domain], Range]
Constructor = Union[Callable[..., Domain], classmethod, staticmethod]
Initializer = Callable[..., None]

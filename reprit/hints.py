from typing import (Callable,
                    TypeVar)

Domain = TypeVar('Domain')
Range = TypeVar('Range')
Map = Callable[[Domain], Range]
Constructor = Callable[..., Domain]
Initializer = Callable[..., None]

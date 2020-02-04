from types import ModuleType
from typing import (Dict,
                    Tuple,
                    Type,
                    TypeVar,
                    Union)

from hypothesis.strategies import SearchStrategy

from reprit.hints import (Constructor,
                          Initializer)

Domain = TypeVar('Domain')
Strategy = SearchStrategy
Method = Union[Constructor, Initializer]
ClassMethodInstance = Tuple[Type[Domain], Method, Domain]


def identity(value: Domain) -> Domain:
    return value


def to_namespace(object_path: str, object_: Domain
                 ) -> Dict[str, Union[Domain, ModuleType]]:
    object_path_parts = object_path.split('.')
    if len(object_path_parts) == 1:
        return {object_path_parts[0]: object_}
    step_module = ModuleType(object_path_parts[0])
    result = {object_path_parts[0]: step_module}
    for part in object_path_parts[1:-1]:
        next_step_module = ModuleType(part)
        setattr(step_module, part, next_step_module)
        step_module = next_step_module
    setattr(step_module, object_path_parts[-1], object_)
    return result

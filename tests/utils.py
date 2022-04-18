import builtins
from enum import _is_dunder
from itertools import chain
from types import (MethodType,
                   ModuleType,
                   SimpleNamespace)
from typing import (Any,
                    Dict,
                    Tuple,
                    Type,
                    TypeVar,
                    Union)

from hypothesis.strategies import SearchStrategy

from reprit.core.hints import (Constructor,
                               Initializer)

Domain = TypeVar('Domain')
Strategy = SearchStrategy
Method = Union[Constructor, Initializer]
ClassMethodInstance = Tuple[Type[Domain], Method, Domain]
Namespace = Dict[str, Union[Domain, ModuleType]]

test_types_module = SimpleNamespace()
test_types_module.__name__ = 'test_types'

base_namespace = {builtins.__name__: builtins,
                  test_types_module.__name__: test_types_module}


def are_objects_equivalent(left: Any, right: Any) -> bool:
    left_dict, right_dict = vars(left), vars(right)
    return (type(left) is type(right)
            and left_dict.keys() == right_dict.keys()
            and all(value() == right_dict[key]()
                    if isinstance(value, MethodType)
                    else value == right_dict[key]
                    for key, value in left_dict.items()))


flatten = chain.from_iterable


def is_not_dunder(name: str) -> bool:
    return not _is_dunder(name)


def identity(value: Domain) -> Domain:
    return value


def to_namespace(object_path: str, object_: Domain) -> Namespace:
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

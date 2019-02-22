import inspect
from types import ModuleType
from typing import (Dict,
                    List,
                    Union)

from hypothesis import strategies

from .factories import (to_characters,
                        to_dictionaries,
                        to_homogeneous_frozensets,
                        to_homogeneous_sequences,
                        to_homogeneous_sets,
                        to_homogeneous_tuples,
                        to_strings)

Serializable = Union[None, bool, float, int, str]
Serializable = Union[Dict[str, Serializable], List[Serializable]]

booleans = strategies.booleans()
integers = (booleans
            | strategies.integers())
real_numbers = (integers
                | strategies.floats(allow_nan=False,
                                    allow_infinity=False))
numbers = (real_numbers
           | strategies.complex_numbers(allow_nan=False,
                                        allow_infinity=False))
scalars = (strategies.none()
           | strategies.just(NotImplemented)
           | strategies.just(Ellipsis)
           | numbers)
strings = to_strings(to_characters())


def module_to_classes(module: ModuleType) -> List[type]:
    return list(filter(inspect.isclass,
                       vars(module).values()))


deferred_hashables = strategies.deferred(lambda: hashables)
deferred_objects = strategies.deferred(lambda: objects)
hashables = (scalars
             | strings
             | to_homogeneous_frozensets(deferred_hashables)
             | to_homogeneous_tuples(deferred_hashables))
iterables = (strings
             | to_homogeneous_sequences(deferred_objects))
sets = to_homogeneous_sets(hashables)
objects = (hashables
           | iterables
           | sets
           | to_dictionaries(hashables, deferred_objects))

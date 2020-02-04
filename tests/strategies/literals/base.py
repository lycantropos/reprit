import inspect
from types import ModuleType
from typing import (Dict,
                    List,
                    Union)

from hypothesis import strategies

from tests.configs import MAX_ALIKE_PARAMETERS_COUNT
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
    return list(filter(inspect.isclass, vars(module).values()))


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

alike_parameters_counts = strategies.integers(0, MAX_ALIKE_PARAMETERS_COUNT)

simple_class_field_name_factories = strategies.just(lambda name: name)
complex_class_field_name_factories = (
        simple_class_field_name_factories
        | strategies.sampled_from([lambda name: '_' + name.lstrip('_'),
                                   lambda name: name.rstrip('_') + '_']))

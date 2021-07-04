import builtins
import inspect
from types import ModuleType
from typing import (Any,
                    Dict,
                    List,
                    Union)

from hypothesis import strategies

from reprit import serializers
from tests.configs import MAX_ALIKE_PARAMETERS_COUNT
from tests.utils import flatten
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
built_ins = vars(builtins).values()
built_in_callables = list(filter(callable, built_ins))
built_in_classes = [callable_
                    for callable_ in built_in_callables
                    if isinstance(callable_, type)]
built_in_classes_fields = list(flatten(vars(class_).values()
                                       for class_ in built_in_classes))


def round_trippable_built_in(object_: Any) -> bool:
    try:
        candidate = eval(serializers.complex_(object_),
                         {builtins.__name__: builtins})
    except Exception:
        return False
    else:
        return candidate is object_


objects = (
        hashables
        | iterables
        | sets
        | to_dictionaries(hashables, deferred_objects)
        | (strategies.sampled_from(built_in_callables
                                   + built_in_classes_fields)
           .filter(round_trippable_built_in)))
alike_parameters_counts = strategies.integers(0, MAX_ALIKE_PARAMETERS_COUNT)
simple_class_field_name_factories = strategies.just(lambda name: name)
complex_class_field_name_factories = (
        simple_class_field_name_factories
        | strategies.sampled_from([lambda name: '_' + name.lstrip('_'),
                                   lambda name: name.rstrip('_') + '_']))

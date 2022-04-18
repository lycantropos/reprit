import builtins
import inspect
from enum import (Enum,
                  EnumMeta,
                  _is_dunder,
                  _is_sunder)
from types import ModuleType
from typing import (Any,
                    Callable,
                    Dict,
                    Hashable,
                    List,
                    Optional,
                    Sequence,
                    Union)

from hypothesis import strategies

from reprit import serializers
from tests.configs import MAX_ALIKE_PARAMETERS_COUNT
from tests.utils import (Strategy,
                         flatten)
from .factories import (to_characters,
                        to_dictionaries,
                        to_homogeneous_frozensets,
                        to_homogeneous_sequences,
                        to_homogeneous_sets,
                        to_homogeneous_tuples,
                        to_strings)
from .identifiers import any_identifiers

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
memory_views = strategies.builds(memoryview, strategies.binary())


def module_to_classes(module: ModuleType) -> List[type]:
    return list(filter(inspect.isclass, vars(module).values()))


deferred_hashables = strategies.deferred(lambda: hashables)
deferred_objects = strategies.deferred(lambda: objects)

Bases = Sequence[type]
UniqueBy = Callable[[Any], Hashable]


def is_valid_key(key: str) -> bool:
    return not is_invalid_key(key) and not _is_dunder(key)


def is_invalid_key(key: str) -> bool:
    return _is_sunder(key) or key == type.mro.__name__


def to_enum_types(*,
                  names: Strategy[str] = any_identifiers,
                  bases: Strategy[Bases]
               = strategies.tuples(strategies.just(Enum)),
                  keys: Strategy[str] = any_identifiers.filter(is_valid_key),
                  values: Strategy[Any],
                  min_size: int = 0,
                  max_size: Optional[int] = None) -> Strategy[EnumMeta]:
    contents = strategies.dictionaries(keys, values,
                                       min_size=min_size,
                                       max_size=max_size)
    return strategies.builds(_to_enum, names, bases, contents)


def _to_enum(name: str, bases: Bases, contents: Dict[str, Any]) -> EnumMeta:
    result = EnumMeta(name, bases, _to_enum_contents(name, bases, contents))
    result.__module__ = '_' + str(hash(result)).replace('-', '_')
    return result


def _to_enum_contents(name: str,
                      bases: Bases,
                      contents: Dict[str, Any]) -> Dict[str, Any]:
    result = EnumMeta.__prepare__(name, bases)
    # can't use `update` method because `_EnumDict` overloads `__setitem__`
    for name, content in contents.items():
        result[name] = content
    return result


hashables = (scalars
             | strings
             | to_homogeneous_frozensets(deferred_hashables)
             | to_homogeneous_tuples(deferred_hashables))
iterables = (strings
             | memory_views
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


objects = (hashables
           | iterables
           | sets
           | to_dictionaries(hashables, deferred_objects)
           | (strategies.sampled_from(built_in_callables
                                      + built_in_classes_fields)
              .filter(round_trippable_built_in)))
enum_types = to_enum_types(values=objects,
                           min_size=1)
enums = enum_types.map(list).flatmap(strategies.sampled_from)
alike_parameters_counts = strategies.integers(0, MAX_ALIKE_PARAMETERS_COUNT)
simple_class_field_name_factories = strategies.just(lambda name: name)
complex_class_field_name_factories = (
        simple_class_field_name_factories
        | strategies.sampled_from([lambda name: '_' + name.lstrip('_'),
                                   lambda name: name.rstrip('_') + '_']))

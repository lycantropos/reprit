import re
from functools import partial
from typing import (Any,
                    Tuple,
                    Type)

from hypothesis import strategies

from reprit.hints import Domain
from tests.utils import Strategy
from .factories import (to_classes,
                        to_initializers,
                        to_instances)
from .literals import identifiers
from .literals.base import (alike_parameters_counts,
                            complex_class_field_name_factories,
                            objects,
                            simple_class_field_name_factories)

simple_classes_methods = strategies.fixed_dictionaries(
        {'__init__': to_initializers(
                parameters_names=identifiers.snake_case,
                field_name_factories=simple_class_field_name_factories)})
simple_classes = to_classes(names=identifiers.pascal_case,
                            bases=strategies.tuples(),
                            namespaces=simple_classes_methods)
to_alphanumeric_characters = partial(re.compile(r'[^a-zA-Z0-9]').sub, '')
complex_classes_methods = strategies.fixed_dictionaries(
        {'__init__': to_initializers(
                parameters_names=identifiers.snake_case,
                # prevents names clashes
                # with underscored attributes
                # like ``b``, ``_b``, ``b_`` and so on
                parameters_names_unique_by=to_alphanumeric_characters,
                field_name_factories=complex_class_field_name_factories)})
complex_classes = to_classes(names=identifiers.pascal_case,
                             bases=strategies.tuples(),
                             namespaces=complex_classes_methods)


class Unsupported:
    def __init__(self, a, a_):
        self._a = a
        self.a_ = a_


unsupported_complex_classes = strategies.just(Unsupported)


def to_classes_with_instances(cls: Type[Domain]
                              ) -> Strategy[Tuple[Type[Domain], Domain]]:
    instances = to_instances(
            cls=cls,
            values={Any: objects},
            variadic_positionals_counts=alike_parameters_counts,
            variadic_keywords_names=identifiers.snake_case,
            variadic_keywords_counts=alike_parameters_counts)
    return strategies.tuples(strategies.just(cls), instances)


simple_classes_with_instances = (simple_classes
                                 .flatmap(to_classes_with_instances))
complex_classes_with_instances = (complex_classes
                                  .flatmap(to_classes_with_instances))
unsupported_complex_classes_with_instances = (
    unsupported_complex_classes.flatmap(to_classes_with_instances))

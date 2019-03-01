import re
from functools import partial
from typing import (Any,
                    Type)

import pytest
from hypothesis.strategies import just

from tests import strategies
from tests.utils import (Domain,
                         find)


@pytest.fixture(scope='function')
def simple_class() -> Type[Domain]:
    initializers_strategy = strategies.to_initializers(
            parameters_names=strategies.snake_case_identifiers,
            field_name_factories=strategies.simple_class_field_name_factories,
            positionals_or_keywords_counts=strategies.parameters_counts,
            variadic_positional_flags=strategies.booleans,
            keywords_only_counts=strategies.parameters_counts,
            variadic_keyword_flags=strategies.booleans)
    methods_strategies = {'__init__': initializers_strategy}
    return find(strategies.to_classes(
            names=strategies.pascal_case_identifiers,
            bases=strategies.to_tuples(),
            namespaces=(strategies.to_fixed_dictionaries(methods_strategies))))


@pytest.fixture(scope='function')
def simple_instance(simple_class: Type[Domain]) -> Domain:
    return find(strategies.to_instances(
            classes=just(simple_class),
            values={Any: strategies.objects},
            variadic_positionals_counts=strategies.parameters_counts,
            variadic_keywords_names=strategies.snake_case_identifiers,
            variadic_keywords_counts=strategies.parameters_counts))


@pytest.fixture(scope='function')
def complex_class() -> Type[Domain]:
    to_alphanumeric_characters = partial(re.compile(r'[^a-zA-Z0-9]').sub, '')
    initializers_strategy = strategies.to_initializers(
            parameters_names=strategies.snake_case_identifiers,
            # prevents names clashes
            # with underscored attributes
            # like ``b``, ``_b``, ``b_`` and so on
            parameters_names_unique_by=to_alphanumeric_characters,
            field_name_factories=strategies.complex_class_field_name_factories,
            positionals_or_keywords_counts=strategies.parameters_counts,
            variadic_positional_flags=strategies.booleans,
            keywords_only_counts=strategies.parameters_counts,
            variadic_keyword_flags=strategies.booleans)
    methods_strategies = {'__init__': initializers_strategy}
    return find(strategies.to_classes(
            names=strategies.pascal_case_identifiers,
            bases=strategies.to_tuples(),
            namespaces=(strategies.to_fixed_dictionaries(methods_strategies))))


@pytest.fixture(scope='function')
def unsupported_complex_class() -> Type[Domain]:
    class Unsupported:
        def __init__(self, a, a_):
            self._a = a
            self.a_ = a_

    return Unsupported


@pytest.fixture(scope='function')
def complex_instance(complex_class: Type[Domain]) -> Domain:
    return find(strategies.to_instances(
            classes=just(complex_class),
            values={Any: strategies.objects},
            variadic_positionals_counts=strategies.parameters_counts,
            variadic_keywords_names=strategies.snake_case_identifiers,
            variadic_keywords_counts=strategies.parameters_counts))


@pytest.fixture(scope='function')
def unsupported_complex_instance(unsupported_complex_class: Type[Domain]
                                 ) -> Type[Domain]:
    return find(strategies.to_instances(
            classes=just(unsupported_complex_class),
            values={Any: strategies.objects},
            variadic_positionals_counts=strategies.parameters_counts,
            variadic_keywords_names=strategies.snake_case_identifiers,
            variadic_keywords_counts=strategies.parameters_counts))

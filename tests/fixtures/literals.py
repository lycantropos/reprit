import inspect
import re
from functools import partial
from typing import (Any,
                    Type)

import pytest
from hypothesis.strategies import just

from tests import strategies
from tests.configs import (MAX_ITERABLES_SIZE,
                           MAX_PARAMETERS_COUNT)
from tests.utils import (Domain,
                         Strategy,
                         find)


@pytest.fixture(scope='function')
def simple_class(parameters_counts: Strategy[int]) -> Type[Domain]:
    initializers_strategy = strategies.to_initializers(
            parameters_names=strategies.snake_case_identifiers,
            field_name_factories=strategies.simple_class_field_name_factories,
            positionals_or_keywords_counts=parameters_counts,
            variadic_positional_flags=strategies.booleans,
            keywords_only_counts=parameters_counts,
            variadic_keyword_flags=strategies.booleans)
    methods_strategies = {'__init__': initializers_strategy}
    return find(strategies.to_classes(
            names=strategies.pascal_case_identifiers,
            bases=strategies.to_tuples(),
            namespaces=(strategies.to_fixed_dictionaries(methods_strategies))))


@pytest.fixture(scope='function')
def simple_instance(simple_class: Type[Domain],
                    parameters_counts: Strategy[int]) -> Domain:
    return find(strategies.to_instances(
            classes=just(simple_class),
            values={Any: strategies.objects},
            variadic_positionals_counts=parameters_counts,
            variadic_keywords_names=strategies.snake_case_identifiers,
            variadic_keywords_counts=parameters_counts))


@pytest.fixture(scope='function')
def complex_class(parameters_counts: Strategy[int]) -> Type[Domain]:
    to_alphanumeric_characters = partial(re.compile(r'[^a-zA-Z0-9]').sub, '')
    initializers_strategy = strategies.to_initializers(
            parameters_names=strategies.snake_case_identifiers,
            # prevents names clashes
            # with underscored attributes
            # like ``b``, ``_b``, ``b_`` and so on
            parameters_names_unique_by=to_alphanumeric_characters,
            field_name_factories=strategies.complex_class_field_name_factories,
            positionals_or_keywords_counts=parameters_counts,
            variadic_positional_flags=strategies.booleans,
            keywords_only_counts=parameters_counts,
            variadic_keyword_flags=strategies.booleans)
    methods_strategies = {'__init__': initializers_strategy}
    return find(strategies.to_classes(
            names=strategies.pascal_case_identifiers,
            bases=strategies.to_tuples(),
            namespaces=(strategies.to_fixed_dictionaries(methods_strategies))))


@pytest.fixture(scope='function')
def complex_instance(complex_class: Type[Domain],
                     parameters_counts: Strategy[int]) -> Domain:
    return find(strategies.to_instances(
            classes=just(complex_class),
            values={Any: strategies.objects},
            variadic_positionals_counts=parameters_counts,
            variadic_keywords_names=strategies.snake_case_identifiers,
            variadic_keywords_counts=parameters_counts))


@pytest.fixture(scope='session')
def parameters_counts() -> Strategy[int]:
    max_parameters_count = min(MAX_ITERABLES_SIZE
                               // len(inspect._ParameterKind),
                               MAX_PARAMETERS_COUNT)
    return strategies.to_integers(0, max_parameters_count)

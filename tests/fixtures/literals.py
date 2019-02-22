import inspect
from typing import (Any,
                    Type)

import pytest
from hypothesis.strategies import just

from tests import strategies
from tests.configs import MAX_ITERABLES_SIZE
from tests.utils import (Domain,
                         Strategy,
                         find)


@pytest.fixture(scope='function')
def cls(parameters_counts: Strategy[int]) -> Type[Domain]:
    initializers_strategy = strategies.to_initializers(
            parameters_names=strategies.snake_case_identifiers,
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
def instance(cls: Type[Domain],
             parameters_counts: Strategy[int]) -> Domain:
    return find(strategies.to_instances(
            classes=just(cls),
            values={Any: strategies.objects},
            variadic_positionals_counts=parameters_counts,
            variadic_keywords_names=strategies.snake_case_identifiers,
            variadic_keywords_counts=parameters_counts))


@pytest.fixture(scope='session')
def parameters_counts() -> Strategy[int]:
    max_parameters_count = MAX_ITERABLES_SIZE // len(inspect._ParameterKind)
    return strategies.to_integers(0, max_parameters_count)

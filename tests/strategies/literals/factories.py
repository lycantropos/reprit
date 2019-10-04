from functools import wraps
from typing import (Callable,
                    Optional,
                    Sequence,
                    Tuple)

from hypothesis import strategies

from tests.configs import MAX_ITERABLES_SIZE
from tests.utils import (Domain,
                         Strategy)

to_characters = strategies.characters


def limit_max_size(factory: Callable[..., Strategy[Domain]]):
    @wraps(factory)
    def limited(*args, max_size: int = MAX_ITERABLES_SIZE, **kwargs
                ) -> Strategy[Domain]:
        return factory(*args, max_size=max_size, **kwargs)

    return limited


to_dictionaries = limit_max_size(strategies.dictionaries)
to_homogeneous_frozensets = limit_max_size(strategies.frozensets)
to_homogeneous_lists = limit_max_size(strategies.lists)


@limit_max_size
def to_homogeneous_sequences(elements: Optional[Strategy[Domain]] = None,
                             *,
                             min_size: int = 0,
                             max_size: Optional[int] = None
                             ) -> Strategy[Sequence[Domain]]:
    return (to_homogeneous_lists(elements,
                                 min_size=min_size,
                                 max_size=max_size)
            | to_homogeneous_tuples(elements,
                                    min_size=min_size,
                                    max_size=max_size))


to_homogeneous_sets = limit_max_size(strategies.sets)


@limit_max_size
def to_homogeneous_tuples(elements: Optional[Strategy[Domain]] = None,
                          *,
                          min_size: int = 0,
                          max_size: Optional[int] = None
                          ) -> Strategy[Tuple[Domain, ...]]:
    return (to_homogeneous_lists(elements,
                                 min_size=min_size,
                                 max_size=max_size)
            .map(tuple))


to_strings = limit_max_size(strategies.text)

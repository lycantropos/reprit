from collections import defaultdict
from typing import (Iterable,
                    List,
                    Tuple)

from .hints import (Domain,
                    Map,
                    Range)


def group_by(iterable: Iterable[Domain],
             *,
             key: Map[Domain, Range] = lambda x: x
             ) -> Iterable[Tuple[Range, List[Domain]]]:
    result = defaultdict(list)
    for element in iterable:
        result[key(element)].append(element)
    return result.items()

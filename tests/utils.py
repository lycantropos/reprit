from types import ModuleType
from typing import (Any,
                    Dict,
                    TypeVar,
                    Union)

from hypothesis import (Phase,
                        core,
                        settings)
from hypothesis.errors import (NoSuchExample,
                               Unsatisfiable)
from hypothesis.searchstrategy import SearchStrategy

Domain = TypeVar('Domain')
Strategy = SearchStrategy


def find(strategy: Strategy[Domain]) -> Domain:
    first_object_list = []

    def condition(object_: Any) -> bool:
        if first_object_list:
            return True
        else:
            first_object_list.append(object_)
            return False

    try:
        return core.find(strategy,
                         condition,
                         settings=settings(database=None,
                                           phases=tuple(set(Phase)
                                                        - {Phase.shrink})))
    except (NoSuchExample, Unsatisfiable) as search_error:
        try:
            result, = first_object_list
        except ValueError as unpacking_error:
            raise unpacking_error from search_error
        else:
            return result


def to_namespace(object_path: str, object_: Domain
                 ) -> Dict[str, Union[Domain, ModuleType]]:
    object_path_parts = object_path.split('.')
    if len(object_path_parts) == 1:
        return {object_path_parts[0]: object_}
    step_module = ModuleType(object_path_parts[0])
    result = {object_path_parts[0]: step_module}
    for part in object_path_parts[1:-1]:
        next_step_module = ModuleType(part)
        setattr(step_module, part, next_step_module)
        step_module = next_step_module
    setattr(step_module, object_path_parts[-1], object_)
    return result

import ast
import inspect
import sys
from collections import OrderedDict
from functools import partial
from itertools import (chain,
                       islice,
                       repeat)
from operator import ne
from types import MethodType
from typing import (Any,
                    Callable,
                    Dict,
                    List,
                    Tuple,
                    Type)

from hypothesis import strategies

from reprit.hints import (Initializer,
                          Map,
                          Operator)
from tests.configs import MAX_PARAMETERS_COUNT
from tests.utils import (Domain,
                         Strategy)
from .literals.factories import (to_dictionaries,
                                 to_homogeneous_lists)


def to_classes(*,
               names: Strategy[str],
               bases: Strategy[Tuple[type, ...]],
               namespaces: Strategy[Dict[str, MethodType]]
               ) -> Strategy[Type[Domain]]:
    return strategies.builds(type, names, bases, namespaces)


SELF_PARAMETER_NAME = 'self'


def to_initializers(*,
                    parameters_names: Strategy[str],
                    parameters_names_unique_by: Map[str, int] = lambda x: x,
                    field_name_factories: Strategy[Operator[str]]
                    ) -> Strategy[Initializer]:
    parameters_names_lists = strategies.lists(
            parameters_names.filter(partial(ne,
                                            SELF_PARAMETER_NAME)),
            max_size=MAX_PARAMETERS_COUNT,
            unique_by=parameters_names_unique_by)
    signature_data = parameters_names_lists.flatmap(_to_signature_data)
    return strategies.builds(_to_initializer,
                             signature_data,
                             field_name_factories)


def _to_signature_data(names: List[str]
                       ) -> Strategy[Dict[inspect._ParameterKind, List[str]]]:
    if not names:
        parameters_counters = strategies.builds(OrderedDict)
    elif len(names) == 1:
        kinds = set(inspect._ParameterKind)
        if sys.version_info < (3, 8):
            kinds -= {inspect._POSITIONAL_ONLY}
        parameters_counters = strategies.sampled_from([OrderedDict([(kind, 1)])
                                                       for kind in kinds])
    else:
        max_counts = (len(names) - 2) // (2
                                          if sys.version_info < (3, 8)
                                          else 3)
        counts = strategies.integers(0, max_counts)
        variants = OrderedDict()
        if sys.version_info >= (3, 8):
            variants[inspect._POSITIONAL_ONLY] = counts
        variants[inspect._POSITIONAL_OR_KEYWORD] = counts
        variants[inspect._VAR_POSITIONAL] = strategies.booleans()
        variants[inspect._KEYWORD_ONLY] = counts
        variants[inspect._VAR_KEYWORD] = strategies.booleans()
        parameters_counters = strategies.fixed_dictionaries(variants)

    def select(counter: Dict[inspect._ParameterKind, int]
               ) -> Dict[inspect._ParameterKind, List[str]]:
        names_iterator = iter(names)
        return OrderedDict((kind, list(islice(names_iterator, count)))
                           for kind, count in counter.items()
                           if count)

    return parameters_counters.map(select)


def _to_initializer(signature_data: Dict[inspect._ParameterKind, List[str]],
                    field_name_factory):
    def to_parameter(name: str) -> ast.arg:
        return ast.arg(name, None)

    positionals_or_keywords_nodes = (
            [ast.arg(SELF_PARAMETER_NAME, None)]
            + [to_parameter(name)
               for name in signature_data.get(inspect._POSITIONAL_OR_KEYWORD,
                                              [])])
    if inspect._VAR_POSITIONAL in signature_data:
        variadic_positional_name, = signature_data[inspect._VAR_POSITIONAL]
        variadic_positional_node = to_parameter(variadic_positional_name)
    else:
        variadic_positional_node = None
    keyword_only_parameters_names = signature_data.get(inspect._KEYWORD_ONLY,
                                                       [])
    keywords_only_nodes = [to_parameter(name)
                           for name in keyword_only_parameters_names]
    if inspect._VAR_KEYWORD in signature_data:
        variadic_keyword_name, = signature_data[inspect._VAR_KEYWORD]
        variadic_keyword_node = to_parameter(variadic_keyword_name)
    else:
        variadic_keyword_node = None
    positionals_or_keywords_defaults = []
    keywords_only_defaults = list(repeat(None,
                                         len(keyword_only_parameters_names)))
    signature = ast.arguments(positionals_or_keywords_nodes,
                              variadic_positional_node,
                              keywords_only_nodes,
                              keywords_only_defaults,
                              variadic_keyword_node,
                              positionals_or_keywords_defaults)
    if signature_data:
        body = [ast.Assign([ast.Attribute(ast.Name(SELF_PARAMETER_NAME,
                                                   ast.Load()),
                                          field_name_factory
                                          (parameter_name),
                                          ast.Store())],
                           ast.Name(parameter_name, ast.Load()))
                for parameter_name in chain.from_iterable(signature_data
                                                          .values())]
    else:
        body = [ast.Pass()]
    name = '__init__'
    function_node = ast.FunctionDef(name, signature, body, [], None)
    tree = ast.fix_missing_locations(ast.Module([function_node]))
    code = compile(tree, '<ast>', 'exec')
    namespace = {}
    exec(code, namespace)
    return namespace[name]


def to_instances(cls: Type[Domain],
                 values: Dict[Type[Domain], Strategy[Domain]],
                 variadic_positionals_counts: Strategy[int],
                 variadic_keywords_names: Strategy[str],
                 variadic_keywords_counts: Strategy[int]) -> Strategy[Domain]:
    def unpack_arguments(arguments: Tuple[Tuple[Any, ...],
                                          Dict[str, Any]]) -> Domain:
        positionals, keywords = arguments
        return cls(*positionals, **keywords)

    return (to_method_arguments(
            method=cls.__init__,
            values=values,
            variadic_positionals_counts=variadic_positionals_counts,
            variadic_keywords_names=variadic_keywords_names,
            variadic_keywords_counts=variadic_keywords_counts)
            .map(unpack_arguments))


@strategies.composite
def to_method_arguments(draw: Callable[[Strategy[Domain]], Domain],
                        *,
                        method: Callable,
                        values: Dict[Type[Domain], Strategy[Domain]],
                        variadic_positionals_counts: Strategy[int],
                        variadic_keywords_names: Strategy[str],
                        variadic_keywords_counts: Strategy[int]
                        ) -> Strategy[Tuple[Tuple[Any, ...], Dict[str, Any]]]:
    signature = inspect.signature(method)
    parameters = OrderedDict(signature.parameters)
    parameters.popitem(0)
    positionals = []
    keywords = {}
    for parameter in parameters.values():  # type: inspect.Parameter
        parameter_annotation = parameter.annotation
        parameter_default = parameter.default
        if parameter_annotation is inspect._empty:
            parameter_annotation = Any
        parameter_values = values[parameter_annotation]
        if parameter_default is not inspect._empty:
            parameter_values |= strategies.just(parameter_default)
        parameter_kind = parameter.kind
        if (parameter_kind is inspect._POSITIONAL_ONLY
                or parameter_kind is inspect._POSITIONAL_OR_KEYWORD):
            positionals.append(draw(parameter_values))
        elif parameter_kind is inspect._VAR_POSITIONAL:
            def count_to_values(count: int) -> Strategy[Any]:
                return to_homogeneous_lists(parameter_values,
                                            min_size=count,
                                            max_size=count)

            positionals.extend(draw(variadic_positionals_counts
                                    .flatmap(count_to_values)))
        elif parameter_kind is inspect._KEYWORD_ONLY:
            keywords[parameter.name] = draw(parameter_values)
        else:
            def count_to_values(count: int) -> Strategy[Dict[str, Any]]:
                return to_dictionaries(variadic_keywords_names
                                       .filter(is_parameter_name_vacant),
                                       parameter_values,
                                       min_size=count,
                                       max_size=count)

            def is_parameter_name_vacant(name: str) -> bool:
                return name not in parameters

            keywords.update(draw(variadic_keywords_counts
                                 .flatmap(count_to_values)))
    return tuple(positionals), keywords

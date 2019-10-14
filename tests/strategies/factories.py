import ast
import inspect
from collections import OrderedDict
from functools import partial
from itertools import (islice,
                       repeat)
from operator import ne
from types import MethodType
from typing import (Any,
                    Callable,
                    Dict,
                    Tuple,
                    Type)

from hypothesis import strategies

from reprit.hints import (Initializer,
                          Map,
                          Operator)
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


@strategies.composite
def to_initializers(
        draw: Callable[[Strategy[Domain]], Domain],
        *,
        names: Strategy[str] = strategies.just('__init__'),
        self_parameters_names: Strategy[str] = strategies.just('self'),
        parameters_names: Strategy[str],
        parameters_names_unique_by: Map[str, int] = lambda x: x,
        field_name_factories: Strategy[Operator[str]],
        positionals_or_keywords_counts: Strategy[int],
        variadic_positional_flags: Strategy[bool],
        keywords_only_counts: Strategy[int],
        variadic_keyword_flags: Strategy[bool]) -> Strategy[Initializer]:
    name = draw(names)
    self_parameter_name = draw(self_parameters_names)
    positionals_or_keywords_count = draw(positionals_or_keywords_counts)
    has_variadic_positional = draw(variadic_positional_flags)
    keywords_only_count = draw(keywords_only_counts)
    has_variadic_keyword = draw(variadic_keyword_flags)
    rest_parameters_count = (positionals_or_keywords_count
                             + has_variadic_positional
                             + keywords_only_count
                             + has_variadic_keyword)
    rest_parameters_names = draw(strategies
                                 .lists(parameters_names
                                        .filter(partial(ne,
                                                        self_parameter_name)),
                                        min_size=rest_parameters_count,
                                        max_size=rest_parameters_count,
                                        unique_by=parameters_names_unique_by))
    rest_parameters_nodes = (ast.arg(parameter_name, None)
                             for parameter_name in rest_parameters_names)
    positionals_or_keywords_nodes = (
            [ast.arg(self_parameter_name, None)]
            + list(islice(rest_parameters_nodes,
                          positionals_or_keywords_count)))
    if has_variadic_positional:
        variadic_positional_node = next(rest_parameters_nodes)
    else:
        variadic_positional_node = None
    keywords_only_nodes = list(islice(rest_parameters_nodes,
                                      keywords_only_count))
    variadic_keyword_node = next(rest_parameters_nodes, None)
    positionals_or_keywords_defaults = []
    keywords_only_defaults = list(repeat(None,
                                         times=keywords_only_count))
    signature = ast.arguments(positionals_or_keywords_nodes,
                              variadic_positional_node,
                              keywords_only_nodes,
                              keywords_only_defaults,
                              variadic_keyword_node,
                              positionals_or_keywords_defaults)
    if rest_parameters_names:
        body = [ast.Assign([ast.Attribute(ast.Name(self_parameter_name,
                                                   ast.Load()),
                                          draw(field_name_factories)
                                          (parameter_name),
                                          ast.Store())],
                           ast.Name(parameter_name, ast.Load()))
                for parameter_name in rest_parameters_names]
    else:
        body = [ast.Pass()]
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

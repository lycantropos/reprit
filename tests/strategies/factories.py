import ast
import inspect
import sys
import types
from collections import OrderedDict
from functools import partial
from itertools import (chain,
                       islice,
                       product,
                       repeat)
from operator import (itemgetter,
                      ne)
from types import (FunctionType,
                   MethodType)
from typing import (Any,
                    Callable,
                    Dict,
                    List,
                    Sequence,
                    Tuple,
                    Type)

from hypothesis import strategies

from reprit.core.hints import (Constructor,
                               Initializer,
                               Map)
from tests.configs import MAX_PARAMETERS_COUNT
from tests.hints import Operator
from tests.utils import (Domain,
                         Strategy,
                         identity,
                         is_not_dunder)
from .literals import identifiers
from .literals.factories import (to_dictionaries,
                                 to_homogeneous_lists)

flatten = chain.from_iterable
booleans = strategies.booleans()


def to_count_with_flags(count: int) -> Strategy[Tuple[int, List[bool]]]:
    return strategies.tuples(strategies.just(count),
                             strategies.lists(booleans,
                                              min_size=count,
                                              max_size=count))


def to_classes(*,
               names: Strategy[str] = identifiers.pascal_case,
               bases: Strategy[Tuple[type, ...]],
               namespaces: Strategy[Dict[str, MethodType]]
               ) -> Strategy[Type[Domain]]:
    return strategies.builds(type, names, bases, namespaces)


SignatureData = Dict[inspect._ParameterKind, List[Tuple[str, bool]]]

DEFAULT_CONSTRUCTOR_NAME = '__new__'
INITIALIZER_NAME = '__init__'
SELF_PARAMETER_NAME = 'self'
CLASS_PARAMETER_NAME = 'cls'
TYPES_MODULE_NAME = types.__name__
TYPES_MODULE_ALIAS = '@' + TYPES_MODULE_NAME

PRE_PYTHON_3_8 = sys.version_info < (3, 8)


def to_constructors_with_initializers(
        *,
        parameters_names: Strategy[str] = identifiers.snake_case,
        parameters_names_unique_by: Map[str, int] = identity,
        field_name_factories: Strategy[Operator[str]]
) -> Strategy[Tuple[Constructor, Initializer]]:
    parameters_names_lists = strategies.lists(
            parameters_names.filter(lambda name:
                                    name not in (SELF_PARAMETER_NAME,
                                                 DEFAULT_CONSTRUCTOR_NAME)),
            max_size=MAX_PARAMETERS_COUNT,
            unique_by=parameters_names_unique_by)
    signatures_data = parameters_names_lists.flatmap(_to_signature_data)
    return strategies.builds(_to_constructor_with_initializer,
                             signatures_data, field_name_factories)


def to_custom_constructors_with_initializers(
        *,
        names: Strategy[str] = identifiers.snake_case.filter(is_not_dunder),
        parameters_names: Strategy[str] = identifiers.snake_case,
        parameters_names_unique_by: Map[str, int] = identity,
        field_name_factories: Strategy[Operator[str]]
) -> Strategy[Tuple[Constructor, Initializer]]:
    parameters_names_lists = strategies.lists(
            parameters_names.filter(lambda name:
                                    name not in (SELF_PARAMETER_NAME,
                                                 DEFAULT_CONSTRUCTOR_NAME)),
            max_size=MAX_PARAMETERS_COUNT,
            unique_by=parameters_names_unique_by)
    signatures_data = parameters_names_lists.flatmap(_to_signature_data)

    def to_names_with_signatures_data(signature_data: SignatureData
                                      ) -> Strategy[Tuple[str, SignatureData]]:
        used_names = frozenset(map(itemgetter(0),
                                   flatten(signature_data.values())))
        return strategies.tuples(names.filter(lambda name:
                                              name not in used_names),
                                 strategies.just(signature_data))

    names_with_signatures_data = (signatures_data
                                  .flatmap(to_names_with_signatures_data))
    return strategies.builds(_to_custom_constructor_with_initializer,
                             names_with_signatures_data, field_name_factories)


def to_initializers(*,
                    parameters_names: Strategy[str] = identifiers.snake_case,
                    parameters_names_unique_by: Map[str, int] = identity,
                    field_name_factories: Strategy[Operator[str]]
                    ) -> Strategy[Initializer]:
    parameters_names_lists = strategies.lists(
            parameters_names.filter(partial(ne, SELF_PARAMETER_NAME)),
            max_size=MAX_PARAMETERS_COUNT,
            unique_by=parameters_names_unique_by)
    signatures_data = parameters_names_lists.flatmap(_to_signature_data)
    return strategies.builds(_to_initializer, signatures_data,
                             field_name_factories)


def _to_signature_data(names: List[str]) -> Strategy[SignatureData]:
    if not names:
        parameters_counters = strategies.builds(OrderedDict)
    elif len(names) == 1:
        kinds = set(inspect._ParameterKind)
        if PRE_PYTHON_3_8:
            kinds -= {inspect._POSITIONAL_ONLY}
        parameters_counters = strategies.sampled_from(
                [OrderedDict([(kind, (1, [is_callable]))])
                 for kind, is_callable in product(kinds, [False, True])])
    else:
        max_counts = (len(names) - 2) // (2 if PRE_PYTHON_3_8 else 3)
        counts = strategies.integers(0, max_counts)
        variants = OrderedDict()
        if not PRE_PYTHON_3_8:
            variants[inspect._POSITIONAL_ONLY] = counts.flatmap(
                    to_count_with_flags)
        variants[inspect._POSITIONAL_OR_KEYWORD] = counts.flatmap(
                to_count_with_flags)
        variants[inspect._VAR_POSITIONAL] = booleans.flatmap(
                to_count_with_flags)
        variants[inspect._KEYWORD_ONLY] = counts.flatmap(to_count_with_flags)
        variants[inspect._VAR_KEYWORD] = booleans.flatmap(to_count_with_flags)
        parameters_counters = strategies.fixed_dictionaries(variants)

    def select(counter: Dict[inspect._ParameterKind, Tuple[int, List[bool]]]
               ) -> SignatureData:
        names_iterator = iter(names)
        return OrderedDict((kind, list(zip(islice(names_iterator, count),
                                           flags)))
                           for kind, (count, flags) in counter.items()
                           if count)

    return parameters_counters.map(select)


def _to_constructor_with_initializer(signature_data: SignatureData,
                                     field_name_factory: Operator[str]
                                     ) -> Tuple[Constructor, Initializer]:
    return (_to_constructor(signature_data),
            _to_initializer(signature_data, field_name_factory))


def _to_custom_constructor_with_initializer(
        name_with_signature_data: Tuple[str, SignatureData],
        field_name_factory: Operator[str]) -> Tuple[Constructor, Initializer]:
    name, signature_data = name_with_signature_data
    return (_to_custom_constructor(name, signature_data),
            _to_initializer(signature_data, field_name_factory))


def _to_constructor(signature_data: SignatureData) -> Constructor:
    signature = _to_signature(CLASS_PARAMETER_NAME, signature_data)
    body = _to_constructor_body()
    return _compile_function(DEFAULT_CONSTRUCTOR_NAME, signature, body, [])


def _to_custom_constructor(name: str,
                           signature_data: SignatureData) -> Constructor:
    signature = _to_signature(CLASS_PARAMETER_NAME, signature_data)
    body = _to_custom_constructor_body(signature_data)
    decorators = [ast.Name(classmethod.__name__, ast.Load())]
    return _compile_function(name, signature, body, decorators)


def _to_initializer(signature_data: SignatureData,
                    field_name_factory: Operator[str]) -> Initializer:
    signature = _to_signature(SELF_PARAMETER_NAME, signature_data)
    body = _to_initializer_body(signature_data, field_name_factory)
    return _compile_function(INITIALIZER_NAME, signature, body, [])


def _to_constructor_body(class_parameter_name: str = CLASS_PARAMETER_NAME,
                         instance_object_name: str = SELF_PARAMETER_NAME
                         ) -> List[ast.stmt]:
    super_call = ast.Call(ast.Name(super.__qualname__, ast.Load()),
                          [ast.Name(type.__qualname__, ast.Load()),
                           ast.Name(class_parameter_name, ast.Load())],
                          [])
    instance_creation = ast.Call(ast.Attribute(super_call,
                                               DEFAULT_CONSTRUCTOR_NAME,
                                               ast.Load()),
                                 [ast.Name(class_parameter_name, ast.Load())],
                                 [])
    return [ast.Assign([ast.Name(instance_object_name, ast.Store())],
                       instance_creation),
            ast.Return(ast.Name(instance_object_name, ast.Load()))]


def _to_custom_constructor_body(
        signature_data: SignatureData,
        class_parameter_name: str = CLASS_PARAMETER_NAME,
        positional_kinds: Sequence[inspect._ParameterKind]
        = (inspect._POSITIONAL_ONLY,
           inspect._POSITIONAL_OR_KEYWORD)) -> List[ast.stmt]:
    positionals = flatten(signature_data.get(kind, [])
                          for kind in positional_kinds)
    keywords = signature_data.get(inspect._KEYWORD_ONLY, [])
    positional_arguments = [_to_loaded_name(parameter_name)
                            for parameter_name, _ in positionals]
    if inspect._VAR_POSITIONAL in signature_data:
        (variadic_positional_name, _), = (
            signature_data[inspect._VAR_POSITIONAL])
        variadic_positional_node = ast.Starred(
                _to_loaded_name(variadic_positional_name), ast.Load())
        positional_arguments.append(variadic_positional_node)
    keyword_arguments = [ast.keyword(parameter_name,
                                     _to_loaded_name(parameter_name))
                         for parameter_name, is_callable in keywords]
    if inspect._VAR_KEYWORD in signature_data:
        (variadic_keyword_name, _), = signature_data[inspect._VAR_KEYWORD]
        variadic_keyword_node = ast.keyword(
                None, _to_loaded_name(variadic_keyword_name))
        keyword_arguments.append(variadic_keyword_node)
    return [ast.Return(ast.Call(_to_loaded_name(class_parameter_name),
                                positional_arguments, keyword_arguments))]


def _to_initializer_body(signature_data: SignatureData,
                         field_name_factory: Operator[str],
                         instance_object_name: str = SELF_PARAMETER_NAME
                         ) -> List[ast.stmt]:
    if signature_data:
        def to_right_hand_value(parameter_name: str,
                                is_callable: bool) -> ast.expr:
            return (ast.Call(
                    ast.Attribute(_to_loaded_name(TYPES_MODULE_ALIAS),
                                  'MethodType', ast.Load()),
                    [ast.Lambda(_to_unit_signature(instance_object_name),
                                _to_loaded_name(parameter_name)),
                     _to_loaded_name(instance_object_name)], [])
                    if is_callable
                    else _to_loaded_name(parameter_name))

        return ([ast.Import([ast.alias(TYPES_MODULE_NAME,
                                       TYPES_MODULE_ALIAS)])]
                + [ast.Assign([ast.Attribute(ast.Name(instance_object_name,
                                                      ast.Load()),
                                             field_name_factory
                                             (parameter_name),
                                             ast.Store())],
                              to_right_hand_value(parameter_name, is_callable))
                   for parameter_name, is_callable in flatten(signature_data
                                                              .values())])
    else:
        return [ast.Pass()]


def _compile_function(name: str,
                      signature: ast.arguments,
                      body: List[ast.stmt],
                      decorators: List[ast.Name],
                      module_factory: Callable[..., ast.Module] =
                      ast.Module if PRE_PYTHON_3_8
                      # Python3.8 adds `type_ignores` parameter
                      else partial(ast.Module, type_ignores=[])
                      ) -> FunctionType:
    function_node = ast.FunctionDef(name, signature, body, decorators, None)
    tree = ast.fix_missing_locations(module_factory([function_node]))
    code = compile(tree, '<ast>', 'exec')
    namespace = {}
    exec(code, namespace)
    return namespace[name]


def _to_loaded_name(name: str) -> ast.Name:
    return ast.Name(name, ast.Load())


def _to_signature(first_parameter_name: str,
                  signature_data: SignatureData) -> ast.arguments:
    def to_parameters(raw_parameters: List[Tuple[str, bool]]) -> List[ast.arg]:
        return [to_parameter(name) for name, _ in raw_parameters]

    def to_parameter(name: str) -> ast.arg:
        return ast.arg(name, None)

    positionals_or_keywords_nodes = to_parameters(
            signature_data.get(inspect._POSITIONAL_OR_KEYWORD, []))
    if inspect._VAR_POSITIONAL in signature_data:
        (variadic_positional_name, _), = (
            signature_data[inspect._VAR_POSITIONAL])
        variadic_positional_node = to_parameter(variadic_positional_name)
    else:
        variadic_positional_node = None
    keyword_only_parameters = signature_data.get(inspect._KEYWORD_ONLY, [])
    keywords_only_nodes = to_parameters(keyword_only_parameters)
    if inspect._VAR_KEYWORD in signature_data:
        (variadic_keyword_name, _), = signature_data[inspect._VAR_KEYWORD]
        variadic_keyword_node = to_parameter(variadic_keyword_name)
    else:
        variadic_keyword_node = None
    positionals_or_keywords_defaults = []
    keywords_only_defaults = list(repeat(None,
                                         len(keyword_only_parameters)))
    if PRE_PYTHON_3_8:
        return ast.arguments([ast.arg(first_parameter_name, None)]
                             + positionals_or_keywords_nodes,
                             variadic_positional_node,
                             keywords_only_nodes,
                             keywords_only_defaults,
                             variadic_keyword_node,
                             positionals_or_keywords_defaults)
    else:
        if inspect._POSITIONAL_ONLY in signature_data:
            positionals_only_nodes = (
                    [ast.arg(first_parameter_name, None)]
                    + to_parameters(signature_data[inspect._POSITIONAL_ONLY]))
        else:
            positionals_only_nodes, positionals_or_keywords_nodes = (
                [],
                [ast.arg(first_parameter_name, None)]
                + positionals_or_keywords_nodes)
        return ast.arguments(positionals_only_nodes,
                             positionals_or_keywords_nodes,
                             variadic_positional_node,
                             keywords_only_nodes,
                             keywords_only_defaults,
                             variadic_keyword_node,
                             positionals_or_keywords_defaults)


def _to_unit_signature(name: str) -> ast.arguments:
    return (ast.arguments([ast.arg(name, None)], None, [], [], None, [])
            if PRE_PYTHON_3_8
            else ast.arguments([ast.arg(name, None)], [], None, [], [], None,
                               []))


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
    parameters = OrderedDict(inspect.signature(method).parameters)
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

import re
from functools import partial
from typing import (Any,
                    Iterable,
                    Type)

from hypothesis import strategies

from reprit.core.hints import Domain
from tests.utils import (ClassMethodInstance,
                         Method,
                         Namespace,
                         Strategy,
                         is_not_dunder)
from .factories import (INITIALIZER_NAME,
                        to_classes,
                        to_constructors_with_initializers,
                        to_custom_constructors_with_initializers,
                        to_initializers,
                        to_instances)
from .literals import identifiers
from .literals.base import (alike_parameters_counts,
                            complex_class_field_name_factories,
                            objects,
                            simple_class_field_name_factories)


def methods_to_namespace(methods: Iterable[Method]) -> Namespace:
    return {(method.__func__
             if isinstance(method, (classmethod, staticmethod))
             else method).__name__: method for method in methods}


simple_classes_namespaces = (
        strategies.fixed_dictionaries({
            INITIALIZER_NAME: to_initializers(
                    field_name_factories=simple_class_field_name_factories)})
        | (((to_constructors_with_initializers
             (field_name_factories=simple_class_field_name_factories))
            | (to_custom_constructors_with_initializers
               (field_name_factories=simple_class_field_name_factories)))
           .map(methods_to_namespace)))
simple_classes = to_classes(bases=strategies.tuples(),
                            namespaces=simple_classes_namespaces)
# prevents names clashes
# with underscored attributes
# like ``b``, ``_b``, ``b_`` and so on
to_alphanumeric_characters = partial(re.compile(r'[^a-zA-Z0-9]').sub, '')
complex_classes_namespaces = (
        strategies.fixed_dictionaries(
                {INITIALIZER_NAME: to_initializers(
                        parameters_names_unique_by
                        =to_alphanumeric_characters,
                        field_name_factories
                        =complex_class_field_name_factories)})
        | (((to_constructors_with_initializers
             (field_name_factories=complex_class_field_name_factories))
            | (to_custom_constructors_with_initializers
               (field_name_factories=complex_class_field_name_factories)))
           .map(methods_to_namespace)))
complex_classes = to_classes(bases=strategies.tuples(),
                             namespaces=complex_classes_namespaces)


class Unsupported:
    def __init__(self, a, a_):
        self._a = a
        self.a_ = a_


unsupported_complex_classes = strategies.just(Unsupported)


def to_class_methods(cls: Type[Domain]) -> Strategy[Method]:
    methods = [cls.__init__]
    if cls.__new__ is not object.__new__:
        methods += [cls.__new__]
    try:
        custom_constructor = next(content
                                  for name, content in vars(cls).items()
                                  if is_not_dunder(name)
                                  and (isinstance(content, (classmethod,
                                                            staticmethod))))
    except StopIteration:
        pass
    else:
        methods.append(custom_constructor)
    return strategies.sampled_from(methods)


simple_classes_methods = simple_classes.flatmap(to_class_methods)
complex_classes_methods = complex_classes.flatmap(to_class_methods)


def to_classes_with_methods_and_instances(cls: Type[Domain]
                                          ) -> Strategy[ClassMethodInstance]:
    instances = to_instances(
            cls=cls,
            values={Any: objects},
            variadic_positionals_counts=alike_parameters_counts,
            variadic_keywords_names=identifiers.snake_case,
            variadic_keywords_counts=alike_parameters_counts)
    methods = to_class_methods(cls)
    return strategies.tuples(strategies.just(cls), methods, instances)


simple_classes_with_methods_and_instances = (
    simple_classes.flatmap(to_classes_with_methods_and_instances))
complex_classes_with_methods_and_instances = (
    complex_classes.flatmap(to_classes_with_methods_and_instances))
unsupported_complex_classes_with_methods_and_instances = (
    unsupported_complex_classes.flatmap(to_classes_with_methods_and_instances))

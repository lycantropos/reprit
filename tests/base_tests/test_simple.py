import platform
import sys

import pytest
from hypothesis import given

from reprit.base import generate_repr
from tests import strategies
from tests.utils import (ClassMethodInstance,
                         Method,
                         to_namespace)


@given(strategies.simple_classes_methods,
       strategies.booleans, strategies.booleans)
def test_basic(method: Method,
               prefer_keyword: bool,
               with_module_name: bool) -> None:
    result = generate_repr(method,
                           prefer_keyword=prefer_keyword,
                           with_module_name=with_module_name)

    assert callable(result)


@given(strategies.simple_classes_with_methods_and_instances,
       strategies.booleans,
       strategies.booleans)
def test_call(class_with_method_and_instance: ClassMethodInstance,
              prefer_keyword: bool,
              with_module_name: bool) -> None:
    _, method, instance = class_with_method_and_instance

    repr_ = generate_repr(method,
                          prefer_keyword=prefer_keyword,
                          with_module_name=with_module_name)

    result = repr_(instance)

    assert isinstance(result, str)


@pytest.mark.skipif(platform.python_implementation() == 'PyPy'
                    and sys.version_info > (3, 5, 3),
                    reason='Unreproducible failures on PyPy3.5.3')
@given(strategies.simple_classes_with_methods_and_instances,
       strategies.booleans,
       strategies.booleans)
def test_evaluation(class_with_method_and_instance: ClassMethodInstance,
                    prefer_keyword: bool,
                    with_module_name: bool) -> None:
    cls, method, instance = class_with_method_and_instance

    repr_ = generate_repr(method,
                          prefer_keyword=prefer_keyword,
                          with_module_name=with_module_name)
    instance_repr = repr_(instance)

    result = eval(instance_repr,
                  to_namespace(cls.__module__ + '.' + cls.__qualname__
                               if with_module_name
                               else cls.__qualname__,
                               cls))

    assert vars(result) == vars(instance)


@given(strategies.simple_classes_with_methods_and_instances,
       strategies.booleans)
def test_with_module_name(class_with_method_and_instance: ClassMethodInstance,
                          prefer_keyword: bool) -> None:
    cls, method, instance = class_with_method_and_instance

    repr_ = generate_repr(method,
                          prefer_keyword=prefer_keyword,
                          with_module_name=True)

    result = repr_(instance)

    assert result.startswith(cls.__module__)

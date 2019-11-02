import platform
import sys
from typing import (Tuple,
                    Type)

import pytest
from hypothesis import given

from reprit.base import generate_repr
from tests import strategies
from tests.utils import Domain


@given(strategies.simple_classes, strategies.booleans, strategies.booleans)
def test_basic(cls: Type[Domain],
               prefer_keyword: bool,
               with_module_name: bool) -> None:
    result = generate_repr(cls.__init__,
                           prefer_keyword=prefer_keyword,
                           with_module_name=with_module_name)

    assert callable(result)


@given(strategies.simple_classes_with_instances, strategies.booleans,
       strategies.booleans)
def test_call(class_with_instance: Tuple[Type[Domain], Domain],
              prefer_keyword: bool,
              with_module_name: bool) -> None:
    cls, instance = class_with_instance

    repr_ = generate_repr(cls.__init__,
                          prefer_keyword=prefer_keyword,
                          with_module_name=with_module_name)

    result = repr_(instance)

    assert isinstance(result, str)


@pytest.mark.skipif(platform.python_implementation() == 'PyPy'
                    and sys.version_info > (3, 5, 3),
                    reason='Unreproducible failures on PyPy3.5.3')
@given(strategies.simple_classes_with_instances, strategies.booleans)
def test_evaluation(class_with_instance: Tuple[Type[Domain], Domain],
                    prefer_keyword: bool) -> None:
    cls, instance = class_with_instance

    repr_ = generate_repr(cls.__init__,
                          prefer_keyword=prefer_keyword)
    instance_repr = repr_(instance)

    result = eval(instance_repr, {cls.__name__: cls})

    assert vars(result) == vars(instance)


@given(strategies.simple_classes_with_instances, strategies.booleans)
def test_with_module_name(class_with_instance: Tuple[Type[Domain], Domain],
                          prefer_keyword: bool) -> None:
    cls, instance = class_with_instance

    repr_ = generate_repr(cls.__init__,
                          prefer_keyword=prefer_keyword,
                          with_module_name=True)

    result = repr_(instance)

    assert result.startswith(cls.__module__)

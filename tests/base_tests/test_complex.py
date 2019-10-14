import platform
import sys
from typing import (Tuple,
                    Type)

import pytest
from hypothesis import given

from reprit import seekers
from reprit.base import generate_repr
from tests import strategies
from tests.utils import Domain


@given(strategies.complex_classes, strategies.booleans)
def test_basic(class_: Type[Domain],
               prefer_keyword: bool) -> None:
    result = generate_repr(class_.__init__,
                           field_seeker=seekers.complex_,
                           prefer_keyword=prefer_keyword)

    assert callable(result)


@given(strategies.complex_classes_with_instances, strategies.booleans)
def test_call(class_with_instance: Tuple[Type[Domain], Domain],
              prefer_keyword: bool) -> None:
    cls, instance = class_with_instance

    repr_ = generate_repr(cls.__init__,
                          field_seeker=seekers.complex_,
                          prefer_keyword=prefer_keyword)

    result = repr_(instance)

    assert isinstance(result, str)


@pytest.mark.skipif(platform.python_implementation() == 'PyPy'
                    and sys.version_info > (3, 5, 3),
                    reason='Unreproducible failures on PyPy3.5.3')
@given(strategies.complex_classes_with_instances, strategies.booleans)
def test_evaluation(class_with_instance: Tuple[Type[Domain], Domain],
                    prefer_keyword: bool) -> None:
    cls, instance = class_with_instance

    repr_ = generate_repr(cls.__init__,
                          field_seeker=seekers.complex_,
                          prefer_keyword=prefer_keyword)
    instance_repr = repr_(instance)

    result = eval(instance_repr, {cls.__name__: cls})

    assert vars(instance) == vars(result)


@given(strategies.unsupported_complex_classes_with_instances,
       strategies.booleans)
def test_unsupported(class_with_instance: Tuple[Type[Domain], Domain],
                     prefer_keyword: bool) -> None:
    cls, instance = class_with_instance

    repr_ = generate_repr(cls.__init__,
                          field_seeker=seekers.complex_,
                          prefer_keyword=prefer_keyword)

    with pytest.raises(AttributeError):
        repr_(instance)

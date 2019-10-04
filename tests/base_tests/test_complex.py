from typing import (Tuple,
                    Type)

import pytest
from hypothesis import given

from reprit import seekers
from reprit.base import generate_repr
from tests import strategies
from tests.utils import Domain


@given(strategies.complex_classes)
def test_basic(class_: Type[Domain]) -> None:
    result = generate_repr(class_.__init__,
                           field_seeker=seekers.complex_)

    assert callable(result)


@given(strategies.complex_classes_with_instances)
def test_call(class_with_instance: Tuple[Type[Domain], Domain]) -> None:
    cls, instance = class_with_instance

    repr_ = generate_repr(cls.__init__,
                          field_seeker=seekers.complex_)

    result = repr_(instance)

    assert isinstance(result, str)


@given(strategies.complex_classes_with_instances)
def test_evaluation(class_with_instance: Tuple[Type[Domain], Domain]) -> None:
    cls, instance = class_with_instance

    repr_ = generate_repr(cls.__init__,
                          field_seeker=seekers.complex_)
    instance_repr = repr_(instance)

    result = eval(instance_repr, {cls.__name__: cls})

    assert vars(instance) == vars(result)


@given(strategies.unsupported_complex_classes_with_instances)
def test_unsupported(class_with_instance: Tuple[Type[Domain], Domain]) -> None:
    cls, instance = class_with_instance

    repr_ = generate_repr(cls.__init__,
                          field_seeker=seekers.complex_)

    with pytest.raises(AttributeError):
        repr_(instance)

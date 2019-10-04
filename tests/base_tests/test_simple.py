from typing import (Tuple,
                    Type)

from hypothesis import given

from reprit.base import generate_repr
from tests import strategies
from tests.utils import Domain


@given(strategies.simple_classes)
def test_basic(cls: Type[Domain]) -> None:
    result = generate_repr(cls.__init__)

    assert callable(result)


@given(strategies.simple_classes_with_instances)
def test_call(class_with_instance: Tuple[Type[Domain], Domain]) -> None:
    cls, instance = class_with_instance

    repr_ = generate_repr(cls.__init__)

    result = repr_(instance)

    assert isinstance(result, str)


@given(strategies.simple_classes_with_instances)
def test_evaluation(class_with_instance: Tuple[Type[Domain], Domain]) -> None:
    cls, instance = class_with_instance

    repr_ = generate_repr(cls.__init__)
    instance_repr = repr_(instance)

    result = eval(instance_repr, {cls.__name__: cls})

    assert vars(result) == vars(instance)

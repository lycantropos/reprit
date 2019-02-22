from typing import Type

from reprit.base import generate_repr
from tests.utils import Domain


def test_basic(cls: Type[Domain]) -> None:
    result = generate_repr(cls.__init__)

    assert callable(result)


def test_call(cls: Type[Domain],
              instance: Domain) -> None:
    repr_ = generate_repr(cls.__init__)

    result = repr_(instance)

    assert isinstance(result, str)


def test_evaluation(cls: Type[Domain],
                    instance: Domain):
    repr_ = generate_repr(cls.__init__)
    instance_repr = repr_(instance)

    result = eval(instance_repr, {cls.__name__: cls})

    assert vars(result) == vars(instance)

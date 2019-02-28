from typing import Type

from reprit.base import generate_repr
from tests.utils import Domain


def test_basic(simple_class: Type[Domain]) -> None:
    result = generate_repr(simple_class.__init__)

    assert callable(result)


def test_call(simple_class: Type[Domain],
              simple_instance: Domain) -> None:
    repr_ = generate_repr(simple_class.__init__)

    result = repr_(simple_instance)

    assert isinstance(result, str)


def test_evaluation(simple_class: Type[Domain],
                    simple_instance: Domain) -> None:
    repr_ = generate_repr(simple_class.__init__)
    instance_repr = repr_(simple_instance)

    result = eval(instance_repr, {simple_class.__name__: simple_class})

    assert vars(result) == vars(simple_instance)

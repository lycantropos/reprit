from typing import Type

import pytest

from reprit import seekers
from reprit.base import generate_repr
from tests.utils import Domain


def test_basic(complex_class: Type[Domain]) -> None:
    result = generate_repr(complex_class.__init__,
                           field_seeker=seekers.complex_)

    assert callable(result)


def test_call(complex_class: Type[Domain],
              complex_instance: Domain) -> None:
    repr_ = generate_repr(complex_class.__init__,
                          field_seeker=seekers.complex_)

    result = repr_(complex_instance)

    assert isinstance(result, str)


def test_evaluation(complex_class: Type[Domain],
                    complex_instance: Domain) -> None:
    repr_ = generate_repr(complex_class.__init__,
                          field_seeker=seekers.complex_)
    instance_repr = repr_(complex_instance)

    result = eval(instance_repr, {complex_class.__name__: complex_class})

    assert vars(complex_instance) == vars(result)


def test_unsupported(unsupported_complex_class: Type[Domain],
                     unsupported_complex_instance: Domain) -> None:
    repr_ = generate_repr(unsupported_complex_class.__init__,
                          field_seeker=seekers.complex_)

    with pytest.raises(AttributeError):
        repr_(unsupported_complex_instance)

import inspect
from collections import (OrderedDict,
                         abc)
from typing import (Iterable,
                    Union)

from . import seekers
from .hints import (Constructor,
                    Domain,
                    FieldSeeker,
                    Initializer,
                    Map)


def generate_repr(constructor_or_initializer: Union[Constructor, Initializer],
                  *,
                  field_seeker: FieldSeeker = seekers.simple,
                  prefer_keyword: bool = False) -> Map[Domain, str]:
    """
    Generates `__repr__` method based on constructor/initializer parameters.

    We are assuming that no parameters data
    get thrown away during instance creation,
    so we can re-create it after.

    :param constructor_or_initializer: constructor/initializer method
    which parameters will be used in resulting representation.
    :param field_seeker: function that re-creates parameter value
    based on class instance and name.
    :param prefer_keyword: flag that tells if positional-or-keyword parameters
    should be outputted as keyword ones when possible.

    >>> from reprit.base import generate_repr
    >>> class Person:
    ...     def __init__(self, name, *, address=None):
    ...         self.name = name
    ...         self.address = address
    ...     __repr__ = generate_repr(__init__)
    >>> Person('Adrian')
    Person('Adrian', address=None)
    >>> Person('Mary', address='Somewhere on Earth')
    Person('Mary', address='Somewhere on Earth')
    >>> class ScoreBoard:
    ...     def __init__(self, first, *rest):
    ...         self.first = first
    ...         self.rest = rest
    ...     __repr__ = generate_repr(__init__,
    ...                              prefer_keyword=True)
    >>> ScoreBoard(1)
    ScoreBoard(first=1)
    >>> ScoreBoard(1, 40)
    ScoreBoard(1, 40)
    >>> from reprit import seekers
    >>> class Account:
    ...     def __init__(self, id_, *, balance=0):
    ...         self.id = id_
    ...         self.balance = balance
    ...     __repr__ = generate_repr(__init__,
    ...                              field_seeker=seekers.complex_)
    >>> Account(1)
    Account(1, balance=0)
    >>> Account(100, balance=-10)
    Account(100, balance=-10)
    """
    signature = inspect.signature(constructor_or_initializer)
    parameters = OrderedDict(signature.parameters)
    # remove `cls`/`self`
    parameters.popitem(0)
    variadic_positional = next((parameter
                                for parameter in parameters.values()
                                if parameter.kind is inspect._VAR_POSITIONAL),
                               None)
    to_positional_argument_string = repr
    to_keyword_argument_string = '{}={!r}'.format

    def __repr__(self: Domain) -> str:
        return (type(self).__qualname__
                + '(' + ', '.join(to_arguments_strings(self)) + ')')

    def to_arguments_strings(object_: Domain) -> Iterable[str]:
        variadic_positional_unset = (
                variadic_positional is None
                or not field_seeker(object_, variadic_positional.name))
        for parameter_name, parameter in parameters.items():
            field = field_seeker(object_, parameter_name)
            if parameter.kind is inspect._POSITIONAL_ONLY:
                yield to_positional_argument_string(field)
            elif parameter.kind is inspect._POSITIONAL_OR_KEYWORD:
                if prefer_keyword and variadic_positional_unset:
                    yield to_keyword_argument_string(parameter_name, field)
                else:
                    yield to_positional_argument_string(field)
            elif parameter.kind is inspect._VAR_POSITIONAL:
                if isinstance(field, abc.Iterator):
                    # we don't want to exhaust iterator
                    yield '...'
                else:
                    yield from map(to_positional_argument_string, field)
            elif parameter.kind is inspect._KEYWORD_ONLY:
                yield to_keyword_argument_string(parameter_name, field)
            else:
                yield from map(to_keyword_argument_string,
                               field.keys(), field.values())

    return __repr__

import inspect
from collections import (OrderedDict,
                         abc)
from typing import (Any,
                    Callable,
                    Iterable,
                    Union)

from .hints import (Constructor,
                    Domain,
                    Initializer,
                    Map)


def generate_repr(constructor_or_initializer: Union[Constructor, Initializer],
                  *,
                  field_seeker: Callable[[Domain, str], Any] = getattr
                  ) -> Map[Domain, str]:
    """
    Generates ``__repr__`` method based on constructor/initializer parameters.

    We are assuming that no parameters data
    get thrown away during instance creation,
    so we can re-create it after.

    :param constructor_or_initializer: constructor/initializer method
    which parameters will be used in resulting representation.
    :param field_seeker: function that re-creates parameter value
    based on class instance and name.
    """
    signature = inspect.signature(constructor_or_initializer)
    parameters = OrderedDict(signature.parameters)
    # remove `self`
    parameters.popitem(0)
    to_positional_argument_string = repr
    to_keyword_argument_string = '{}={!r}'.format

    def __repr__(self: Domain) -> str:
        return (type(self).__qualname__
                + '(' + ', '.join(to_arguments_strings(self)) + ')')

    def to_arguments_strings(object_: Domain) -> Iterable[str]:
        for parameter_name, parameter in parameters.items():
            field = field_seeker(object_, parameter_name)
            if parameter.kind == inspect._VAR_POSITIONAL:
                if isinstance(field, abc.Iterator):
                    # we don't want to exhaust iterator
                    yield '...'
                else:
                    yield from map(to_positional_argument_string, field)
            elif parameter.kind == inspect._VAR_KEYWORD:
                yield from map(to_keyword_argument_string,
                               field.keys(), field.values())
            elif parameter.kind in {inspect._POSITIONAL_ONLY,
                                    inspect._POSITIONAL_OR_KEYWORD}:
                yield to_positional_argument_string(field)
            else:
                yield to_keyword_argument_string(parameter_name, field)

    return __repr__

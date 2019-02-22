import keyword
from string import (ascii_letters,
                    ascii_lowercase,
                    digits)

from hypothesis import strategies


def is_not_keyword(string: str) -> bool:
    return not keyword.iskeyword(string)


snake_case_alphabet = strategies.sampled_from(ascii_lowercase + '_' + digits)
snake_case_identifiers = (strategies.text(alphabet=snake_case_alphabet,
                                          min_size=1)
                          .filter(str.isidentifier)
                          .filter(is_not_keyword))
camel_case_alphabet = strategies.sampled_from(ascii_letters + digits)


def camel_case_to_pascal_case(string: str) -> str:
    return string[:1].capitalize() + string[1:]


pascal_case_identifiers = (strategies.text(alphabet=camel_case_alphabet,
                                           min_size=1)
                           .filter(str.isidentifier)
                           .filter(is_not_keyword)
                           .map(camel_case_to_pascal_case))

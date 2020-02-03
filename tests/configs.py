import inspect
import sys

MAX_ITERABLES_SIZE = min(10 ** 3, sys.maxsize)
MAX_PARAMETERS_COUNT = 255 if sys.version_info < (3, 7) else None
MAX_ALIKE_PARAMETERS_COUNT = (min(MAX_ITERABLES_SIZE, MAX_PARAMETERS_COUNT)
                              // len(inspect._ParameterKind)
                              if MAX_PARAMETERS_COUNT is not None
                              else MAX_ITERABLES_SIZE)

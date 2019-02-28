import sys

MAX_ITERABLES_SIZE = min(10 ** 3, sys.maxsize)
MAX_PARAMETERS_COUNT = 255 if sys.version_info < (3, 7) else float('inf')

from types import (BuiltinFunctionType as _BuiltinFunctionType,
                   BuiltinMethodType as _BuiltinMethodType,
                   FunctionType as _FunctionType,
                   GetSetDescriptorType as _GetSetDescriptorType,
                   MemberDescriptorType as _MemberDescriptorType,
                   MethodType as _MethodType,
                   ModuleType as _ModuleType)
from typing import Any as _Any

try:
    from types import MethodDescriptorType as _MethodDescriptorType
except ImportError:
    _MethodDescriptorType = type(str.join)
try:
    from types import MethodWrapperType as _MethodWrapperType
except ImportError:
    _MethodWrapperType = type(object().__str__)

simple = repr


def complex_(object_: _Any) -> str:
    if isinstance(object_, _ModuleType):
        return object_.__name__
    elif isinstance(object_, (_BuiltinFunctionType, _FunctionType, type)):
        return '{}.{}'.format(object_.__module__, object_.__qualname__)
    elif isinstance(object_, (_BuiltinMethodType, _MethodType)):
        return '{}.{}'.format(complex_(object_.__self__), object_.__name__)
    elif isinstance(object_, (_GetSetDescriptorType, _MemberDescriptorType,
                              _MethodDescriptorType, _MethodWrapperType)):
        return '{}.{}'.format(complex_(object_.__objclass__), object_.__name__)
    else:
        return repr(object_)

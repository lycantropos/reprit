from functools import singledispatch as _singledispatch
from types import (BuiltinFunctionType as _BuiltinFunctionType,
                   BuiltinMethodType as _BuiltinMethodType,
                   FunctionType as _FunctionType,
                   GetSetDescriptorType as _GetSetDescriptorType,
                   MemberDescriptorType as _MemberDescriptorType,
                   MethodType as _MethodType,
                   ModuleType as _ModuleType)
from typing import (Any as _Any,
                    Union as _Union)
from enum import Enum as _Enum

try:
    from types import ClassMethodDescriptorType as _ClassMethodDescriptorType
except ImportError:
    _ClassMethodDescriptorType = type(dict.__dict__['fromkeys'])
try:
    from types import MethodDescriptorType as _MethodDescriptorType
except ImportError:
    _MethodDescriptorType = type(str.join)
try:
    from types import MethodWrapperType as _MethodWrapperType
except ImportError:
    _MethodWrapperType = type(object().__str__)
try:
    from types import WrapperDescriptorType as _WrapperDescriptorType
except ImportError:
    _WrapperDescriptorType = type(object.__init__)

simple = repr


@_singledispatch
def complex_(object_: _Any) -> str:
    return repr(object_)


@complex_.register(_BuiltinFunctionType)
@complex_.register(_FunctionType)
@complex_.register(type)
def _(object_: _Union[_BuiltinFunctionType, _FunctionType, type]) -> str:
    return object_.__module__ + '.' + object_.__qualname__


@complex_.register(_BuiltinMethodType)
@complex_.register(_MethodType)
def _(object_: _Union[_BuiltinMethodType, _MethodType]) -> str:
    return complex_(object_.__self__) + '.' + object_.__name__


@complex_.register(_ClassMethodDescriptorType)
@complex_.register(_GetSetDescriptorType)
@complex_.register(_MemberDescriptorType)
@complex_.register(_MethodDescriptorType)
@complex_.register(_MethodWrapperType)
@complex_.register(_WrapperDescriptorType)
def _(object_: _Union[_ClassMethodDescriptorType, _GetSetDescriptorType,
                      _MemberDescriptorType, _MethodDescriptorType,
                      _MethodWrapperType, _WrapperDescriptorType]) -> str:
    return complex_(object_.__objclass__) + '.' + object_.__name__


@complex_.register(_Enum)
def _(object_: _Enum) -> str:
    return complex_(type(object_)) + '.' + object_.name


@complex_.register(_ModuleType)
def _(object_: _ModuleType) -> str:
    return object_.__name__


@complex_.register(classmethod)
@complex_.register(staticmethod)
def _(object_: _Union[classmethod, staticmethod]) -> str:
    return '{}({})'.format(complex_(type(object_)), complex_(object_.__func__))


@complex_.register(dict)
def _(object_: dict) -> str:
    return '{' + ', '.join(map('{}: {}'.format,
                               map(complex_, object_.keys()),
                               map(complex_, object_.values()))) + '}'


@complex_.register(frozenset)
def _(object_: frozenset) -> str:
    return (complex_(type(object_)) + '('
            + ('{' + ', '.join(map(complex_, object_)) + '}'
               if object_
               else '')
            + ')')


@complex_.register(list)
def _(object_: list) -> str:
    return '[' + ', '.join(map(complex_, object_)) + ']'


@complex_.register(memoryview)
def _(object_: memoryview) -> str:
    return complex_(type(object_)) + '(' + complex_(object_.obj) + ')'


@complex_.register(set)
def _(object_: set) -> str:
    return ('{' + ', '.join(map(complex_, object_)) + '}'
            if object_
            else complex_(type(object_)) + '()')


@complex_.register(tuple)
def _(object_: tuple) -> str:
    return ('(' + ', '.join(map(complex_, object_))
            + (',' if len(object_) == 1 else '') + ')')

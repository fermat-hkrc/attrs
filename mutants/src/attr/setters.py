# SPDX-License-Identifier: MIT

"""
Commonly used hooks for on_setattr.
"""

from . import _config
from .exceptions import FrozenAttributeError
from typing import Annotated
from typing import Callable
from typing import ClassVar

MutantDict = Annotated[dict[str, Callable], "Mutant"] # type: ignore


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None): # type: ignore
    """Forward call to original or mutated function, depending on the environment"""
    import os # type: ignore
    mutant_under_test = os.environ['MUTANT_UNDER_TEST'] # type: ignore
    if mutant_under_test == 'fail': # type: ignore
        from mutmut.__main__ import MutmutProgrammaticFailException # type: ignore
        raise MutmutProgrammaticFailException('Failed programmatically')       # type: ignore
    elif mutant_under_test == 'stats': # type: ignore
        from mutmut.__main__ import record_trampoline_hit # type: ignore
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__) # type: ignore
        # (for class methods, orig is bound and thus does not need the explicit self argument)
        result = orig(*call_args, **call_kwargs) # type: ignore
        return result # type: ignore
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_' # type: ignore
    if not mutant_under_test.startswith(prefix): # type: ignore
        result = orig(*call_args, **call_kwargs) # type: ignore
        return result # type: ignore
    mutant_name = mutant_under_test.rpartition('.')[-1] # type: ignore
    if self_arg is not None: # type: ignore
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs) # type: ignore
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs) # type: ignore
    return result # type: ignore


def pipe(*setters):
    args = [*setters]# type: ignore
    kwargs = {}# type: ignore
    return _mutmut_trampoline(x_pipe__mutmut_orig, x_pipe__mutmut_mutants, args, kwargs, None)


def x_pipe__mutmut_orig(*setters):
    """
    Run all *setters* and return the return value of the last one.

    .. versionadded:: 20.1.0
    """

    def wrapped_pipe(instance, attrib, new_value):
        rv = new_value

        for setter in setters:
            rv = setter(instance, attrib, rv)

        return rv

    return wrapped_pipe


def x_pipe__mutmut_1(*setters):
    """
    Run all *setters* and return the return value of the last one.

    .. versionadded:: 20.1.0
    """

    def wrapped_pipe(instance, attrib, new_value):
        rv = None

        for setter in setters:
            rv = setter(instance, attrib, rv)

        return rv

    return wrapped_pipe


def x_pipe__mutmut_2(*setters):
    """
    Run all *setters* and return the return value of the last one.

    .. versionadded:: 20.1.0
    """

    def wrapped_pipe(instance, attrib, new_value):
        rv = new_value

        for setter in setters:
            rv = None

        return rv

    return wrapped_pipe


def x_pipe__mutmut_3(*setters):
    """
    Run all *setters* and return the return value of the last one.

    .. versionadded:: 20.1.0
    """

    def wrapped_pipe(instance, attrib, new_value):
        rv = new_value

        for setter in setters:
            rv = setter(None, attrib, rv)

        return rv

    return wrapped_pipe


def x_pipe__mutmut_4(*setters):
    """
    Run all *setters* and return the return value of the last one.

    .. versionadded:: 20.1.0
    """

    def wrapped_pipe(instance, attrib, new_value):
        rv = new_value

        for setter in setters:
            rv = setter(instance, None, rv)

        return rv

    return wrapped_pipe


def x_pipe__mutmut_5(*setters):
    """
    Run all *setters* and return the return value of the last one.

    .. versionadded:: 20.1.0
    """

    def wrapped_pipe(instance, attrib, new_value):
        rv = new_value

        for setter in setters:
            rv = setter(instance, attrib, None)

        return rv

    return wrapped_pipe


def x_pipe__mutmut_6(*setters):
    """
    Run all *setters* and return the return value of the last one.

    .. versionadded:: 20.1.0
    """

    def wrapped_pipe(instance, attrib, new_value):
        rv = new_value

        for setter in setters:
            rv = setter(attrib, rv)

        return rv

    return wrapped_pipe


def x_pipe__mutmut_7(*setters):
    """
    Run all *setters* and return the return value of the last one.

    .. versionadded:: 20.1.0
    """

    def wrapped_pipe(instance, attrib, new_value):
        rv = new_value

        for setter in setters:
            rv = setter(instance, rv)

        return rv

    return wrapped_pipe


def x_pipe__mutmut_8(*setters):
    """
    Run all *setters* and return the return value of the last one.

    .. versionadded:: 20.1.0
    """

    def wrapped_pipe(instance, attrib, new_value):
        rv = new_value

        for setter in setters:
            rv = setter(instance, attrib, )

        return rv

    return wrapped_pipe

x_pipe__mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
'x_pipe__mutmut_1': x_pipe__mutmut_1, 
    'x_pipe__mutmut_2': x_pipe__mutmut_2, 
    'x_pipe__mutmut_3': x_pipe__mutmut_3, 
    'x_pipe__mutmut_4': x_pipe__mutmut_4, 
    'x_pipe__mutmut_5': x_pipe__mutmut_5, 
    'x_pipe__mutmut_6': x_pipe__mutmut_6, 
    'x_pipe__mutmut_7': x_pipe__mutmut_7, 
    'x_pipe__mutmut_8': x_pipe__mutmut_8
}
x_pipe__mutmut_orig.__name__ = 'x_pipe'


def frozen(_, __, ___):
    """
    Prevent an attribute to be modified.

    .. versionadded:: 20.1.0
    """
    raise FrozenAttributeError


def validate(instance, attrib, new_value):
    args = [instance, attrib, new_value]# type: ignore
    kwargs = {}# type: ignore
    return _mutmut_trampoline(x_validate__mutmut_orig, x_validate__mutmut_mutants, args, kwargs, None)


def x_validate__mutmut_orig(instance, attrib, new_value):
    """
    Run *attrib*'s validator on *new_value* if it has one.

    .. versionadded:: 20.1.0
    """
    if _config._run_validators is False:
        return new_value

    v = attrib.validator
    if not v:
        return new_value

    v(instance, attrib, new_value)

    return new_value


def x_validate__mutmut_1(instance, attrib, new_value):
    """
    Run *attrib*'s validator on *new_value* if it has one.

    .. versionadded:: 20.1.0
    """
    if _config._run_validators is not False:
        return new_value

    v = attrib.validator
    if not v:
        return new_value

    v(instance, attrib, new_value)

    return new_value


def x_validate__mutmut_2(instance, attrib, new_value):
    """
    Run *attrib*'s validator on *new_value* if it has one.

    .. versionadded:: 20.1.0
    """
    if _config._run_validators is True:
        return new_value

    v = attrib.validator
    if not v:
        return new_value

    v(instance, attrib, new_value)

    return new_value


def x_validate__mutmut_3(instance, attrib, new_value):
    """
    Run *attrib*'s validator on *new_value* if it has one.

    .. versionadded:: 20.1.0
    """
    if _config._run_validators is False:
        return new_value

    v = None
    if not v:
        return new_value

    v(instance, attrib, new_value)

    return new_value


def x_validate__mutmut_4(instance, attrib, new_value):
    """
    Run *attrib*'s validator on *new_value* if it has one.

    .. versionadded:: 20.1.0
    """
    if _config._run_validators is False:
        return new_value

    v = attrib.validator
    if v:
        return new_value

    v(instance, attrib, new_value)

    return new_value


def x_validate__mutmut_5(instance, attrib, new_value):
    """
    Run *attrib*'s validator on *new_value* if it has one.

    .. versionadded:: 20.1.0
    """
    if _config._run_validators is False:
        return new_value

    v = attrib.validator
    if not v:
        return new_value

    v(None, attrib, new_value)

    return new_value


def x_validate__mutmut_6(instance, attrib, new_value):
    """
    Run *attrib*'s validator on *new_value* if it has one.

    .. versionadded:: 20.1.0
    """
    if _config._run_validators is False:
        return new_value

    v = attrib.validator
    if not v:
        return new_value

    v(instance, None, new_value)

    return new_value


def x_validate__mutmut_7(instance, attrib, new_value):
    """
    Run *attrib*'s validator on *new_value* if it has one.

    .. versionadded:: 20.1.0
    """
    if _config._run_validators is False:
        return new_value

    v = attrib.validator
    if not v:
        return new_value

    v(instance, attrib, None)

    return new_value


def x_validate__mutmut_8(instance, attrib, new_value):
    """
    Run *attrib*'s validator on *new_value* if it has one.

    .. versionadded:: 20.1.0
    """
    if _config._run_validators is False:
        return new_value

    v = attrib.validator
    if not v:
        return new_value

    v(attrib, new_value)

    return new_value


def x_validate__mutmut_9(instance, attrib, new_value):
    """
    Run *attrib*'s validator on *new_value* if it has one.

    .. versionadded:: 20.1.0
    """
    if _config._run_validators is False:
        return new_value

    v = attrib.validator
    if not v:
        return new_value

    v(instance, new_value)

    return new_value


def x_validate__mutmut_10(instance, attrib, new_value):
    """
    Run *attrib*'s validator on *new_value* if it has one.

    .. versionadded:: 20.1.0
    """
    if _config._run_validators is False:
        return new_value

    v = attrib.validator
    if not v:
        return new_value

    v(instance, attrib, )

    return new_value

x_validate__mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
'x_validate__mutmut_1': x_validate__mutmut_1, 
    'x_validate__mutmut_2': x_validate__mutmut_2, 
    'x_validate__mutmut_3': x_validate__mutmut_3, 
    'x_validate__mutmut_4': x_validate__mutmut_4, 
    'x_validate__mutmut_5': x_validate__mutmut_5, 
    'x_validate__mutmut_6': x_validate__mutmut_6, 
    'x_validate__mutmut_7': x_validate__mutmut_7, 
    'x_validate__mutmut_8': x_validate__mutmut_8, 
    'x_validate__mutmut_9': x_validate__mutmut_9, 
    'x_validate__mutmut_10': x_validate__mutmut_10
}
x_validate__mutmut_orig.__name__ = 'x_validate'


def convert(instance, attrib, new_value):
    args = [instance, attrib, new_value]# type: ignore
    kwargs = {}# type: ignore
    return _mutmut_trampoline(x_convert__mutmut_orig, x_convert__mutmut_mutants, args, kwargs, None)


def x_convert__mutmut_orig(instance, attrib, new_value):
    """
    Run *attrib*'s converter -- if it has one -- on *new_value* and return the
    result.

    .. versionadded:: 20.1.0
    """
    c = attrib.converter
    if c:
        # This can be removed once we drop 3.8 and use attrs.Converter instead.
        from ._make import Converter

        if not isinstance(c, Converter):
            return c(new_value)

        return c(new_value, instance, attrib)

    return new_value


def x_convert__mutmut_1(instance, attrib, new_value):
    """
    Run *attrib*'s converter -- if it has one -- on *new_value* and return the
    result.

    .. versionadded:: 20.1.0
    """
    c = None
    if c:
        # This can be removed once we drop 3.8 and use attrs.Converter instead.
        from ._make import Converter

        if not isinstance(c, Converter):
            return c(new_value)

        return c(new_value, instance, attrib)

    return new_value


def x_convert__mutmut_2(instance, attrib, new_value):
    """
    Run *attrib*'s converter -- if it has one -- on *new_value* and return the
    result.

    .. versionadded:: 20.1.0
    """
    c = attrib.converter
    if c:
        # This can be removed once we drop 3.8 and use attrs.Converter instead.
        from ._make import Converter

        if isinstance(c, Converter):
            return c(new_value)

        return c(new_value, instance, attrib)

    return new_value


def x_convert__mutmut_3(instance, attrib, new_value):
    """
    Run *attrib*'s converter -- if it has one -- on *new_value* and return the
    result.

    .. versionadded:: 20.1.0
    """
    c = attrib.converter
    if c:
        # This can be removed once we drop 3.8 and use attrs.Converter instead.
        from ._make import Converter

        if not isinstance(c, Converter):
            return c(None)

        return c(new_value, instance, attrib)

    return new_value


def x_convert__mutmut_4(instance, attrib, new_value):
    """
    Run *attrib*'s converter -- if it has one -- on *new_value* and return the
    result.

    .. versionadded:: 20.1.0
    """
    c = attrib.converter
    if c:
        # This can be removed once we drop 3.8 and use attrs.Converter instead.
        from ._make import Converter

        if not isinstance(c, Converter):
            return c(new_value)

        return c(None, instance, attrib)

    return new_value


def x_convert__mutmut_5(instance, attrib, new_value):
    """
    Run *attrib*'s converter -- if it has one -- on *new_value* and return the
    result.

    .. versionadded:: 20.1.0
    """
    c = attrib.converter
    if c:
        # This can be removed once we drop 3.8 and use attrs.Converter instead.
        from ._make import Converter

        if not isinstance(c, Converter):
            return c(new_value)

        return c(new_value, None, attrib)

    return new_value


def x_convert__mutmut_6(instance, attrib, new_value):
    """
    Run *attrib*'s converter -- if it has one -- on *new_value* and return the
    result.

    .. versionadded:: 20.1.0
    """
    c = attrib.converter
    if c:
        # This can be removed once we drop 3.8 and use attrs.Converter instead.
        from ._make import Converter

        if not isinstance(c, Converter):
            return c(new_value)

        return c(new_value, instance, None)

    return new_value


def x_convert__mutmut_7(instance, attrib, new_value):
    """
    Run *attrib*'s converter -- if it has one -- on *new_value* and return the
    result.

    .. versionadded:: 20.1.0
    """
    c = attrib.converter
    if c:
        # This can be removed once we drop 3.8 and use attrs.Converter instead.
        from ._make import Converter

        if not isinstance(c, Converter):
            return c(new_value)

        return c(instance, attrib)

    return new_value


def x_convert__mutmut_8(instance, attrib, new_value):
    """
    Run *attrib*'s converter -- if it has one -- on *new_value* and return the
    result.

    .. versionadded:: 20.1.0
    """
    c = attrib.converter
    if c:
        # This can be removed once we drop 3.8 and use attrs.Converter instead.
        from ._make import Converter

        if not isinstance(c, Converter):
            return c(new_value)

        return c(new_value, attrib)

    return new_value


def x_convert__mutmut_9(instance, attrib, new_value):
    """
    Run *attrib*'s converter -- if it has one -- on *new_value* and return the
    result.

    .. versionadded:: 20.1.0
    """
    c = attrib.converter
    if c:
        # This can be removed once we drop 3.8 and use attrs.Converter instead.
        from ._make import Converter

        if not isinstance(c, Converter):
            return c(new_value)

        return c(new_value, instance, )

    return new_value

x_convert__mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
'x_convert__mutmut_1': x_convert__mutmut_1, 
    'x_convert__mutmut_2': x_convert__mutmut_2, 
    'x_convert__mutmut_3': x_convert__mutmut_3, 
    'x_convert__mutmut_4': x_convert__mutmut_4, 
    'x_convert__mutmut_5': x_convert__mutmut_5, 
    'x_convert__mutmut_6': x_convert__mutmut_6, 
    'x_convert__mutmut_7': x_convert__mutmut_7, 
    'x_convert__mutmut_8': x_convert__mutmut_8, 
    'x_convert__mutmut_9': x_convert__mutmut_9
}
x_convert__mutmut_orig.__name__ = 'x_convert'


# Sentinel for disabling class-wide *on_setattr* hooks for certain attributes.
# Sphinx's autodata stopped working, so the docstring is inlined in the API
# docs.
NO_OP = object()

# SPDX-License-Identifier: MIT

"""
Commonly useful filters for `attrs.asdict` and `attrs.astuple`.
"""

from ._make import Attribute
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


def _split_what(what):
    args = [what]# type: ignore
    kwargs = {}# type: ignore
    return _mutmut_trampoline(x__split_what__mutmut_orig, x__split_what__mutmut_mutants, args, kwargs, None)


def x__split_what__mutmut_orig(what):
    """
    Returns a tuple of `frozenset`s of classes and attributes.
    """
    return (
        frozenset(cls for cls in what if isinstance(cls, type)),
        frozenset(cls for cls in what if isinstance(cls, str)),
        frozenset(cls for cls in what if isinstance(cls, Attribute)),
    )


def x__split_what__mutmut_1(what):
    """
    Returns a tuple of `frozenset`s of classes and attributes.
    """
    return (
        frozenset(None),
        frozenset(cls for cls in what if isinstance(cls, str)),
        frozenset(cls for cls in what if isinstance(cls, Attribute)),
    )


def x__split_what__mutmut_2(what):
    """
    Returns a tuple of `frozenset`s of classes and attributes.
    """
    return (
        frozenset(cls for cls in what if isinstance(cls, type)),
        frozenset(None),
        frozenset(cls for cls in what if isinstance(cls, Attribute)),
    )


def x__split_what__mutmut_3(what):
    """
    Returns a tuple of `frozenset`s of classes and attributes.
    """
    return (
        frozenset(cls for cls in what if isinstance(cls, type)),
        frozenset(cls for cls in what if isinstance(cls, str)),
        frozenset(None),
    )

x__split_what__mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
'x__split_what__mutmut_1': x__split_what__mutmut_1, 
    'x__split_what__mutmut_2': x__split_what__mutmut_2, 
    'x__split_what__mutmut_3': x__split_what__mutmut_3
}
x__split_what__mutmut_orig.__name__ = 'x__split_what'


def include(*what):
    args = [*what]# type: ignore
    kwargs = {}# type: ignore
    return _mutmut_trampoline(x_include__mutmut_orig, x_include__mutmut_mutants, args, kwargs, None)


def x_include__mutmut_orig(*what):
    """
    Create a filter that only allows *what*.

    Args:
        what (list[type, str, attrs.Attribute]):
            What to include. Can be a type, a name, or an attribute.

    Returns:
        Callable:
            A callable that can be passed to `attrs.asdict`'s and
            `attrs.astuple`'s *filter* argument.

    .. versionchanged:: 23.1.0 Accept strings with field names.
    """
    cls, names, attrs = _split_what(what)

    def include_(attribute, value):
        return (
            value.__class__ in cls
            or attribute.name in names
            or attribute in attrs
        )

    return include_


def x_include__mutmut_1(*what):
    """
    Create a filter that only allows *what*.

    Args:
        what (list[type, str, attrs.Attribute]):
            What to include. Can be a type, a name, or an attribute.

    Returns:
        Callable:
            A callable that can be passed to `attrs.asdict`'s and
            `attrs.astuple`'s *filter* argument.

    .. versionchanged:: 23.1.0 Accept strings with field names.
    """
    cls, names, attrs = None

    def include_(attribute, value):
        return (
            value.__class__ in cls
            or attribute.name in names
            or attribute in attrs
        )

    return include_


def x_include__mutmut_2(*what):
    """
    Create a filter that only allows *what*.

    Args:
        what (list[type, str, attrs.Attribute]):
            What to include. Can be a type, a name, or an attribute.

    Returns:
        Callable:
            A callable that can be passed to `attrs.asdict`'s and
            `attrs.astuple`'s *filter* argument.

    .. versionchanged:: 23.1.0 Accept strings with field names.
    """
    cls, names, attrs = _split_what(None)

    def include_(attribute, value):
        return (
            value.__class__ in cls
            or attribute.name in names
            or attribute in attrs
        )

    return include_


def x_include__mutmut_3(*what):
    """
    Create a filter that only allows *what*.

    Args:
        what (list[type, str, attrs.Attribute]):
            What to include. Can be a type, a name, or an attribute.

    Returns:
        Callable:
            A callable that can be passed to `attrs.asdict`'s and
            `attrs.astuple`'s *filter* argument.

    .. versionchanged:: 23.1.0 Accept strings with field names.
    """
    cls, names, attrs = _split_what(what)

    def include_(attribute, value):
        return (
            value.__class__ in cls
            or attribute.name in names and attribute in attrs
        )

    return include_


def x_include__mutmut_4(*what):
    """
    Create a filter that only allows *what*.

    Args:
        what (list[type, str, attrs.Attribute]):
            What to include. Can be a type, a name, or an attribute.

    Returns:
        Callable:
            A callable that can be passed to `attrs.asdict`'s and
            `attrs.astuple`'s *filter* argument.

    .. versionchanged:: 23.1.0 Accept strings with field names.
    """
    cls, names, attrs = _split_what(what)

    def include_(attribute, value):
        return (
            value.__class__ in cls and attribute.name in names
            or attribute in attrs
        )

    return include_


def x_include__mutmut_5(*what):
    """
    Create a filter that only allows *what*.

    Args:
        what (list[type, str, attrs.Attribute]):
            What to include. Can be a type, a name, or an attribute.

    Returns:
        Callable:
            A callable that can be passed to `attrs.asdict`'s and
            `attrs.astuple`'s *filter* argument.

    .. versionchanged:: 23.1.0 Accept strings with field names.
    """
    cls, names, attrs = _split_what(what)

    def include_(attribute, value):
        return (
            value.__class__ not in cls
            or attribute.name in names
            or attribute in attrs
        )

    return include_


def x_include__mutmut_6(*what):
    """
    Create a filter that only allows *what*.

    Args:
        what (list[type, str, attrs.Attribute]):
            What to include. Can be a type, a name, or an attribute.

    Returns:
        Callable:
            A callable that can be passed to `attrs.asdict`'s and
            `attrs.astuple`'s *filter* argument.

    .. versionchanged:: 23.1.0 Accept strings with field names.
    """
    cls, names, attrs = _split_what(what)

    def include_(attribute, value):
        return (
            value.__class__ in cls
            or attribute.name not in names
            or attribute in attrs
        )

    return include_


def x_include__mutmut_7(*what):
    """
    Create a filter that only allows *what*.

    Args:
        what (list[type, str, attrs.Attribute]):
            What to include. Can be a type, a name, or an attribute.

    Returns:
        Callable:
            A callable that can be passed to `attrs.asdict`'s and
            `attrs.astuple`'s *filter* argument.

    .. versionchanged:: 23.1.0 Accept strings with field names.
    """
    cls, names, attrs = _split_what(what)

    def include_(attribute, value):
        return (
            value.__class__ in cls
            or attribute.name in names
            or attribute not in attrs
        )

    return include_

x_include__mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
'x_include__mutmut_1': x_include__mutmut_1, 
    'x_include__mutmut_2': x_include__mutmut_2, 
    'x_include__mutmut_3': x_include__mutmut_3, 
    'x_include__mutmut_4': x_include__mutmut_4, 
    'x_include__mutmut_5': x_include__mutmut_5, 
    'x_include__mutmut_6': x_include__mutmut_6, 
    'x_include__mutmut_7': x_include__mutmut_7
}
x_include__mutmut_orig.__name__ = 'x_include'


def exclude(*what):
    args = [*what]# type: ignore
    kwargs = {}# type: ignore
    return _mutmut_trampoline(x_exclude__mutmut_orig, x_exclude__mutmut_mutants, args, kwargs, None)


def x_exclude__mutmut_orig(*what):
    """
    Create a filter that does **not** allow *what*.

    Args:
        what (list[type, str, attrs.Attribute]):
            What to exclude. Can be a type, a name, or an attribute.

    Returns:
        Callable:
            A callable that can be passed to `attrs.asdict`'s and
            `attrs.astuple`'s *filter* argument.

    .. versionchanged:: 23.3.0 Accept field name string as input argument
    """
    cls, names, attrs = _split_what(what)

    def exclude_(attribute, value):
        return not (
            value.__class__ in cls
            or attribute.name in names
            or attribute in attrs
        )

    return exclude_


def x_exclude__mutmut_1(*what):
    """
    Create a filter that does **not** allow *what*.

    Args:
        what (list[type, str, attrs.Attribute]):
            What to exclude. Can be a type, a name, or an attribute.

    Returns:
        Callable:
            A callable that can be passed to `attrs.asdict`'s and
            `attrs.astuple`'s *filter* argument.

    .. versionchanged:: 23.3.0 Accept field name string as input argument
    """
    cls, names, attrs = None

    def exclude_(attribute, value):
        return not (
            value.__class__ in cls
            or attribute.name in names
            or attribute in attrs
        )

    return exclude_


def x_exclude__mutmut_2(*what):
    """
    Create a filter that does **not** allow *what*.

    Args:
        what (list[type, str, attrs.Attribute]):
            What to exclude. Can be a type, a name, or an attribute.

    Returns:
        Callable:
            A callable that can be passed to `attrs.asdict`'s and
            `attrs.astuple`'s *filter* argument.

    .. versionchanged:: 23.3.0 Accept field name string as input argument
    """
    cls, names, attrs = _split_what(None)

    def exclude_(attribute, value):
        return not (
            value.__class__ in cls
            or attribute.name in names
            or attribute in attrs
        )

    return exclude_


def x_exclude__mutmut_3(*what):
    """
    Create a filter that does **not** allow *what*.

    Args:
        what (list[type, str, attrs.Attribute]):
            What to exclude. Can be a type, a name, or an attribute.

    Returns:
        Callable:
            A callable that can be passed to `attrs.asdict`'s and
            `attrs.astuple`'s *filter* argument.

    .. versionchanged:: 23.3.0 Accept field name string as input argument
    """
    cls, names, attrs = _split_what(what)

    def exclude_(attribute, value):
        return (
            value.__class__ in cls
            or attribute.name in names
            or attribute in attrs
        )

    return exclude_


def x_exclude__mutmut_4(*what):
    """
    Create a filter that does **not** allow *what*.

    Args:
        what (list[type, str, attrs.Attribute]):
            What to exclude. Can be a type, a name, or an attribute.

    Returns:
        Callable:
            A callable that can be passed to `attrs.asdict`'s and
            `attrs.astuple`'s *filter* argument.

    .. versionchanged:: 23.3.0 Accept field name string as input argument
    """
    cls, names, attrs = _split_what(what)

    def exclude_(attribute, value):
        return not (
            value.__class__ in cls
            or attribute.name in names and attribute in attrs
        )

    return exclude_


def x_exclude__mutmut_5(*what):
    """
    Create a filter that does **not** allow *what*.

    Args:
        what (list[type, str, attrs.Attribute]):
            What to exclude. Can be a type, a name, or an attribute.

    Returns:
        Callable:
            A callable that can be passed to `attrs.asdict`'s and
            `attrs.astuple`'s *filter* argument.

    .. versionchanged:: 23.3.0 Accept field name string as input argument
    """
    cls, names, attrs = _split_what(what)

    def exclude_(attribute, value):
        return not (
            value.__class__ in cls and attribute.name in names
            or attribute in attrs
        )

    return exclude_


def x_exclude__mutmut_6(*what):
    """
    Create a filter that does **not** allow *what*.

    Args:
        what (list[type, str, attrs.Attribute]):
            What to exclude. Can be a type, a name, or an attribute.

    Returns:
        Callable:
            A callable that can be passed to `attrs.asdict`'s and
            `attrs.astuple`'s *filter* argument.

    .. versionchanged:: 23.3.0 Accept field name string as input argument
    """
    cls, names, attrs = _split_what(what)

    def exclude_(attribute, value):
        return not (
            value.__class__ not in cls
            or attribute.name in names
            or attribute in attrs
        )

    return exclude_


def x_exclude__mutmut_7(*what):
    """
    Create a filter that does **not** allow *what*.

    Args:
        what (list[type, str, attrs.Attribute]):
            What to exclude. Can be a type, a name, or an attribute.

    Returns:
        Callable:
            A callable that can be passed to `attrs.asdict`'s and
            `attrs.astuple`'s *filter* argument.

    .. versionchanged:: 23.3.0 Accept field name string as input argument
    """
    cls, names, attrs = _split_what(what)

    def exclude_(attribute, value):
        return not (
            value.__class__ in cls
            or attribute.name not in names
            or attribute in attrs
        )

    return exclude_


def x_exclude__mutmut_8(*what):
    """
    Create a filter that does **not** allow *what*.

    Args:
        what (list[type, str, attrs.Attribute]):
            What to exclude. Can be a type, a name, or an attribute.

    Returns:
        Callable:
            A callable that can be passed to `attrs.asdict`'s and
            `attrs.astuple`'s *filter* argument.

    .. versionchanged:: 23.3.0 Accept field name string as input argument
    """
    cls, names, attrs = _split_what(what)

    def exclude_(attribute, value):
        return not (
            value.__class__ in cls
            or attribute.name in names
            or attribute not in attrs
        )

    return exclude_

x_exclude__mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
'x_exclude__mutmut_1': x_exclude__mutmut_1, 
    'x_exclude__mutmut_2': x_exclude__mutmut_2, 
    'x_exclude__mutmut_3': x_exclude__mutmut_3, 
    'x_exclude__mutmut_4': x_exclude__mutmut_4, 
    'x_exclude__mutmut_5': x_exclude__mutmut_5, 
    'x_exclude__mutmut_6': x_exclude__mutmut_6, 
    'x_exclude__mutmut_7': x_exclude__mutmut_7, 
    'x_exclude__mutmut_8': x_exclude__mutmut_8
}
x_exclude__mutmut_orig.__name__ = 'x_exclude'

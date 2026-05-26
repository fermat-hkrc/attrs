# SPDX-License-Identifier: MIT

"""
Commonly useful validators.
"""

import operator
import re

from contextlib import contextmanager
from re import Pattern

from ._config import get_run_validators, set_run_validators
from ._make import _AndValidator, and_, attrib, attrs
from .converters import default_if_none
from .exceptions import NotCallableError


__all__ = [
    "and_",
    "deep_iterable",
    "deep_mapping",
    "disabled",
    "ge",
    "get_disabled",
    "gt",
    "in_",
    "instance_of",
    "is_callable",
    "le",
    "lt",
    "matches_re",
    "max_len",
    "min_len",
    "not_",
    "optional",
    "or_",
    "set_disabled",
]
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


def set_disabled(disabled):
    args = [disabled]# type: ignore
    kwargs = {}# type: ignore
    return _mutmut_trampoline(x_set_disabled__mutmut_orig, x_set_disabled__mutmut_mutants, args, kwargs, None)


def x_set_disabled__mutmut_orig(disabled):
    """
    Globally disable or enable running validators.

    By default, they are run.

    Args:
        disabled (bool): If `True`, disable running all validators.

    .. warning::

        This function is not thread-safe!

    .. versionadded:: 21.3.0
    """
    set_run_validators(not disabled)


def x_set_disabled__mutmut_1(disabled):
    """
    Globally disable or enable running validators.

    By default, they are run.

    Args:
        disabled (bool): If `True`, disable running all validators.

    .. warning::

        This function is not thread-safe!

    .. versionadded:: 21.3.0
    """
    set_run_validators(None)


def x_set_disabled__mutmut_2(disabled):
    """
    Globally disable or enable running validators.

    By default, they are run.

    Args:
        disabled (bool): If `True`, disable running all validators.

    .. warning::

        This function is not thread-safe!

    .. versionadded:: 21.3.0
    """
    set_run_validators(disabled)

x_set_disabled__mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
'x_set_disabled__mutmut_1': x_set_disabled__mutmut_1, 
    'x_set_disabled__mutmut_2': x_set_disabled__mutmut_2
}
x_set_disabled__mutmut_orig.__name__ = 'x_set_disabled'


def get_disabled():
    args = []# type: ignore
    kwargs = {}# type: ignore
    return _mutmut_trampoline(x_get_disabled__mutmut_orig, x_get_disabled__mutmut_mutants, args, kwargs, None)


def x_get_disabled__mutmut_orig():
    """
    Return a bool indicating whether validators are currently disabled or not.

    Returns:
        bool:`True` if validators are currently disabled.

    .. versionadded:: 21.3.0
    """
    return not get_run_validators()


def x_get_disabled__mutmut_1():
    """
    Return a bool indicating whether validators are currently disabled or not.

    Returns:
        bool:`True` if validators are currently disabled.

    .. versionadded:: 21.3.0
    """
    return get_run_validators()

x_get_disabled__mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
'x_get_disabled__mutmut_1': x_get_disabled__mutmut_1
}
x_get_disabled__mutmut_orig.__name__ = 'x_get_disabled'


@contextmanager
def disabled():
    """
    Context manager that disables running validators within its context.

    .. warning::

        This context manager is not thread-safe!

    .. versionadded:: 21.3.0
    .. versionchanged:: 26.1.0 The contextmanager is nestable.
    """
    prev = get_run_validators()
    set_run_validators(False)
    try:
        yield
    finally:
        set_run_validators(prev)


@attrs(repr=False, slots=True, unsafe_hash=True)
class _InstanceOfValidator:
    type = attrib()

    def __call__(self, inst, attr, value):
        """
        We use a callable class to be able to change the ``__repr__``.
        """
        if not isinstance(value, self.type):
            msg = f"'{attr.name}' must be {self.type!r} (got {value!r} that is a {value.__class__!r})."
            raise TypeError(
                msg,
                attr,
                self.type,
                value,
            )

    def __repr__(self):
        return f"<instance_of validator for type {self.type!r}>"


def instance_of(type):
    args = [type]# type: ignore
    kwargs = {}# type: ignore
    return _mutmut_trampoline(x_instance_of__mutmut_orig, x_instance_of__mutmut_mutants, args, kwargs, None)


def x_instance_of__mutmut_orig(type):
    """
    A validator that raises a `TypeError` if the initializer is called with a
    wrong type for this particular attribute (checks are performed using
    `isinstance` therefore it's also valid to pass a tuple of types).

    Args:
        type (type | tuple[type]): The type to check for.

    Raises:
        TypeError:
            With a human readable error message, the attribute (of type
            `attrs.Attribute`), the expected type, and the value it got.
    """
    return _InstanceOfValidator(type)


def x_instance_of__mutmut_1(type):
    """
    A validator that raises a `TypeError` if the initializer is called with a
    wrong type for this particular attribute (checks are performed using
    `isinstance` therefore it's also valid to pass a tuple of types).

    Args:
        type (type | tuple[type]): The type to check for.

    Raises:
        TypeError:
            With a human readable error message, the attribute (of type
            `attrs.Attribute`), the expected type, and the value it got.
    """
    return _InstanceOfValidator(None)

x_instance_of__mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
'x_instance_of__mutmut_1': x_instance_of__mutmut_1
}
x_instance_of__mutmut_orig.__name__ = 'x_instance_of'


@attrs(repr=False, frozen=True, slots=True)
class _MatchesReValidator:
    pattern = attrib()
    match_func = attrib()

    def __call__(self, inst, attr, value):
        """
        We use a callable class to be able to change the ``__repr__``.
        """
        if not self.match_func(value):
            msg = f"'{attr.name}' must match regex {self.pattern.pattern!r} ({value!r} doesn't)"
            raise ValueError(
                msg,
                attr,
                self.pattern,
                value,
            )

    def __repr__(self):
        return f"<matches_re validator for pattern {self.pattern!r}>"


def matches_re(regex, flags=0, func=None):
    args = [regex, flags, func]# type: ignore
    kwargs = {}# type: ignore
    return _mutmut_trampoline(x_matches_re__mutmut_orig, x_matches_re__mutmut_mutants, args, kwargs, None)


def x_matches_re__mutmut_orig(regex, flags=0, func=None):
    r"""
    A validator that raises `ValueError` if the initializer is called with a
    string that doesn't match *regex*.

    Args:
        regex (str, re.Pattern):
            A regex string or precompiled pattern to match against

        flags (int):
            Flags that will be passed to the underlying re function (default 0)

        func (typing.Callable):
            Which underlying `re` function to call. Valid options are
            `re.fullmatch`, `re.search`, and `re.match`; the default `None`
            means `re.fullmatch`. For performance reasons, the pattern is
            always precompiled using `re.compile`.

    .. versionadded:: 19.2.0
    .. versionchanged:: 21.3.0 *regex* can be a pre-compiled pattern.
    """
    valid_funcs = (re.fullmatch, None, re.search, re.match)
    if func not in valid_funcs:
        msg = "'func' must be one of {}.".format(
            ", ".join(
                sorted((e and e.__name__) or "None" for e in set(valid_funcs))
            )
        )
        raise ValueError(msg)

    if isinstance(regex, Pattern):
        if flags:
            msg = "'flags' can only be used with a string pattern; pass flags to re.compile() instead"
            raise TypeError(msg)
        pattern = regex
    else:
        pattern = re.compile(regex, flags)

    if func is re.match:
        match_func = pattern.match
    elif func is re.search:
        match_func = pattern.search
    else:
        match_func = pattern.fullmatch

    return _MatchesReValidator(pattern, match_func)


def x_matches_re__mutmut_1(regex, flags=1, func=None):
    r"""
    A validator that raises `ValueError` if the initializer is called with a
    string that doesn't match *regex*.

    Args:
        regex (str, re.Pattern):
            A regex string or precompiled pattern to match against

        flags (int):
            Flags that will be passed to the underlying re function (default 0)

        func (typing.Callable):
            Which underlying `re` function to call. Valid options are
            `re.fullmatch`, `re.search`, and `re.match`; the default `None`
            means `re.fullmatch`. For performance reasons, the pattern is
            always precompiled using `re.compile`.

    .. versionadded:: 19.2.0
    .. versionchanged:: 21.3.0 *regex* can be a pre-compiled pattern.
    """
    valid_funcs = (re.fullmatch, None, re.search, re.match)
    if func not in valid_funcs:
        msg = "'func' must be one of {}.".format(
            ", ".join(
                sorted((e and e.__name__) or "None" for e in set(valid_funcs))
            )
        )
        raise ValueError(msg)

    if isinstance(regex, Pattern):
        if flags:
            msg = "'flags' can only be used with a string pattern; pass flags to re.compile() instead"
            raise TypeError(msg)
        pattern = regex
    else:
        pattern = re.compile(regex, flags)

    if func is re.match:
        match_func = pattern.match
    elif func is re.search:
        match_func = pattern.search
    else:
        match_func = pattern.fullmatch

    return _MatchesReValidator(pattern, match_func)


def x_matches_re__mutmut_2(regex, flags=0, func=None):
    r"""
    A validator that raises `ValueError` if the initializer is called with a
    string that doesn't match *regex*.

    Args:
        regex (str, re.Pattern):
            A regex string or precompiled pattern to match against

        flags (int):
            Flags that will be passed to the underlying re function (default 0)

        func (typing.Callable):
            Which underlying `re` function to call. Valid options are
            `re.fullmatch`, `re.search`, and `re.match`; the default `None`
            means `re.fullmatch`. For performance reasons, the pattern is
            always precompiled using `re.compile`.

    .. versionadded:: 19.2.0
    .. versionchanged:: 21.3.0 *regex* can be a pre-compiled pattern.
    """
    valid_funcs = None
    if func not in valid_funcs:
        msg = "'func' must be one of {}.".format(
            ", ".join(
                sorted((e and e.__name__) or "None" for e in set(valid_funcs))
            )
        )
        raise ValueError(msg)

    if isinstance(regex, Pattern):
        if flags:
            msg = "'flags' can only be used with a string pattern; pass flags to re.compile() instead"
            raise TypeError(msg)
        pattern = regex
    else:
        pattern = re.compile(regex, flags)

    if func is re.match:
        match_func = pattern.match
    elif func is re.search:
        match_func = pattern.search
    else:
        match_func = pattern.fullmatch

    return _MatchesReValidator(pattern, match_func)


def x_matches_re__mutmut_3(regex, flags=0, func=None):
    r"""
    A validator that raises `ValueError` if the initializer is called with a
    string that doesn't match *regex*.

    Args:
        regex (str, re.Pattern):
            A regex string or precompiled pattern to match against

        flags (int):
            Flags that will be passed to the underlying re function (default 0)

        func (typing.Callable):
            Which underlying `re` function to call. Valid options are
            `re.fullmatch`, `re.search`, and `re.match`; the default `None`
            means `re.fullmatch`. For performance reasons, the pattern is
            always precompiled using `re.compile`.

    .. versionadded:: 19.2.0
    .. versionchanged:: 21.3.0 *regex* can be a pre-compiled pattern.
    """
    valid_funcs = (re.fullmatch, None, re.search, re.match)
    if func in valid_funcs:
        msg = "'func' must be one of {}.".format(
            ", ".join(
                sorted((e and e.__name__) or "None" for e in set(valid_funcs))
            )
        )
        raise ValueError(msg)

    if isinstance(regex, Pattern):
        if flags:
            msg = "'flags' can only be used with a string pattern; pass flags to re.compile() instead"
            raise TypeError(msg)
        pattern = regex
    else:
        pattern = re.compile(regex, flags)

    if func is re.match:
        match_func = pattern.match
    elif func is re.search:
        match_func = pattern.search
    else:
        match_func = pattern.fullmatch

    return _MatchesReValidator(pattern, match_func)


def x_matches_re__mutmut_4(regex, flags=0, func=None):
    r"""
    A validator that raises `ValueError` if the initializer is called with a
    string that doesn't match *regex*.

    Args:
        regex (str, re.Pattern):
            A regex string or precompiled pattern to match against

        flags (int):
            Flags that will be passed to the underlying re function (default 0)

        func (typing.Callable):
            Which underlying `re` function to call. Valid options are
            `re.fullmatch`, `re.search`, and `re.match`; the default `None`
            means `re.fullmatch`. For performance reasons, the pattern is
            always precompiled using `re.compile`.

    .. versionadded:: 19.2.0
    .. versionchanged:: 21.3.0 *regex* can be a pre-compiled pattern.
    """
    valid_funcs = (re.fullmatch, None, re.search, re.match)
    if func not in valid_funcs:
        msg = None
        raise ValueError(msg)

    if isinstance(regex, Pattern):
        if flags:
            msg = "'flags' can only be used with a string pattern; pass flags to re.compile() instead"
            raise TypeError(msg)
        pattern = regex
    else:
        pattern = re.compile(regex, flags)

    if func is re.match:
        match_func = pattern.match
    elif func is re.search:
        match_func = pattern.search
    else:
        match_func = pattern.fullmatch

    return _MatchesReValidator(pattern, match_func)


def x_matches_re__mutmut_5(regex, flags=0, func=None):
    r"""
    A validator that raises `ValueError` if the initializer is called with a
    string that doesn't match *regex*.

    Args:
        regex (str, re.Pattern):
            A regex string or precompiled pattern to match against

        flags (int):
            Flags that will be passed to the underlying re function (default 0)

        func (typing.Callable):
            Which underlying `re` function to call. Valid options are
            `re.fullmatch`, `re.search`, and `re.match`; the default `None`
            means `re.fullmatch`. For performance reasons, the pattern is
            always precompiled using `re.compile`.

    .. versionadded:: 19.2.0
    .. versionchanged:: 21.3.0 *regex* can be a pre-compiled pattern.
    """
    valid_funcs = (re.fullmatch, None, re.search, re.match)
    if func not in valid_funcs:
        msg = "'func' must be one of {}.".format(
            None
        )
        raise ValueError(msg)

    if isinstance(regex, Pattern):
        if flags:
            msg = "'flags' can only be used with a string pattern; pass flags to re.compile() instead"
            raise TypeError(msg)
        pattern = regex
    else:
        pattern = re.compile(regex, flags)

    if func is re.match:
        match_func = pattern.match
    elif func is re.search:
        match_func = pattern.search
    else:
        match_func = pattern.fullmatch

    return _MatchesReValidator(pattern, match_func)


def x_matches_re__mutmut_6(regex, flags=0, func=None):
    r"""
    A validator that raises `ValueError` if the initializer is called with a
    string that doesn't match *regex*.

    Args:
        regex (str, re.Pattern):
            A regex string or precompiled pattern to match against

        flags (int):
            Flags that will be passed to the underlying re function (default 0)

        func (typing.Callable):
            Which underlying `re` function to call. Valid options are
            `re.fullmatch`, `re.search`, and `re.match`; the default `None`
            means `re.fullmatch`. For performance reasons, the pattern is
            always precompiled using `re.compile`.

    .. versionadded:: 19.2.0
    .. versionchanged:: 21.3.0 *regex* can be a pre-compiled pattern.
    """
    valid_funcs = (re.fullmatch, None, re.search, re.match)
    if func not in valid_funcs:
        msg = "XX'func' must be one of {}.XX".format(
            ", ".join(
                sorted((e and e.__name__) or "None" for e in set(valid_funcs))
            )
        )
        raise ValueError(msg)

    if isinstance(regex, Pattern):
        if flags:
            msg = "'flags' can only be used with a string pattern; pass flags to re.compile() instead"
            raise TypeError(msg)
        pattern = regex
    else:
        pattern = re.compile(regex, flags)

    if func is re.match:
        match_func = pattern.match
    elif func is re.search:
        match_func = pattern.search
    else:
        match_func = pattern.fullmatch

    return _MatchesReValidator(pattern, match_func)


def x_matches_re__mutmut_7(regex, flags=0, func=None):
    r"""
    A validator that raises `ValueError` if the initializer is called with a
    string that doesn't match *regex*.

    Args:
        regex (str, re.Pattern):
            A regex string or precompiled pattern to match against

        flags (int):
            Flags that will be passed to the underlying re function (default 0)

        func (typing.Callable):
            Which underlying `re` function to call. Valid options are
            `re.fullmatch`, `re.search`, and `re.match`; the default `None`
            means `re.fullmatch`. For performance reasons, the pattern is
            always precompiled using `re.compile`.

    .. versionadded:: 19.2.0
    .. versionchanged:: 21.3.0 *regex* can be a pre-compiled pattern.
    """
    valid_funcs = (re.fullmatch, None, re.search, re.match)
    if func not in valid_funcs:
        msg = "'FUNC' MUST BE ONE OF {}.".format(
            ", ".join(
                sorted((e and e.__name__) or "None" for e in set(valid_funcs))
            )
        )
        raise ValueError(msg)

    if isinstance(regex, Pattern):
        if flags:
            msg = "'flags' can only be used with a string pattern; pass flags to re.compile() instead"
            raise TypeError(msg)
        pattern = regex
    else:
        pattern = re.compile(regex, flags)

    if func is re.match:
        match_func = pattern.match
    elif func is re.search:
        match_func = pattern.search
    else:
        match_func = pattern.fullmatch

    return _MatchesReValidator(pattern, match_func)


def x_matches_re__mutmut_8(regex, flags=0, func=None):
    r"""
    A validator that raises `ValueError` if the initializer is called with a
    string that doesn't match *regex*.

    Args:
        regex (str, re.Pattern):
            A regex string or precompiled pattern to match against

        flags (int):
            Flags that will be passed to the underlying re function (default 0)

        func (typing.Callable):
            Which underlying `re` function to call. Valid options are
            `re.fullmatch`, `re.search`, and `re.match`; the default `None`
            means `re.fullmatch`. For performance reasons, the pattern is
            always precompiled using `re.compile`.

    .. versionadded:: 19.2.0
    .. versionchanged:: 21.3.0 *regex* can be a pre-compiled pattern.
    """
    valid_funcs = (re.fullmatch, None, re.search, re.match)
    if func not in valid_funcs:
        msg = "'func' must be one of {}.".format(
            ", ".join(
                None
            )
        )
        raise ValueError(msg)

    if isinstance(regex, Pattern):
        if flags:
            msg = "'flags' can only be used with a string pattern; pass flags to re.compile() instead"
            raise TypeError(msg)
        pattern = regex
    else:
        pattern = re.compile(regex, flags)

    if func is re.match:
        match_func = pattern.match
    elif func is re.search:
        match_func = pattern.search
    else:
        match_func = pattern.fullmatch

    return _MatchesReValidator(pattern, match_func)


def x_matches_re__mutmut_9(regex, flags=0, func=None):
    r"""
    A validator that raises `ValueError` if the initializer is called with a
    string that doesn't match *regex*.

    Args:
        regex (str, re.Pattern):
            A regex string or precompiled pattern to match against

        flags (int):
            Flags that will be passed to the underlying re function (default 0)

        func (typing.Callable):
            Which underlying `re` function to call. Valid options are
            `re.fullmatch`, `re.search`, and `re.match`; the default `None`
            means `re.fullmatch`. For performance reasons, the pattern is
            always precompiled using `re.compile`.

    .. versionadded:: 19.2.0
    .. versionchanged:: 21.3.0 *regex* can be a pre-compiled pattern.
    """
    valid_funcs = (re.fullmatch, None, re.search, re.match)
    if func not in valid_funcs:
        msg = "'func' must be one of {}.".format(
            "XX, XX".join(
                sorted((e and e.__name__) or "None" for e in set(valid_funcs))
            )
        )
        raise ValueError(msg)

    if isinstance(regex, Pattern):
        if flags:
            msg = "'flags' can only be used with a string pattern; pass flags to re.compile() instead"
            raise TypeError(msg)
        pattern = regex
    else:
        pattern = re.compile(regex, flags)

    if func is re.match:
        match_func = pattern.match
    elif func is re.search:
        match_func = pattern.search
    else:
        match_func = pattern.fullmatch

    return _MatchesReValidator(pattern, match_func)


def x_matches_re__mutmut_10(regex, flags=0, func=None):
    r"""
    A validator that raises `ValueError` if the initializer is called with a
    string that doesn't match *regex*.

    Args:
        regex (str, re.Pattern):
            A regex string or precompiled pattern to match against

        flags (int):
            Flags that will be passed to the underlying re function (default 0)

        func (typing.Callable):
            Which underlying `re` function to call. Valid options are
            `re.fullmatch`, `re.search`, and `re.match`; the default `None`
            means `re.fullmatch`. For performance reasons, the pattern is
            always precompiled using `re.compile`.

    .. versionadded:: 19.2.0
    .. versionchanged:: 21.3.0 *regex* can be a pre-compiled pattern.
    """
    valid_funcs = (re.fullmatch, None, re.search, re.match)
    if func not in valid_funcs:
        msg = "'func' must be one of {}.".format(
            ", ".join(
                sorted(None)
            )
        )
        raise ValueError(msg)

    if isinstance(regex, Pattern):
        if flags:
            msg = "'flags' can only be used with a string pattern; pass flags to re.compile() instead"
            raise TypeError(msg)
        pattern = regex
    else:
        pattern = re.compile(regex, flags)

    if func is re.match:
        match_func = pattern.match
    elif func is re.search:
        match_func = pattern.search
    else:
        match_func = pattern.fullmatch

    return _MatchesReValidator(pattern, match_func)


def x_matches_re__mutmut_11(regex, flags=0, func=None):
    r"""
    A validator that raises `ValueError` if the initializer is called with a
    string that doesn't match *regex*.

    Args:
        regex (str, re.Pattern):
            A regex string or precompiled pattern to match against

        flags (int):
            Flags that will be passed to the underlying re function (default 0)

        func (typing.Callable):
            Which underlying `re` function to call. Valid options are
            `re.fullmatch`, `re.search`, and `re.match`; the default `None`
            means `re.fullmatch`. For performance reasons, the pattern is
            always precompiled using `re.compile`.

    .. versionadded:: 19.2.0
    .. versionchanged:: 21.3.0 *regex* can be a pre-compiled pattern.
    """
    valid_funcs = (re.fullmatch, None, re.search, re.match)
    if func not in valid_funcs:
        msg = "'func' must be one of {}.".format(
            ", ".join(
                sorted((e and e.__name__) and "None" for e in set(valid_funcs))
            )
        )
        raise ValueError(msg)

    if isinstance(regex, Pattern):
        if flags:
            msg = "'flags' can only be used with a string pattern; pass flags to re.compile() instead"
            raise TypeError(msg)
        pattern = regex
    else:
        pattern = re.compile(regex, flags)

    if func is re.match:
        match_func = pattern.match
    elif func is re.search:
        match_func = pattern.search
    else:
        match_func = pattern.fullmatch

    return _MatchesReValidator(pattern, match_func)


def x_matches_re__mutmut_12(regex, flags=0, func=None):
    r"""
    A validator that raises `ValueError` if the initializer is called with a
    string that doesn't match *regex*.

    Args:
        regex (str, re.Pattern):
            A regex string or precompiled pattern to match against

        flags (int):
            Flags that will be passed to the underlying re function (default 0)

        func (typing.Callable):
            Which underlying `re` function to call. Valid options are
            `re.fullmatch`, `re.search`, and `re.match`; the default `None`
            means `re.fullmatch`. For performance reasons, the pattern is
            always precompiled using `re.compile`.

    .. versionadded:: 19.2.0
    .. versionchanged:: 21.3.0 *regex* can be a pre-compiled pattern.
    """
    valid_funcs = (re.fullmatch, None, re.search, re.match)
    if func not in valid_funcs:
        msg = "'func' must be one of {}.".format(
            ", ".join(
                sorted((e or e.__name__) or "None" for e in set(valid_funcs))
            )
        )
        raise ValueError(msg)

    if isinstance(regex, Pattern):
        if flags:
            msg = "'flags' can only be used with a string pattern; pass flags to re.compile() instead"
            raise TypeError(msg)
        pattern = regex
    else:
        pattern = re.compile(regex, flags)

    if func is re.match:
        match_func = pattern.match
    elif func is re.search:
        match_func = pattern.search
    else:
        match_func = pattern.fullmatch

    return _MatchesReValidator(pattern, match_func)


def x_matches_re__mutmut_13(regex, flags=0, func=None):
    r"""
    A validator that raises `ValueError` if the initializer is called with a
    string that doesn't match *regex*.

    Args:
        regex (str, re.Pattern):
            A regex string or precompiled pattern to match against

        flags (int):
            Flags that will be passed to the underlying re function (default 0)

        func (typing.Callable):
            Which underlying `re` function to call. Valid options are
            `re.fullmatch`, `re.search`, and `re.match`; the default `None`
            means `re.fullmatch`. For performance reasons, the pattern is
            always precompiled using `re.compile`.

    .. versionadded:: 19.2.0
    .. versionchanged:: 21.3.0 *regex* can be a pre-compiled pattern.
    """
    valid_funcs = (re.fullmatch, None, re.search, re.match)
    if func not in valid_funcs:
        msg = "'func' must be one of {}.".format(
            ", ".join(
                sorted((e and e.__name__) or "XXNoneXX" for e in set(valid_funcs))
            )
        )
        raise ValueError(msg)

    if isinstance(regex, Pattern):
        if flags:
            msg = "'flags' can only be used with a string pattern; pass flags to re.compile() instead"
            raise TypeError(msg)
        pattern = regex
    else:
        pattern = re.compile(regex, flags)

    if func is re.match:
        match_func = pattern.match
    elif func is re.search:
        match_func = pattern.search
    else:
        match_func = pattern.fullmatch

    return _MatchesReValidator(pattern, match_func)


def x_matches_re__mutmut_14(regex, flags=0, func=None):
    r"""
    A validator that raises `ValueError` if the initializer is called with a
    string that doesn't match *regex*.

    Args:
        regex (str, re.Pattern):
            A regex string or precompiled pattern to match against

        flags (int):
            Flags that will be passed to the underlying re function (default 0)

        func (typing.Callable):
            Which underlying `re` function to call. Valid options are
            `re.fullmatch`, `re.search`, and `re.match`; the default `None`
            means `re.fullmatch`. For performance reasons, the pattern is
            always precompiled using `re.compile`.

    .. versionadded:: 19.2.0
    .. versionchanged:: 21.3.0 *regex* can be a pre-compiled pattern.
    """
    valid_funcs = (re.fullmatch, None, re.search, re.match)
    if func not in valid_funcs:
        msg = "'func' must be one of {}.".format(
            ", ".join(
                sorted((e and e.__name__) or "none" for e in set(valid_funcs))
            )
        )
        raise ValueError(msg)

    if isinstance(regex, Pattern):
        if flags:
            msg = "'flags' can only be used with a string pattern; pass flags to re.compile() instead"
            raise TypeError(msg)
        pattern = regex
    else:
        pattern = re.compile(regex, flags)

    if func is re.match:
        match_func = pattern.match
    elif func is re.search:
        match_func = pattern.search
    else:
        match_func = pattern.fullmatch

    return _MatchesReValidator(pattern, match_func)


def x_matches_re__mutmut_15(regex, flags=0, func=None):
    r"""
    A validator that raises `ValueError` if the initializer is called with a
    string that doesn't match *regex*.

    Args:
        regex (str, re.Pattern):
            A regex string or precompiled pattern to match against

        flags (int):
            Flags that will be passed to the underlying re function (default 0)

        func (typing.Callable):
            Which underlying `re` function to call. Valid options are
            `re.fullmatch`, `re.search`, and `re.match`; the default `None`
            means `re.fullmatch`. For performance reasons, the pattern is
            always precompiled using `re.compile`.

    .. versionadded:: 19.2.0
    .. versionchanged:: 21.3.0 *regex* can be a pre-compiled pattern.
    """
    valid_funcs = (re.fullmatch, None, re.search, re.match)
    if func not in valid_funcs:
        msg = "'func' must be one of {}.".format(
            ", ".join(
                sorted((e and e.__name__) or "NONE" for e in set(valid_funcs))
            )
        )
        raise ValueError(msg)

    if isinstance(regex, Pattern):
        if flags:
            msg = "'flags' can only be used with a string pattern; pass flags to re.compile() instead"
            raise TypeError(msg)
        pattern = regex
    else:
        pattern = re.compile(regex, flags)

    if func is re.match:
        match_func = pattern.match
    elif func is re.search:
        match_func = pattern.search
    else:
        match_func = pattern.fullmatch

    return _MatchesReValidator(pattern, match_func)


def x_matches_re__mutmut_16(regex, flags=0, func=None):
    r"""
    A validator that raises `ValueError` if the initializer is called with a
    string that doesn't match *regex*.

    Args:
        regex (str, re.Pattern):
            A regex string or precompiled pattern to match against

        flags (int):
            Flags that will be passed to the underlying re function (default 0)

        func (typing.Callable):
            Which underlying `re` function to call. Valid options are
            `re.fullmatch`, `re.search`, and `re.match`; the default `None`
            means `re.fullmatch`. For performance reasons, the pattern is
            always precompiled using `re.compile`.

    .. versionadded:: 19.2.0
    .. versionchanged:: 21.3.0 *regex* can be a pre-compiled pattern.
    """
    valid_funcs = (re.fullmatch, None, re.search, re.match)
    if func not in valid_funcs:
        msg = "'func' must be one of {}.".format(
            ", ".join(
                sorted((e and e.__name__) or "None" for e in set(None))
            )
        )
        raise ValueError(msg)

    if isinstance(regex, Pattern):
        if flags:
            msg = "'flags' can only be used with a string pattern; pass flags to re.compile() instead"
            raise TypeError(msg)
        pattern = regex
    else:
        pattern = re.compile(regex, flags)

    if func is re.match:
        match_func = pattern.match
    elif func is re.search:
        match_func = pattern.search
    else:
        match_func = pattern.fullmatch

    return _MatchesReValidator(pattern, match_func)


def x_matches_re__mutmut_17(regex, flags=0, func=None):
    r"""
    A validator that raises `ValueError` if the initializer is called with a
    string that doesn't match *regex*.

    Args:
        regex (str, re.Pattern):
            A regex string or precompiled pattern to match against

        flags (int):
            Flags that will be passed to the underlying re function (default 0)

        func (typing.Callable):
            Which underlying `re` function to call. Valid options are
            `re.fullmatch`, `re.search`, and `re.match`; the default `None`
            means `re.fullmatch`. For performance reasons, the pattern is
            always precompiled using `re.compile`.

    .. versionadded:: 19.2.0
    .. versionchanged:: 21.3.0 *regex* can be a pre-compiled pattern.
    """
    valid_funcs = (re.fullmatch, None, re.search, re.match)
    if func not in valid_funcs:
        msg = "'func' must be one of {}.".format(
            ", ".join(
                sorted((e and e.__name__) or "None" for e in set(valid_funcs))
            )
        )
        raise ValueError(None)

    if isinstance(regex, Pattern):
        if flags:
            msg = "'flags' can only be used with a string pattern; pass flags to re.compile() instead"
            raise TypeError(msg)
        pattern = regex
    else:
        pattern = re.compile(regex, flags)

    if func is re.match:
        match_func = pattern.match
    elif func is re.search:
        match_func = pattern.search
    else:
        match_func = pattern.fullmatch

    return _MatchesReValidator(pattern, match_func)


def x_matches_re__mutmut_18(regex, flags=0, func=None):
    r"""
    A validator that raises `ValueError` if the initializer is called with a
    string that doesn't match *regex*.

    Args:
        regex (str, re.Pattern):
            A regex string or precompiled pattern to match against

        flags (int):
            Flags that will be passed to the underlying re function (default 0)

        func (typing.Callable):
            Which underlying `re` function to call. Valid options are
            `re.fullmatch`, `re.search`, and `re.match`; the default `None`
            means `re.fullmatch`. For performance reasons, the pattern is
            always precompiled using `re.compile`.

    .. versionadded:: 19.2.0
    .. versionchanged:: 21.3.0 *regex* can be a pre-compiled pattern.
    """
    valid_funcs = (re.fullmatch, None, re.search, re.match)
    if func not in valid_funcs:
        msg = "'func' must be one of {}.".format(
            ", ".join(
                sorted((e and e.__name__) or "None" for e in set(valid_funcs))
            )
        )
        raise ValueError(msg)

    if isinstance(regex, Pattern):
        if flags:
            msg = None
            raise TypeError(msg)
        pattern = regex
    else:
        pattern = re.compile(regex, flags)

    if func is re.match:
        match_func = pattern.match
    elif func is re.search:
        match_func = pattern.search
    else:
        match_func = pattern.fullmatch

    return _MatchesReValidator(pattern, match_func)


def x_matches_re__mutmut_19(regex, flags=0, func=None):
    r"""
    A validator that raises `ValueError` if the initializer is called with a
    string that doesn't match *regex*.

    Args:
        regex (str, re.Pattern):
            A regex string or precompiled pattern to match against

        flags (int):
            Flags that will be passed to the underlying re function (default 0)

        func (typing.Callable):
            Which underlying `re` function to call. Valid options are
            `re.fullmatch`, `re.search`, and `re.match`; the default `None`
            means `re.fullmatch`. For performance reasons, the pattern is
            always precompiled using `re.compile`.

    .. versionadded:: 19.2.0
    .. versionchanged:: 21.3.0 *regex* can be a pre-compiled pattern.
    """
    valid_funcs = (re.fullmatch, None, re.search, re.match)
    if func not in valid_funcs:
        msg = "'func' must be one of {}.".format(
            ", ".join(
                sorted((e and e.__name__) or "None" for e in set(valid_funcs))
            )
        )
        raise ValueError(msg)

    if isinstance(regex, Pattern):
        if flags:
            msg = "XX'flags' can only be used with a string pattern; pass flags to re.compile() insteadXX"
            raise TypeError(msg)
        pattern = regex
    else:
        pattern = re.compile(regex, flags)

    if func is re.match:
        match_func = pattern.match
    elif func is re.search:
        match_func = pattern.search
    else:
        match_func = pattern.fullmatch

    return _MatchesReValidator(pattern, match_func)


def x_matches_re__mutmut_20(regex, flags=0, func=None):
    r"""
    A validator that raises `ValueError` if the initializer is called with a
    string that doesn't match *regex*.

    Args:
        regex (str, re.Pattern):
            A regex string or precompiled pattern to match against

        flags (int):
            Flags that will be passed to the underlying re function (default 0)

        func (typing.Callable):
            Which underlying `re` function to call. Valid options are
            `re.fullmatch`, `re.search`, and `re.match`; the default `None`
            means `re.fullmatch`. For performance reasons, the pattern is
            always precompiled using `re.compile`.

    .. versionadded:: 19.2.0
    .. versionchanged:: 21.3.0 *regex* can be a pre-compiled pattern.
    """
    valid_funcs = (re.fullmatch, None, re.search, re.match)
    if func not in valid_funcs:
        msg = "'func' must be one of {}.".format(
            ", ".join(
                sorted((e and e.__name__) or "None" for e in set(valid_funcs))
            )
        )
        raise ValueError(msg)

    if isinstance(regex, Pattern):
        if flags:
            msg = "'FLAGS' CAN ONLY BE USED WITH A STRING PATTERN; PASS FLAGS TO RE.COMPILE() INSTEAD"
            raise TypeError(msg)
        pattern = regex
    else:
        pattern = re.compile(regex, flags)

    if func is re.match:
        match_func = pattern.match
    elif func is re.search:
        match_func = pattern.search
    else:
        match_func = pattern.fullmatch

    return _MatchesReValidator(pattern, match_func)


def x_matches_re__mutmut_21(regex, flags=0, func=None):
    r"""
    A validator that raises `ValueError` if the initializer is called with a
    string that doesn't match *regex*.

    Args:
        regex (str, re.Pattern):
            A regex string or precompiled pattern to match against

        flags (int):
            Flags that will be passed to the underlying re function (default 0)

        func (typing.Callable):
            Which underlying `re` function to call. Valid options are
            `re.fullmatch`, `re.search`, and `re.match`; the default `None`
            means `re.fullmatch`. For performance reasons, the pattern is
            always precompiled using `re.compile`.

    .. versionadded:: 19.2.0
    .. versionchanged:: 21.3.0 *regex* can be a pre-compiled pattern.
    """
    valid_funcs = (re.fullmatch, None, re.search, re.match)
    if func not in valid_funcs:
        msg = "'func' must be one of {}.".format(
            ", ".join(
                sorted((e and e.__name__) or "None" for e in set(valid_funcs))
            )
        )
        raise ValueError(msg)

    if isinstance(regex, Pattern):
        if flags:
            msg = "'flags' can only be used with a string pattern; pass flags to re.compile() instead"
            raise TypeError(None)
        pattern = regex
    else:
        pattern = re.compile(regex, flags)

    if func is re.match:
        match_func = pattern.match
    elif func is re.search:
        match_func = pattern.search
    else:
        match_func = pattern.fullmatch

    return _MatchesReValidator(pattern, match_func)


def x_matches_re__mutmut_22(regex, flags=0, func=None):
    r"""
    A validator that raises `ValueError` if the initializer is called with a
    string that doesn't match *regex*.

    Args:
        regex (str, re.Pattern):
            A regex string or precompiled pattern to match against

        flags (int):
            Flags that will be passed to the underlying re function (default 0)

        func (typing.Callable):
            Which underlying `re` function to call. Valid options are
            `re.fullmatch`, `re.search`, and `re.match`; the default `None`
            means `re.fullmatch`. For performance reasons, the pattern is
            always precompiled using `re.compile`.

    .. versionadded:: 19.2.0
    .. versionchanged:: 21.3.0 *regex* can be a pre-compiled pattern.
    """
    valid_funcs = (re.fullmatch, None, re.search, re.match)
    if func not in valid_funcs:
        msg = "'func' must be one of {}.".format(
            ", ".join(
                sorted((e and e.__name__) or "None" for e in set(valid_funcs))
            )
        )
        raise ValueError(msg)

    if isinstance(regex, Pattern):
        if flags:
            msg = "'flags' can only be used with a string pattern; pass flags to re.compile() instead"
            raise TypeError(msg)
        pattern = None
    else:
        pattern = re.compile(regex, flags)

    if func is re.match:
        match_func = pattern.match
    elif func is re.search:
        match_func = pattern.search
    else:
        match_func = pattern.fullmatch

    return _MatchesReValidator(pattern, match_func)


def x_matches_re__mutmut_23(regex, flags=0, func=None):
    r"""
    A validator that raises `ValueError` if the initializer is called with a
    string that doesn't match *regex*.

    Args:
        regex (str, re.Pattern):
            A regex string or precompiled pattern to match against

        flags (int):
            Flags that will be passed to the underlying re function (default 0)

        func (typing.Callable):
            Which underlying `re` function to call. Valid options are
            `re.fullmatch`, `re.search`, and `re.match`; the default `None`
            means `re.fullmatch`. For performance reasons, the pattern is
            always precompiled using `re.compile`.

    .. versionadded:: 19.2.0
    .. versionchanged:: 21.3.0 *regex* can be a pre-compiled pattern.
    """
    valid_funcs = (re.fullmatch, None, re.search, re.match)
    if func not in valid_funcs:
        msg = "'func' must be one of {}.".format(
            ", ".join(
                sorted((e and e.__name__) or "None" for e in set(valid_funcs))
            )
        )
        raise ValueError(msg)

    if isinstance(regex, Pattern):
        if flags:
            msg = "'flags' can only be used with a string pattern; pass flags to re.compile() instead"
            raise TypeError(msg)
        pattern = regex
    else:
        pattern = None

    if func is re.match:
        match_func = pattern.match
    elif func is re.search:
        match_func = pattern.search
    else:
        match_func = pattern.fullmatch

    return _MatchesReValidator(pattern, match_func)


def x_matches_re__mutmut_24(regex, flags=0, func=None):
    r"""
    A validator that raises `ValueError` if the initializer is called with a
    string that doesn't match *regex*.

    Args:
        regex (str, re.Pattern):
            A regex string or precompiled pattern to match against

        flags (int):
            Flags that will be passed to the underlying re function (default 0)

        func (typing.Callable):
            Which underlying `re` function to call. Valid options are
            `re.fullmatch`, `re.search`, and `re.match`; the default `None`
            means `re.fullmatch`. For performance reasons, the pattern is
            always precompiled using `re.compile`.

    .. versionadded:: 19.2.0
    .. versionchanged:: 21.3.0 *regex* can be a pre-compiled pattern.
    """
    valid_funcs = (re.fullmatch, None, re.search, re.match)
    if func not in valid_funcs:
        msg = "'func' must be one of {}.".format(
            ", ".join(
                sorted((e and e.__name__) or "None" for e in set(valid_funcs))
            )
        )
        raise ValueError(msg)

    if isinstance(regex, Pattern):
        if flags:
            msg = "'flags' can only be used with a string pattern; pass flags to re.compile() instead"
            raise TypeError(msg)
        pattern = regex
    else:
        pattern = re.compile(None, flags)

    if func is re.match:
        match_func = pattern.match
    elif func is re.search:
        match_func = pattern.search
    else:
        match_func = pattern.fullmatch

    return _MatchesReValidator(pattern, match_func)


def x_matches_re__mutmut_25(regex, flags=0, func=None):
    r"""
    A validator that raises `ValueError` if the initializer is called with a
    string that doesn't match *regex*.

    Args:
        regex (str, re.Pattern):
            A regex string or precompiled pattern to match against

        flags (int):
            Flags that will be passed to the underlying re function (default 0)

        func (typing.Callable):
            Which underlying `re` function to call. Valid options are
            `re.fullmatch`, `re.search`, and `re.match`; the default `None`
            means `re.fullmatch`. For performance reasons, the pattern is
            always precompiled using `re.compile`.

    .. versionadded:: 19.2.0
    .. versionchanged:: 21.3.0 *regex* can be a pre-compiled pattern.
    """
    valid_funcs = (re.fullmatch, None, re.search, re.match)
    if func not in valid_funcs:
        msg = "'func' must be one of {}.".format(
            ", ".join(
                sorted((e and e.__name__) or "None" for e in set(valid_funcs))
            )
        )
        raise ValueError(msg)

    if isinstance(regex, Pattern):
        if flags:
            msg = "'flags' can only be used with a string pattern; pass flags to re.compile() instead"
            raise TypeError(msg)
        pattern = regex
    else:
        pattern = re.compile(regex, None)

    if func is re.match:
        match_func = pattern.match
    elif func is re.search:
        match_func = pattern.search
    else:
        match_func = pattern.fullmatch

    return _MatchesReValidator(pattern, match_func)


def x_matches_re__mutmut_26(regex, flags=0, func=None):
    r"""
    A validator that raises `ValueError` if the initializer is called with a
    string that doesn't match *regex*.

    Args:
        regex (str, re.Pattern):
            A regex string or precompiled pattern to match against

        flags (int):
            Flags that will be passed to the underlying re function (default 0)

        func (typing.Callable):
            Which underlying `re` function to call. Valid options are
            `re.fullmatch`, `re.search`, and `re.match`; the default `None`
            means `re.fullmatch`. For performance reasons, the pattern is
            always precompiled using `re.compile`.

    .. versionadded:: 19.2.0
    .. versionchanged:: 21.3.0 *regex* can be a pre-compiled pattern.
    """
    valid_funcs = (re.fullmatch, None, re.search, re.match)
    if func not in valid_funcs:
        msg = "'func' must be one of {}.".format(
            ", ".join(
                sorted((e and e.__name__) or "None" for e in set(valid_funcs))
            )
        )
        raise ValueError(msg)

    if isinstance(regex, Pattern):
        if flags:
            msg = "'flags' can only be used with a string pattern; pass flags to re.compile() instead"
            raise TypeError(msg)
        pattern = regex
    else:
        pattern = re.compile(flags)

    if func is re.match:
        match_func = pattern.match
    elif func is re.search:
        match_func = pattern.search
    else:
        match_func = pattern.fullmatch

    return _MatchesReValidator(pattern, match_func)


def x_matches_re__mutmut_27(regex, flags=0, func=None):
    r"""
    A validator that raises `ValueError` if the initializer is called with a
    string that doesn't match *regex*.

    Args:
        regex (str, re.Pattern):
            A regex string or precompiled pattern to match against

        flags (int):
            Flags that will be passed to the underlying re function (default 0)

        func (typing.Callable):
            Which underlying `re` function to call. Valid options are
            `re.fullmatch`, `re.search`, and `re.match`; the default `None`
            means `re.fullmatch`. For performance reasons, the pattern is
            always precompiled using `re.compile`.

    .. versionadded:: 19.2.0
    .. versionchanged:: 21.3.0 *regex* can be a pre-compiled pattern.
    """
    valid_funcs = (re.fullmatch, None, re.search, re.match)
    if func not in valid_funcs:
        msg = "'func' must be one of {}.".format(
            ", ".join(
                sorted((e and e.__name__) or "None" for e in set(valid_funcs))
            )
        )
        raise ValueError(msg)

    if isinstance(regex, Pattern):
        if flags:
            msg = "'flags' can only be used with a string pattern; pass flags to re.compile() instead"
            raise TypeError(msg)
        pattern = regex
    else:
        pattern = re.compile(regex, )

    if func is re.match:
        match_func = pattern.match
    elif func is re.search:
        match_func = pattern.search
    else:
        match_func = pattern.fullmatch

    return _MatchesReValidator(pattern, match_func)


def x_matches_re__mutmut_28(regex, flags=0, func=None):
    r"""
    A validator that raises `ValueError` if the initializer is called with a
    string that doesn't match *regex*.

    Args:
        regex (str, re.Pattern):
            A regex string or precompiled pattern to match against

        flags (int):
            Flags that will be passed to the underlying re function (default 0)

        func (typing.Callable):
            Which underlying `re` function to call. Valid options are
            `re.fullmatch`, `re.search`, and `re.match`; the default `None`
            means `re.fullmatch`. For performance reasons, the pattern is
            always precompiled using `re.compile`.

    .. versionadded:: 19.2.0
    .. versionchanged:: 21.3.0 *regex* can be a pre-compiled pattern.
    """
    valid_funcs = (re.fullmatch, None, re.search, re.match)
    if func not in valid_funcs:
        msg = "'func' must be one of {}.".format(
            ", ".join(
                sorted((e and e.__name__) or "None" for e in set(valid_funcs))
            )
        )
        raise ValueError(msg)

    if isinstance(regex, Pattern):
        if flags:
            msg = "'flags' can only be used with a string pattern; pass flags to re.compile() instead"
            raise TypeError(msg)
        pattern = regex
    else:
        pattern = re.compile(regex, flags)

    if func is not re.match:
        match_func = pattern.match
    elif func is re.search:
        match_func = pattern.search
    else:
        match_func = pattern.fullmatch

    return _MatchesReValidator(pattern, match_func)


def x_matches_re__mutmut_29(regex, flags=0, func=None):
    r"""
    A validator that raises `ValueError` if the initializer is called with a
    string that doesn't match *regex*.

    Args:
        regex (str, re.Pattern):
            A regex string or precompiled pattern to match against

        flags (int):
            Flags that will be passed to the underlying re function (default 0)

        func (typing.Callable):
            Which underlying `re` function to call. Valid options are
            `re.fullmatch`, `re.search`, and `re.match`; the default `None`
            means `re.fullmatch`. For performance reasons, the pattern is
            always precompiled using `re.compile`.

    .. versionadded:: 19.2.0
    .. versionchanged:: 21.3.0 *regex* can be a pre-compiled pattern.
    """
    valid_funcs = (re.fullmatch, None, re.search, re.match)
    if func not in valid_funcs:
        msg = "'func' must be one of {}.".format(
            ", ".join(
                sorted((e and e.__name__) or "None" for e in set(valid_funcs))
            )
        )
        raise ValueError(msg)

    if isinstance(regex, Pattern):
        if flags:
            msg = "'flags' can only be used with a string pattern; pass flags to re.compile() instead"
            raise TypeError(msg)
        pattern = regex
    else:
        pattern = re.compile(regex, flags)

    if func is re.match:
        match_func = None
    elif func is re.search:
        match_func = pattern.search
    else:
        match_func = pattern.fullmatch

    return _MatchesReValidator(pattern, match_func)


def x_matches_re__mutmut_30(regex, flags=0, func=None):
    r"""
    A validator that raises `ValueError` if the initializer is called with a
    string that doesn't match *regex*.

    Args:
        regex (str, re.Pattern):
            A regex string or precompiled pattern to match against

        flags (int):
            Flags that will be passed to the underlying re function (default 0)

        func (typing.Callable):
            Which underlying `re` function to call. Valid options are
            `re.fullmatch`, `re.search`, and `re.match`; the default `None`
            means `re.fullmatch`. For performance reasons, the pattern is
            always precompiled using `re.compile`.

    .. versionadded:: 19.2.0
    .. versionchanged:: 21.3.0 *regex* can be a pre-compiled pattern.
    """
    valid_funcs = (re.fullmatch, None, re.search, re.match)
    if func not in valid_funcs:
        msg = "'func' must be one of {}.".format(
            ", ".join(
                sorted((e and e.__name__) or "None" for e in set(valid_funcs))
            )
        )
        raise ValueError(msg)

    if isinstance(regex, Pattern):
        if flags:
            msg = "'flags' can only be used with a string pattern; pass flags to re.compile() instead"
            raise TypeError(msg)
        pattern = regex
    else:
        pattern = re.compile(regex, flags)

    if func is re.match:
        match_func = pattern.match
    elif func is not re.search:
        match_func = pattern.search
    else:
        match_func = pattern.fullmatch

    return _MatchesReValidator(pattern, match_func)


def x_matches_re__mutmut_31(regex, flags=0, func=None):
    r"""
    A validator that raises `ValueError` if the initializer is called with a
    string that doesn't match *regex*.

    Args:
        regex (str, re.Pattern):
            A regex string or precompiled pattern to match against

        flags (int):
            Flags that will be passed to the underlying re function (default 0)

        func (typing.Callable):
            Which underlying `re` function to call. Valid options are
            `re.fullmatch`, `re.search`, and `re.match`; the default `None`
            means `re.fullmatch`. For performance reasons, the pattern is
            always precompiled using `re.compile`.

    .. versionadded:: 19.2.0
    .. versionchanged:: 21.3.0 *regex* can be a pre-compiled pattern.
    """
    valid_funcs = (re.fullmatch, None, re.search, re.match)
    if func not in valid_funcs:
        msg = "'func' must be one of {}.".format(
            ", ".join(
                sorted((e and e.__name__) or "None" for e in set(valid_funcs))
            )
        )
        raise ValueError(msg)

    if isinstance(regex, Pattern):
        if flags:
            msg = "'flags' can only be used with a string pattern; pass flags to re.compile() instead"
            raise TypeError(msg)
        pattern = regex
    else:
        pattern = re.compile(regex, flags)

    if func is re.match:
        match_func = pattern.match
    elif func is re.search:
        match_func = None
    else:
        match_func = pattern.fullmatch

    return _MatchesReValidator(pattern, match_func)


def x_matches_re__mutmut_32(regex, flags=0, func=None):
    r"""
    A validator that raises `ValueError` if the initializer is called with a
    string that doesn't match *regex*.

    Args:
        regex (str, re.Pattern):
            A regex string or precompiled pattern to match against

        flags (int):
            Flags that will be passed to the underlying re function (default 0)

        func (typing.Callable):
            Which underlying `re` function to call. Valid options are
            `re.fullmatch`, `re.search`, and `re.match`; the default `None`
            means `re.fullmatch`. For performance reasons, the pattern is
            always precompiled using `re.compile`.

    .. versionadded:: 19.2.0
    .. versionchanged:: 21.3.0 *regex* can be a pre-compiled pattern.
    """
    valid_funcs = (re.fullmatch, None, re.search, re.match)
    if func not in valid_funcs:
        msg = "'func' must be one of {}.".format(
            ", ".join(
                sorted((e and e.__name__) or "None" for e in set(valid_funcs))
            )
        )
        raise ValueError(msg)

    if isinstance(regex, Pattern):
        if flags:
            msg = "'flags' can only be used with a string pattern; pass flags to re.compile() instead"
            raise TypeError(msg)
        pattern = regex
    else:
        pattern = re.compile(regex, flags)

    if func is re.match:
        match_func = pattern.match
    elif func is re.search:
        match_func = pattern.search
    else:
        match_func = None

    return _MatchesReValidator(pattern, match_func)


def x_matches_re__mutmut_33(regex, flags=0, func=None):
    r"""
    A validator that raises `ValueError` if the initializer is called with a
    string that doesn't match *regex*.

    Args:
        regex (str, re.Pattern):
            A regex string or precompiled pattern to match against

        flags (int):
            Flags that will be passed to the underlying re function (default 0)

        func (typing.Callable):
            Which underlying `re` function to call. Valid options are
            `re.fullmatch`, `re.search`, and `re.match`; the default `None`
            means `re.fullmatch`. For performance reasons, the pattern is
            always precompiled using `re.compile`.

    .. versionadded:: 19.2.0
    .. versionchanged:: 21.3.0 *regex* can be a pre-compiled pattern.
    """
    valid_funcs = (re.fullmatch, None, re.search, re.match)
    if func not in valid_funcs:
        msg = "'func' must be one of {}.".format(
            ", ".join(
                sorted((e and e.__name__) or "None" for e in set(valid_funcs))
            )
        )
        raise ValueError(msg)

    if isinstance(regex, Pattern):
        if flags:
            msg = "'flags' can only be used with a string pattern; pass flags to re.compile() instead"
            raise TypeError(msg)
        pattern = regex
    else:
        pattern = re.compile(regex, flags)

    if func is re.match:
        match_func = pattern.match
    elif func is re.search:
        match_func = pattern.search
    else:
        match_func = pattern.fullmatch

    return _MatchesReValidator(None, match_func)


def x_matches_re__mutmut_34(regex, flags=0, func=None):
    r"""
    A validator that raises `ValueError` if the initializer is called with a
    string that doesn't match *regex*.

    Args:
        regex (str, re.Pattern):
            A regex string or precompiled pattern to match against

        flags (int):
            Flags that will be passed to the underlying re function (default 0)

        func (typing.Callable):
            Which underlying `re` function to call. Valid options are
            `re.fullmatch`, `re.search`, and `re.match`; the default `None`
            means `re.fullmatch`. For performance reasons, the pattern is
            always precompiled using `re.compile`.

    .. versionadded:: 19.2.0
    .. versionchanged:: 21.3.0 *regex* can be a pre-compiled pattern.
    """
    valid_funcs = (re.fullmatch, None, re.search, re.match)
    if func not in valid_funcs:
        msg = "'func' must be one of {}.".format(
            ", ".join(
                sorted((e and e.__name__) or "None" for e in set(valid_funcs))
            )
        )
        raise ValueError(msg)

    if isinstance(regex, Pattern):
        if flags:
            msg = "'flags' can only be used with a string pattern; pass flags to re.compile() instead"
            raise TypeError(msg)
        pattern = regex
    else:
        pattern = re.compile(regex, flags)

    if func is re.match:
        match_func = pattern.match
    elif func is re.search:
        match_func = pattern.search
    else:
        match_func = pattern.fullmatch

    return _MatchesReValidator(pattern, None)


def x_matches_re__mutmut_35(regex, flags=0, func=None):
    r"""
    A validator that raises `ValueError` if the initializer is called with a
    string that doesn't match *regex*.

    Args:
        regex (str, re.Pattern):
            A regex string or precompiled pattern to match against

        flags (int):
            Flags that will be passed to the underlying re function (default 0)

        func (typing.Callable):
            Which underlying `re` function to call. Valid options are
            `re.fullmatch`, `re.search`, and `re.match`; the default `None`
            means `re.fullmatch`. For performance reasons, the pattern is
            always precompiled using `re.compile`.

    .. versionadded:: 19.2.0
    .. versionchanged:: 21.3.0 *regex* can be a pre-compiled pattern.
    """
    valid_funcs = (re.fullmatch, None, re.search, re.match)
    if func not in valid_funcs:
        msg = "'func' must be one of {}.".format(
            ", ".join(
                sorted((e and e.__name__) or "None" for e in set(valid_funcs))
            )
        )
        raise ValueError(msg)

    if isinstance(regex, Pattern):
        if flags:
            msg = "'flags' can only be used with a string pattern; pass flags to re.compile() instead"
            raise TypeError(msg)
        pattern = regex
    else:
        pattern = re.compile(regex, flags)

    if func is re.match:
        match_func = pattern.match
    elif func is re.search:
        match_func = pattern.search
    else:
        match_func = pattern.fullmatch

    return _MatchesReValidator(match_func)


def x_matches_re__mutmut_36(regex, flags=0, func=None):
    r"""
    A validator that raises `ValueError` if the initializer is called with a
    string that doesn't match *regex*.

    Args:
        regex (str, re.Pattern):
            A regex string or precompiled pattern to match against

        flags (int):
            Flags that will be passed to the underlying re function (default 0)

        func (typing.Callable):
            Which underlying `re` function to call. Valid options are
            `re.fullmatch`, `re.search`, and `re.match`; the default `None`
            means `re.fullmatch`. For performance reasons, the pattern is
            always precompiled using `re.compile`.

    .. versionadded:: 19.2.0
    .. versionchanged:: 21.3.0 *regex* can be a pre-compiled pattern.
    """
    valid_funcs = (re.fullmatch, None, re.search, re.match)
    if func not in valid_funcs:
        msg = "'func' must be one of {}.".format(
            ", ".join(
                sorted((e and e.__name__) or "None" for e in set(valid_funcs))
            )
        )
        raise ValueError(msg)

    if isinstance(regex, Pattern):
        if flags:
            msg = "'flags' can only be used with a string pattern; pass flags to re.compile() instead"
            raise TypeError(msg)
        pattern = regex
    else:
        pattern = re.compile(regex, flags)

    if func is re.match:
        match_func = pattern.match
    elif func is re.search:
        match_func = pattern.search
    else:
        match_func = pattern.fullmatch

    return _MatchesReValidator(pattern, )

x_matches_re__mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
'x_matches_re__mutmut_1': x_matches_re__mutmut_1, 
    'x_matches_re__mutmut_2': x_matches_re__mutmut_2, 
    'x_matches_re__mutmut_3': x_matches_re__mutmut_3, 
    'x_matches_re__mutmut_4': x_matches_re__mutmut_4, 
    'x_matches_re__mutmut_5': x_matches_re__mutmut_5, 
    'x_matches_re__mutmut_6': x_matches_re__mutmut_6, 
    'x_matches_re__mutmut_7': x_matches_re__mutmut_7, 
    'x_matches_re__mutmut_8': x_matches_re__mutmut_8, 
    'x_matches_re__mutmut_9': x_matches_re__mutmut_9, 
    'x_matches_re__mutmut_10': x_matches_re__mutmut_10, 
    'x_matches_re__mutmut_11': x_matches_re__mutmut_11, 
    'x_matches_re__mutmut_12': x_matches_re__mutmut_12, 
    'x_matches_re__mutmut_13': x_matches_re__mutmut_13, 
    'x_matches_re__mutmut_14': x_matches_re__mutmut_14, 
    'x_matches_re__mutmut_15': x_matches_re__mutmut_15, 
    'x_matches_re__mutmut_16': x_matches_re__mutmut_16, 
    'x_matches_re__mutmut_17': x_matches_re__mutmut_17, 
    'x_matches_re__mutmut_18': x_matches_re__mutmut_18, 
    'x_matches_re__mutmut_19': x_matches_re__mutmut_19, 
    'x_matches_re__mutmut_20': x_matches_re__mutmut_20, 
    'x_matches_re__mutmut_21': x_matches_re__mutmut_21, 
    'x_matches_re__mutmut_22': x_matches_re__mutmut_22, 
    'x_matches_re__mutmut_23': x_matches_re__mutmut_23, 
    'x_matches_re__mutmut_24': x_matches_re__mutmut_24, 
    'x_matches_re__mutmut_25': x_matches_re__mutmut_25, 
    'x_matches_re__mutmut_26': x_matches_re__mutmut_26, 
    'x_matches_re__mutmut_27': x_matches_re__mutmut_27, 
    'x_matches_re__mutmut_28': x_matches_re__mutmut_28, 
    'x_matches_re__mutmut_29': x_matches_re__mutmut_29, 
    'x_matches_re__mutmut_30': x_matches_re__mutmut_30, 
    'x_matches_re__mutmut_31': x_matches_re__mutmut_31, 
    'x_matches_re__mutmut_32': x_matches_re__mutmut_32, 
    'x_matches_re__mutmut_33': x_matches_re__mutmut_33, 
    'x_matches_re__mutmut_34': x_matches_re__mutmut_34, 
    'x_matches_re__mutmut_35': x_matches_re__mutmut_35, 
    'x_matches_re__mutmut_36': x_matches_re__mutmut_36
}
x_matches_re__mutmut_orig.__name__ = 'x_matches_re'


@attrs(repr=False, slots=True, unsafe_hash=True)
class _OptionalValidator:
    validator = attrib()

    def __call__(self, inst, attr, value):
        if value is None:
            return

        self.validator(inst, attr, value)

    def __repr__(self):
        return f"<optional validator for {self.validator!r} or None>"


def optional(validator):
    args = [validator]# type: ignore
    kwargs = {}# type: ignore
    return _mutmut_trampoline(x_optional__mutmut_orig, x_optional__mutmut_mutants, args, kwargs, None)


def x_optional__mutmut_orig(validator):
    """
    A validator that makes an attribute optional.  An optional attribute is one
    which can be set to `None` in addition to satisfying the requirements of
    the sub-validator.

    Args:
        validator
            (typing.Callable | tuple[typing.Callable] | list[typing.Callable]):
            A validator (or validators) that is used for non-`None` values.

    .. versionadded:: 15.1.0
    .. versionchanged:: 17.1.0 *validator* can be a list of validators.
    .. versionchanged:: 23.1.0 *validator* can also be a tuple of validators.
    """
    if isinstance(validator, (list, tuple)):
        return _OptionalValidator(_AndValidator(validator))

    return _OptionalValidator(validator)


def x_optional__mutmut_1(validator):
    """
    A validator that makes an attribute optional.  An optional attribute is one
    which can be set to `None` in addition to satisfying the requirements of
    the sub-validator.

    Args:
        validator
            (typing.Callable | tuple[typing.Callable] | list[typing.Callable]):
            A validator (or validators) that is used for non-`None` values.

    .. versionadded:: 15.1.0
    .. versionchanged:: 17.1.0 *validator* can be a list of validators.
    .. versionchanged:: 23.1.0 *validator* can also be a tuple of validators.
    """
    if isinstance(validator, (list, tuple)):
        return _OptionalValidator(None)

    return _OptionalValidator(validator)


def x_optional__mutmut_2(validator):
    """
    A validator that makes an attribute optional.  An optional attribute is one
    which can be set to `None` in addition to satisfying the requirements of
    the sub-validator.

    Args:
        validator
            (typing.Callable | tuple[typing.Callable] | list[typing.Callable]):
            A validator (or validators) that is used for non-`None` values.

    .. versionadded:: 15.1.0
    .. versionchanged:: 17.1.0 *validator* can be a list of validators.
    .. versionchanged:: 23.1.0 *validator* can also be a tuple of validators.
    """
    if isinstance(validator, (list, tuple)):
        return _OptionalValidator(_AndValidator(None))

    return _OptionalValidator(validator)


def x_optional__mutmut_3(validator):
    """
    A validator that makes an attribute optional.  An optional attribute is one
    which can be set to `None` in addition to satisfying the requirements of
    the sub-validator.

    Args:
        validator
            (typing.Callable | tuple[typing.Callable] | list[typing.Callable]):
            A validator (or validators) that is used for non-`None` values.

    .. versionadded:: 15.1.0
    .. versionchanged:: 17.1.0 *validator* can be a list of validators.
    .. versionchanged:: 23.1.0 *validator* can also be a tuple of validators.
    """
    if isinstance(validator, (list, tuple)):
        return _OptionalValidator(_AndValidator(validator))

    return _OptionalValidator(None)

x_optional__mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
'x_optional__mutmut_1': x_optional__mutmut_1, 
    'x_optional__mutmut_2': x_optional__mutmut_2, 
    'x_optional__mutmut_3': x_optional__mutmut_3
}
x_optional__mutmut_orig.__name__ = 'x_optional'


@attrs(repr=False, slots=True, unsafe_hash=True)
class _InValidator:
    options = attrib()
    _original_options = attrib(hash=False)

    def __call__(self, inst, attr, value):
        try:
            in_options = value in self.options
        except TypeError:  # e.g. `1 in "abc"`
            in_options = False

        if not in_options:
            msg = f"'{attr.name}' must be in {self._original_options!r} (got {value!r})"
            raise ValueError(
                msg,
                attr,
                self._original_options,
                value,
            )

    def __repr__(self):
        return f"<in_ validator with options {self._original_options!r}>"


def in_(options):
    args = [options]# type: ignore
    kwargs = {}# type: ignore
    return _mutmut_trampoline(x_in___mutmut_orig, x_in___mutmut_mutants, args, kwargs, None)


def x_in___mutmut_orig(options):
    """
    A validator that raises a `ValueError` if the initializer is called with a
    value that does not belong in the *options* provided.

    The check is performed using ``value in options``, so *options* has to
    support that operation.

    To keep the validator hashable, dicts, lists, and sets are transparently
    transformed into a `tuple`.

    Args:
        options: Allowed options.

    Raises:
        ValueError:
            With a human readable error message, the attribute (of type
            `attrs.Attribute`), the expected options, and the value it got.

    .. versionadded:: 17.1.0
    .. versionchanged:: 22.1.0
       The ValueError was incomplete until now and only contained the human
       readable error message. Now it contains all the information that has
       been promised since 17.1.0.
    .. versionchanged:: 24.1.0
       *options* that are a list, dict, or a set are now transformed into a
       tuple to keep the validator hashable.
    """
    repr_options = options
    if isinstance(options, (list, dict, set)):
        options = tuple(options)

    return _InValidator(options, repr_options)


def x_in___mutmut_1(options):
    """
    A validator that raises a `ValueError` if the initializer is called with a
    value that does not belong in the *options* provided.

    The check is performed using ``value in options``, so *options* has to
    support that operation.

    To keep the validator hashable, dicts, lists, and sets are transparently
    transformed into a `tuple`.

    Args:
        options: Allowed options.

    Raises:
        ValueError:
            With a human readable error message, the attribute (of type
            `attrs.Attribute`), the expected options, and the value it got.

    .. versionadded:: 17.1.0
    .. versionchanged:: 22.1.0
       The ValueError was incomplete until now and only contained the human
       readable error message. Now it contains all the information that has
       been promised since 17.1.0.
    .. versionchanged:: 24.1.0
       *options* that are a list, dict, or a set are now transformed into a
       tuple to keep the validator hashable.
    """
    repr_options = None
    if isinstance(options, (list, dict, set)):
        options = tuple(options)

    return _InValidator(options, repr_options)


def x_in___mutmut_2(options):
    """
    A validator that raises a `ValueError` if the initializer is called with a
    value that does not belong in the *options* provided.

    The check is performed using ``value in options``, so *options* has to
    support that operation.

    To keep the validator hashable, dicts, lists, and sets are transparently
    transformed into a `tuple`.

    Args:
        options: Allowed options.

    Raises:
        ValueError:
            With a human readable error message, the attribute (of type
            `attrs.Attribute`), the expected options, and the value it got.

    .. versionadded:: 17.1.0
    .. versionchanged:: 22.1.0
       The ValueError was incomplete until now and only contained the human
       readable error message. Now it contains all the information that has
       been promised since 17.1.0.
    .. versionchanged:: 24.1.0
       *options* that are a list, dict, or a set are now transformed into a
       tuple to keep the validator hashable.
    """
    repr_options = options
    if isinstance(options, (list, dict, set)):
        options = None

    return _InValidator(options, repr_options)


def x_in___mutmut_3(options):
    """
    A validator that raises a `ValueError` if the initializer is called with a
    value that does not belong in the *options* provided.

    The check is performed using ``value in options``, so *options* has to
    support that operation.

    To keep the validator hashable, dicts, lists, and sets are transparently
    transformed into a `tuple`.

    Args:
        options: Allowed options.

    Raises:
        ValueError:
            With a human readable error message, the attribute (of type
            `attrs.Attribute`), the expected options, and the value it got.

    .. versionadded:: 17.1.0
    .. versionchanged:: 22.1.0
       The ValueError was incomplete until now and only contained the human
       readable error message. Now it contains all the information that has
       been promised since 17.1.0.
    .. versionchanged:: 24.1.0
       *options* that are a list, dict, or a set are now transformed into a
       tuple to keep the validator hashable.
    """
    repr_options = options
    if isinstance(options, (list, dict, set)):
        options = tuple(None)

    return _InValidator(options, repr_options)


def x_in___mutmut_4(options):
    """
    A validator that raises a `ValueError` if the initializer is called with a
    value that does not belong in the *options* provided.

    The check is performed using ``value in options``, so *options* has to
    support that operation.

    To keep the validator hashable, dicts, lists, and sets are transparently
    transformed into a `tuple`.

    Args:
        options: Allowed options.

    Raises:
        ValueError:
            With a human readable error message, the attribute (of type
            `attrs.Attribute`), the expected options, and the value it got.

    .. versionadded:: 17.1.0
    .. versionchanged:: 22.1.0
       The ValueError was incomplete until now and only contained the human
       readable error message. Now it contains all the information that has
       been promised since 17.1.0.
    .. versionchanged:: 24.1.0
       *options* that are a list, dict, or a set are now transformed into a
       tuple to keep the validator hashable.
    """
    repr_options = options
    if isinstance(options, (list, dict, set)):
        options = tuple(options)

    return _InValidator(None, repr_options)


def x_in___mutmut_5(options):
    """
    A validator that raises a `ValueError` if the initializer is called with a
    value that does not belong in the *options* provided.

    The check is performed using ``value in options``, so *options* has to
    support that operation.

    To keep the validator hashable, dicts, lists, and sets are transparently
    transformed into a `tuple`.

    Args:
        options: Allowed options.

    Raises:
        ValueError:
            With a human readable error message, the attribute (of type
            `attrs.Attribute`), the expected options, and the value it got.

    .. versionadded:: 17.1.0
    .. versionchanged:: 22.1.0
       The ValueError was incomplete until now and only contained the human
       readable error message. Now it contains all the information that has
       been promised since 17.1.0.
    .. versionchanged:: 24.1.0
       *options* that are a list, dict, or a set are now transformed into a
       tuple to keep the validator hashable.
    """
    repr_options = options
    if isinstance(options, (list, dict, set)):
        options = tuple(options)

    return _InValidator(options, None)


def x_in___mutmut_6(options):
    """
    A validator that raises a `ValueError` if the initializer is called with a
    value that does not belong in the *options* provided.

    The check is performed using ``value in options``, so *options* has to
    support that operation.

    To keep the validator hashable, dicts, lists, and sets are transparently
    transformed into a `tuple`.

    Args:
        options: Allowed options.

    Raises:
        ValueError:
            With a human readable error message, the attribute (of type
            `attrs.Attribute`), the expected options, and the value it got.

    .. versionadded:: 17.1.0
    .. versionchanged:: 22.1.0
       The ValueError was incomplete until now and only contained the human
       readable error message. Now it contains all the information that has
       been promised since 17.1.0.
    .. versionchanged:: 24.1.0
       *options* that are a list, dict, or a set are now transformed into a
       tuple to keep the validator hashable.
    """
    repr_options = options
    if isinstance(options, (list, dict, set)):
        options = tuple(options)

    return _InValidator(repr_options)


def x_in___mutmut_7(options):
    """
    A validator that raises a `ValueError` if the initializer is called with a
    value that does not belong in the *options* provided.

    The check is performed using ``value in options``, so *options* has to
    support that operation.

    To keep the validator hashable, dicts, lists, and sets are transparently
    transformed into a `tuple`.

    Args:
        options: Allowed options.

    Raises:
        ValueError:
            With a human readable error message, the attribute (of type
            `attrs.Attribute`), the expected options, and the value it got.

    .. versionadded:: 17.1.0
    .. versionchanged:: 22.1.0
       The ValueError was incomplete until now and only contained the human
       readable error message. Now it contains all the information that has
       been promised since 17.1.0.
    .. versionchanged:: 24.1.0
       *options* that are a list, dict, or a set are now transformed into a
       tuple to keep the validator hashable.
    """
    repr_options = options
    if isinstance(options, (list, dict, set)):
        options = tuple(options)

    return _InValidator(options, )

x_in___mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
'x_in___mutmut_1': x_in___mutmut_1, 
    'x_in___mutmut_2': x_in___mutmut_2, 
    'x_in___mutmut_3': x_in___mutmut_3, 
    'x_in___mutmut_4': x_in___mutmut_4, 
    'x_in___mutmut_5': x_in___mutmut_5, 
    'x_in___mutmut_6': x_in___mutmut_6, 
    'x_in___mutmut_7': x_in___mutmut_7
}
x_in___mutmut_orig.__name__ = 'x_in_'


@attrs(repr=False, slots=False, unsafe_hash=True)
class _IsCallableValidator:
    def __call__(self, inst, attr, value):
        """
        We use a callable class to be able to change the ``__repr__``.
        """
        if not callable(value):
            message = (
                "'{name}' must be callable "
                "(got {value!r} that is a {actual!r})."
            )
            raise NotCallableError(
                msg=message.format(
                    name=attr.name, value=value, actual=value.__class__
                ),
                value=value,
            )

    def __repr__(self):
        return "<is_callable validator>"


def is_callable():
    """
    A validator that raises a `attrs.exceptions.NotCallableError` if the
    initializer is called with a value for this particular attribute that is
    not callable.

    .. versionadded:: 19.1.0

    Raises:
        attrs.exceptions.NotCallableError:
            With a human readable error message containing the attribute
            (`attrs.Attribute`) name, and the value it got.
    """
    return _IsCallableValidator()


@attrs(repr=False, slots=True, unsafe_hash=True)
class _DeepIterable:
    member_validator = attrib(validator=is_callable())
    iterable_validator = attrib(
        default=None, validator=optional(is_callable())
    )

    def __call__(self, inst, attr, value):
        """
        We use a callable class to be able to change the ``__repr__``.
        """
        if self.iterable_validator is not None:
            self.iterable_validator(inst, attr, value)

        for member in value:
            self.member_validator(inst, attr, member)

    def __repr__(self):
        iterable_identifier = (
            ""
            if self.iterable_validator is None
            else f" {self.iterable_validator!r}"
        )
        return (
            f"<deep_iterable validator for{iterable_identifier}"
            f" iterables of {self.member_validator!r}>"
        )


def deep_iterable(member_validator, iterable_validator=None):
    args = [member_validator, iterable_validator]# type: ignore
    kwargs = {}# type: ignore
    return _mutmut_trampoline(x_deep_iterable__mutmut_orig, x_deep_iterable__mutmut_mutants, args, kwargs, None)


def x_deep_iterable__mutmut_orig(member_validator, iterable_validator=None):
    """
    A validator that performs deep validation of an iterable.

    Args:
        member_validator: Validator(s) to apply to iterable members.

        iterable_validator:
            Validator(s) to apply to iterable itself (optional).

    Raises
        TypeError: if any sub-validators fail

    .. versionadded:: 19.1.0

    .. versionchanged:: 25.4.0
       *member_validator* and *iterable_validator* can now be a list or tuple
       of validators.
    """
    if isinstance(member_validator, (list, tuple)):
        member_validator = and_(*member_validator)
    if isinstance(iterable_validator, (list, tuple)):
        iterable_validator = and_(*iterable_validator)
    return _DeepIterable(member_validator, iterable_validator)


def x_deep_iterable__mutmut_1(member_validator, iterable_validator=None):
    """
    A validator that performs deep validation of an iterable.

    Args:
        member_validator: Validator(s) to apply to iterable members.

        iterable_validator:
            Validator(s) to apply to iterable itself (optional).

    Raises
        TypeError: if any sub-validators fail

    .. versionadded:: 19.1.0

    .. versionchanged:: 25.4.0
       *member_validator* and *iterable_validator* can now be a list or tuple
       of validators.
    """
    if isinstance(member_validator, (list, tuple)):
        member_validator = None
    if isinstance(iterable_validator, (list, tuple)):
        iterable_validator = and_(*iterable_validator)
    return _DeepIterable(member_validator, iterable_validator)


def x_deep_iterable__mutmut_2(member_validator, iterable_validator=None):
    """
    A validator that performs deep validation of an iterable.

    Args:
        member_validator: Validator(s) to apply to iterable members.

        iterable_validator:
            Validator(s) to apply to iterable itself (optional).

    Raises
        TypeError: if any sub-validators fail

    .. versionadded:: 19.1.0

    .. versionchanged:: 25.4.0
       *member_validator* and *iterable_validator* can now be a list or tuple
       of validators.
    """
    if isinstance(member_validator, (list, tuple)):
        member_validator = and_(*member_validator)
    if isinstance(iterable_validator, (list, tuple)):
        iterable_validator = None
    return _DeepIterable(member_validator, iterable_validator)


def x_deep_iterable__mutmut_3(member_validator, iterable_validator=None):
    """
    A validator that performs deep validation of an iterable.

    Args:
        member_validator: Validator(s) to apply to iterable members.

        iterable_validator:
            Validator(s) to apply to iterable itself (optional).

    Raises
        TypeError: if any sub-validators fail

    .. versionadded:: 19.1.0

    .. versionchanged:: 25.4.0
       *member_validator* and *iterable_validator* can now be a list or tuple
       of validators.
    """
    if isinstance(member_validator, (list, tuple)):
        member_validator = and_(*member_validator)
    if isinstance(iterable_validator, (list, tuple)):
        iterable_validator = and_(*iterable_validator)
    return _DeepIterable(None, iterable_validator)


def x_deep_iterable__mutmut_4(member_validator, iterable_validator=None):
    """
    A validator that performs deep validation of an iterable.

    Args:
        member_validator: Validator(s) to apply to iterable members.

        iterable_validator:
            Validator(s) to apply to iterable itself (optional).

    Raises
        TypeError: if any sub-validators fail

    .. versionadded:: 19.1.0

    .. versionchanged:: 25.4.0
       *member_validator* and *iterable_validator* can now be a list or tuple
       of validators.
    """
    if isinstance(member_validator, (list, tuple)):
        member_validator = and_(*member_validator)
    if isinstance(iterable_validator, (list, tuple)):
        iterable_validator = and_(*iterable_validator)
    return _DeepIterable(member_validator, None)


def x_deep_iterable__mutmut_5(member_validator, iterable_validator=None):
    """
    A validator that performs deep validation of an iterable.

    Args:
        member_validator: Validator(s) to apply to iterable members.

        iterable_validator:
            Validator(s) to apply to iterable itself (optional).

    Raises
        TypeError: if any sub-validators fail

    .. versionadded:: 19.1.0

    .. versionchanged:: 25.4.0
       *member_validator* and *iterable_validator* can now be a list or tuple
       of validators.
    """
    if isinstance(member_validator, (list, tuple)):
        member_validator = and_(*member_validator)
    if isinstance(iterable_validator, (list, tuple)):
        iterable_validator = and_(*iterable_validator)
    return _DeepIterable(iterable_validator)


def x_deep_iterable__mutmut_6(member_validator, iterable_validator=None):
    """
    A validator that performs deep validation of an iterable.

    Args:
        member_validator: Validator(s) to apply to iterable members.

        iterable_validator:
            Validator(s) to apply to iterable itself (optional).

    Raises
        TypeError: if any sub-validators fail

    .. versionadded:: 19.1.0

    .. versionchanged:: 25.4.0
       *member_validator* and *iterable_validator* can now be a list or tuple
       of validators.
    """
    if isinstance(member_validator, (list, tuple)):
        member_validator = and_(*member_validator)
    if isinstance(iterable_validator, (list, tuple)):
        iterable_validator = and_(*iterable_validator)
    return _DeepIterable(member_validator, )

x_deep_iterable__mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
'x_deep_iterable__mutmut_1': x_deep_iterable__mutmut_1, 
    'x_deep_iterable__mutmut_2': x_deep_iterable__mutmut_2, 
    'x_deep_iterable__mutmut_3': x_deep_iterable__mutmut_3, 
    'x_deep_iterable__mutmut_4': x_deep_iterable__mutmut_4, 
    'x_deep_iterable__mutmut_5': x_deep_iterable__mutmut_5, 
    'x_deep_iterable__mutmut_6': x_deep_iterable__mutmut_6
}
x_deep_iterable__mutmut_orig.__name__ = 'x_deep_iterable'


@attrs(repr=False, slots=True, unsafe_hash=True)
class _DeepMapping:
    key_validator = attrib(validator=optional(is_callable()))
    value_validator = attrib(validator=optional(is_callable()))
    mapping_validator = attrib(validator=optional(is_callable()))

    def __call__(self, inst, attr, value):
        """
        We use a callable class to be able to change the ``__repr__``.
        """
        if self.mapping_validator is not None:
            self.mapping_validator(inst, attr, value)

        for key in value:
            if self.key_validator is not None:
                self.key_validator(inst, attr, key)
            if self.value_validator is not None:
                self.value_validator(inst, attr, value[key])

    def __repr__(self):
        return f"<deep_mapping validator for objects mapping {self.key_validator!r} to {self.value_validator!r}>"


def deep_mapping(
    key_validator=None, value_validator=None, mapping_validator=None
):
    args = [key_validator, value_validator, mapping_validator]# type: ignore
    kwargs = {}# type: ignore
    return _mutmut_trampoline(x_deep_mapping__mutmut_orig, x_deep_mapping__mutmut_mutants, args, kwargs, None)


def x_deep_mapping__mutmut_orig(
    key_validator=None, value_validator=None, mapping_validator=None
):
    """
    A validator that performs deep validation of a dictionary.

    All validators are optional, but at least one of *key_validator* or
    *value_validator* must be provided.

    Args:
        key_validator: Validator(s) to apply to dictionary keys.

        value_validator: Validator(s) to apply to dictionary values.

        mapping_validator:
            Validator(s) to apply to top-level mapping attribute.

    .. versionadded:: 19.1.0

    .. versionchanged:: 25.4.0
       *key_validator* and *value_validator* are now optional, but at least one
       of them must be provided.

    .. versionchanged:: 25.4.0
       *key_validator*, *value_validator*, and *mapping_validator* can now be a
       list or tuple of validators.

    Raises:
        TypeError: If any sub-validator fails on validation.

        ValueError:
            If neither *key_validator* nor *value_validator* is provided on
            instantiation.
    """
    if key_validator is None and value_validator is None:
        msg = (
            "At least one of key_validator or value_validator must be provided"
        )
        raise ValueError(msg)

    if isinstance(key_validator, (list, tuple)):
        key_validator = and_(*key_validator)
    if isinstance(value_validator, (list, tuple)):
        value_validator = and_(*value_validator)
    if isinstance(mapping_validator, (list, tuple)):
        mapping_validator = and_(*mapping_validator)

    return _DeepMapping(key_validator, value_validator, mapping_validator)


def x_deep_mapping__mutmut_1(
    key_validator=None, value_validator=None, mapping_validator=None
):
    """
    A validator that performs deep validation of a dictionary.

    All validators are optional, but at least one of *key_validator* or
    *value_validator* must be provided.

    Args:
        key_validator: Validator(s) to apply to dictionary keys.

        value_validator: Validator(s) to apply to dictionary values.

        mapping_validator:
            Validator(s) to apply to top-level mapping attribute.

    .. versionadded:: 19.1.0

    .. versionchanged:: 25.4.0
       *key_validator* and *value_validator* are now optional, but at least one
       of them must be provided.

    .. versionchanged:: 25.4.0
       *key_validator*, *value_validator*, and *mapping_validator* can now be a
       list or tuple of validators.

    Raises:
        TypeError: If any sub-validator fails on validation.

        ValueError:
            If neither *key_validator* nor *value_validator* is provided on
            instantiation.
    """
    if key_validator is None or value_validator is None:
        msg = (
            "At least one of key_validator or value_validator must be provided"
        )
        raise ValueError(msg)

    if isinstance(key_validator, (list, tuple)):
        key_validator = and_(*key_validator)
    if isinstance(value_validator, (list, tuple)):
        value_validator = and_(*value_validator)
    if isinstance(mapping_validator, (list, tuple)):
        mapping_validator = and_(*mapping_validator)

    return _DeepMapping(key_validator, value_validator, mapping_validator)


def x_deep_mapping__mutmut_2(
    key_validator=None, value_validator=None, mapping_validator=None
):
    """
    A validator that performs deep validation of a dictionary.

    All validators are optional, but at least one of *key_validator* or
    *value_validator* must be provided.

    Args:
        key_validator: Validator(s) to apply to dictionary keys.

        value_validator: Validator(s) to apply to dictionary values.

        mapping_validator:
            Validator(s) to apply to top-level mapping attribute.

    .. versionadded:: 19.1.0

    .. versionchanged:: 25.4.0
       *key_validator* and *value_validator* are now optional, but at least one
       of them must be provided.

    .. versionchanged:: 25.4.0
       *key_validator*, *value_validator*, and *mapping_validator* can now be a
       list or tuple of validators.

    Raises:
        TypeError: If any sub-validator fails on validation.

        ValueError:
            If neither *key_validator* nor *value_validator* is provided on
            instantiation.
    """
    if key_validator is not None and value_validator is None:
        msg = (
            "At least one of key_validator or value_validator must be provided"
        )
        raise ValueError(msg)

    if isinstance(key_validator, (list, tuple)):
        key_validator = and_(*key_validator)
    if isinstance(value_validator, (list, tuple)):
        value_validator = and_(*value_validator)
    if isinstance(mapping_validator, (list, tuple)):
        mapping_validator = and_(*mapping_validator)

    return _DeepMapping(key_validator, value_validator, mapping_validator)


def x_deep_mapping__mutmut_3(
    key_validator=None, value_validator=None, mapping_validator=None
):
    """
    A validator that performs deep validation of a dictionary.

    All validators are optional, but at least one of *key_validator* or
    *value_validator* must be provided.

    Args:
        key_validator: Validator(s) to apply to dictionary keys.

        value_validator: Validator(s) to apply to dictionary values.

        mapping_validator:
            Validator(s) to apply to top-level mapping attribute.

    .. versionadded:: 19.1.0

    .. versionchanged:: 25.4.0
       *key_validator* and *value_validator* are now optional, but at least one
       of them must be provided.

    .. versionchanged:: 25.4.0
       *key_validator*, *value_validator*, and *mapping_validator* can now be a
       list or tuple of validators.

    Raises:
        TypeError: If any sub-validator fails on validation.

        ValueError:
            If neither *key_validator* nor *value_validator* is provided on
            instantiation.
    """
    if key_validator is None and value_validator is not None:
        msg = (
            "At least one of key_validator or value_validator must be provided"
        )
        raise ValueError(msg)

    if isinstance(key_validator, (list, tuple)):
        key_validator = and_(*key_validator)
    if isinstance(value_validator, (list, tuple)):
        value_validator = and_(*value_validator)
    if isinstance(mapping_validator, (list, tuple)):
        mapping_validator = and_(*mapping_validator)

    return _DeepMapping(key_validator, value_validator, mapping_validator)


def x_deep_mapping__mutmut_4(
    key_validator=None, value_validator=None, mapping_validator=None
):
    """
    A validator that performs deep validation of a dictionary.

    All validators are optional, but at least one of *key_validator* or
    *value_validator* must be provided.

    Args:
        key_validator: Validator(s) to apply to dictionary keys.

        value_validator: Validator(s) to apply to dictionary values.

        mapping_validator:
            Validator(s) to apply to top-level mapping attribute.

    .. versionadded:: 19.1.0

    .. versionchanged:: 25.4.0
       *key_validator* and *value_validator* are now optional, but at least one
       of them must be provided.

    .. versionchanged:: 25.4.0
       *key_validator*, *value_validator*, and *mapping_validator* can now be a
       list or tuple of validators.

    Raises:
        TypeError: If any sub-validator fails on validation.

        ValueError:
            If neither *key_validator* nor *value_validator* is provided on
            instantiation.
    """
    if key_validator is None and value_validator is None:
        msg = None
        raise ValueError(msg)

    if isinstance(key_validator, (list, tuple)):
        key_validator = and_(*key_validator)
    if isinstance(value_validator, (list, tuple)):
        value_validator = and_(*value_validator)
    if isinstance(mapping_validator, (list, tuple)):
        mapping_validator = and_(*mapping_validator)

    return _DeepMapping(key_validator, value_validator, mapping_validator)


def x_deep_mapping__mutmut_5(
    key_validator=None, value_validator=None, mapping_validator=None
):
    """
    A validator that performs deep validation of a dictionary.

    All validators are optional, but at least one of *key_validator* or
    *value_validator* must be provided.

    Args:
        key_validator: Validator(s) to apply to dictionary keys.

        value_validator: Validator(s) to apply to dictionary values.

        mapping_validator:
            Validator(s) to apply to top-level mapping attribute.

    .. versionadded:: 19.1.0

    .. versionchanged:: 25.4.0
       *key_validator* and *value_validator* are now optional, but at least one
       of them must be provided.

    .. versionchanged:: 25.4.0
       *key_validator*, *value_validator*, and *mapping_validator* can now be a
       list or tuple of validators.

    Raises:
        TypeError: If any sub-validator fails on validation.

        ValueError:
            If neither *key_validator* nor *value_validator* is provided on
            instantiation.
    """
    if key_validator is None and value_validator is None:
        msg = (
            "XXAt least one of key_validator or value_validator must be providedXX"
        )
        raise ValueError(msg)

    if isinstance(key_validator, (list, tuple)):
        key_validator = and_(*key_validator)
    if isinstance(value_validator, (list, tuple)):
        value_validator = and_(*value_validator)
    if isinstance(mapping_validator, (list, tuple)):
        mapping_validator = and_(*mapping_validator)

    return _DeepMapping(key_validator, value_validator, mapping_validator)


def x_deep_mapping__mutmut_6(
    key_validator=None, value_validator=None, mapping_validator=None
):
    """
    A validator that performs deep validation of a dictionary.

    All validators are optional, but at least one of *key_validator* or
    *value_validator* must be provided.

    Args:
        key_validator: Validator(s) to apply to dictionary keys.

        value_validator: Validator(s) to apply to dictionary values.

        mapping_validator:
            Validator(s) to apply to top-level mapping attribute.

    .. versionadded:: 19.1.0

    .. versionchanged:: 25.4.0
       *key_validator* and *value_validator* are now optional, but at least one
       of them must be provided.

    .. versionchanged:: 25.4.0
       *key_validator*, *value_validator*, and *mapping_validator* can now be a
       list or tuple of validators.

    Raises:
        TypeError: If any sub-validator fails on validation.

        ValueError:
            If neither *key_validator* nor *value_validator* is provided on
            instantiation.
    """
    if key_validator is None and value_validator is None:
        msg = (
            "at least one of key_validator or value_validator must be provided"
        )
        raise ValueError(msg)

    if isinstance(key_validator, (list, tuple)):
        key_validator = and_(*key_validator)
    if isinstance(value_validator, (list, tuple)):
        value_validator = and_(*value_validator)
    if isinstance(mapping_validator, (list, tuple)):
        mapping_validator = and_(*mapping_validator)

    return _DeepMapping(key_validator, value_validator, mapping_validator)


def x_deep_mapping__mutmut_7(
    key_validator=None, value_validator=None, mapping_validator=None
):
    """
    A validator that performs deep validation of a dictionary.

    All validators are optional, but at least one of *key_validator* or
    *value_validator* must be provided.

    Args:
        key_validator: Validator(s) to apply to dictionary keys.

        value_validator: Validator(s) to apply to dictionary values.

        mapping_validator:
            Validator(s) to apply to top-level mapping attribute.

    .. versionadded:: 19.1.0

    .. versionchanged:: 25.4.0
       *key_validator* and *value_validator* are now optional, but at least one
       of them must be provided.

    .. versionchanged:: 25.4.0
       *key_validator*, *value_validator*, and *mapping_validator* can now be a
       list or tuple of validators.

    Raises:
        TypeError: If any sub-validator fails on validation.

        ValueError:
            If neither *key_validator* nor *value_validator* is provided on
            instantiation.
    """
    if key_validator is None and value_validator is None:
        msg = (
            "AT LEAST ONE OF KEY_VALIDATOR OR VALUE_VALIDATOR MUST BE PROVIDED"
        )
        raise ValueError(msg)

    if isinstance(key_validator, (list, tuple)):
        key_validator = and_(*key_validator)
    if isinstance(value_validator, (list, tuple)):
        value_validator = and_(*value_validator)
    if isinstance(mapping_validator, (list, tuple)):
        mapping_validator = and_(*mapping_validator)

    return _DeepMapping(key_validator, value_validator, mapping_validator)


def x_deep_mapping__mutmut_8(
    key_validator=None, value_validator=None, mapping_validator=None
):
    """
    A validator that performs deep validation of a dictionary.

    All validators are optional, but at least one of *key_validator* or
    *value_validator* must be provided.

    Args:
        key_validator: Validator(s) to apply to dictionary keys.

        value_validator: Validator(s) to apply to dictionary values.

        mapping_validator:
            Validator(s) to apply to top-level mapping attribute.

    .. versionadded:: 19.1.0

    .. versionchanged:: 25.4.0
       *key_validator* and *value_validator* are now optional, but at least one
       of them must be provided.

    .. versionchanged:: 25.4.0
       *key_validator*, *value_validator*, and *mapping_validator* can now be a
       list or tuple of validators.

    Raises:
        TypeError: If any sub-validator fails on validation.

        ValueError:
            If neither *key_validator* nor *value_validator* is provided on
            instantiation.
    """
    if key_validator is None and value_validator is None:
        msg = (
            "At least one of key_validator or value_validator must be provided"
        )
        raise ValueError(None)

    if isinstance(key_validator, (list, tuple)):
        key_validator = and_(*key_validator)
    if isinstance(value_validator, (list, tuple)):
        value_validator = and_(*value_validator)
    if isinstance(mapping_validator, (list, tuple)):
        mapping_validator = and_(*mapping_validator)

    return _DeepMapping(key_validator, value_validator, mapping_validator)


def x_deep_mapping__mutmut_9(
    key_validator=None, value_validator=None, mapping_validator=None
):
    """
    A validator that performs deep validation of a dictionary.

    All validators are optional, but at least one of *key_validator* or
    *value_validator* must be provided.

    Args:
        key_validator: Validator(s) to apply to dictionary keys.

        value_validator: Validator(s) to apply to dictionary values.

        mapping_validator:
            Validator(s) to apply to top-level mapping attribute.

    .. versionadded:: 19.1.0

    .. versionchanged:: 25.4.0
       *key_validator* and *value_validator* are now optional, but at least one
       of them must be provided.

    .. versionchanged:: 25.4.0
       *key_validator*, *value_validator*, and *mapping_validator* can now be a
       list or tuple of validators.

    Raises:
        TypeError: If any sub-validator fails on validation.

        ValueError:
            If neither *key_validator* nor *value_validator* is provided on
            instantiation.
    """
    if key_validator is None and value_validator is None:
        msg = (
            "At least one of key_validator or value_validator must be provided"
        )
        raise ValueError(msg)

    if isinstance(key_validator, (list, tuple)):
        key_validator = None
    if isinstance(value_validator, (list, tuple)):
        value_validator = and_(*value_validator)
    if isinstance(mapping_validator, (list, tuple)):
        mapping_validator = and_(*mapping_validator)

    return _DeepMapping(key_validator, value_validator, mapping_validator)


def x_deep_mapping__mutmut_10(
    key_validator=None, value_validator=None, mapping_validator=None
):
    """
    A validator that performs deep validation of a dictionary.

    All validators are optional, but at least one of *key_validator* or
    *value_validator* must be provided.

    Args:
        key_validator: Validator(s) to apply to dictionary keys.

        value_validator: Validator(s) to apply to dictionary values.

        mapping_validator:
            Validator(s) to apply to top-level mapping attribute.

    .. versionadded:: 19.1.0

    .. versionchanged:: 25.4.0
       *key_validator* and *value_validator* are now optional, but at least one
       of them must be provided.

    .. versionchanged:: 25.4.0
       *key_validator*, *value_validator*, and *mapping_validator* can now be a
       list or tuple of validators.

    Raises:
        TypeError: If any sub-validator fails on validation.

        ValueError:
            If neither *key_validator* nor *value_validator* is provided on
            instantiation.
    """
    if key_validator is None and value_validator is None:
        msg = (
            "At least one of key_validator or value_validator must be provided"
        )
        raise ValueError(msg)

    if isinstance(key_validator, (list, tuple)):
        key_validator = and_(*key_validator)
    if isinstance(value_validator, (list, tuple)):
        value_validator = None
    if isinstance(mapping_validator, (list, tuple)):
        mapping_validator = and_(*mapping_validator)

    return _DeepMapping(key_validator, value_validator, mapping_validator)


def x_deep_mapping__mutmut_11(
    key_validator=None, value_validator=None, mapping_validator=None
):
    """
    A validator that performs deep validation of a dictionary.

    All validators are optional, but at least one of *key_validator* or
    *value_validator* must be provided.

    Args:
        key_validator: Validator(s) to apply to dictionary keys.

        value_validator: Validator(s) to apply to dictionary values.

        mapping_validator:
            Validator(s) to apply to top-level mapping attribute.

    .. versionadded:: 19.1.0

    .. versionchanged:: 25.4.0
       *key_validator* and *value_validator* are now optional, but at least one
       of them must be provided.

    .. versionchanged:: 25.4.0
       *key_validator*, *value_validator*, and *mapping_validator* can now be a
       list or tuple of validators.

    Raises:
        TypeError: If any sub-validator fails on validation.

        ValueError:
            If neither *key_validator* nor *value_validator* is provided on
            instantiation.
    """
    if key_validator is None and value_validator is None:
        msg = (
            "At least one of key_validator or value_validator must be provided"
        )
        raise ValueError(msg)

    if isinstance(key_validator, (list, tuple)):
        key_validator = and_(*key_validator)
    if isinstance(value_validator, (list, tuple)):
        value_validator = and_(*value_validator)
    if isinstance(mapping_validator, (list, tuple)):
        mapping_validator = None

    return _DeepMapping(key_validator, value_validator, mapping_validator)


def x_deep_mapping__mutmut_12(
    key_validator=None, value_validator=None, mapping_validator=None
):
    """
    A validator that performs deep validation of a dictionary.

    All validators are optional, but at least one of *key_validator* or
    *value_validator* must be provided.

    Args:
        key_validator: Validator(s) to apply to dictionary keys.

        value_validator: Validator(s) to apply to dictionary values.

        mapping_validator:
            Validator(s) to apply to top-level mapping attribute.

    .. versionadded:: 19.1.0

    .. versionchanged:: 25.4.0
       *key_validator* and *value_validator* are now optional, but at least one
       of them must be provided.

    .. versionchanged:: 25.4.0
       *key_validator*, *value_validator*, and *mapping_validator* can now be a
       list or tuple of validators.

    Raises:
        TypeError: If any sub-validator fails on validation.

        ValueError:
            If neither *key_validator* nor *value_validator* is provided on
            instantiation.
    """
    if key_validator is None and value_validator is None:
        msg = (
            "At least one of key_validator or value_validator must be provided"
        )
        raise ValueError(msg)

    if isinstance(key_validator, (list, tuple)):
        key_validator = and_(*key_validator)
    if isinstance(value_validator, (list, tuple)):
        value_validator = and_(*value_validator)
    if isinstance(mapping_validator, (list, tuple)):
        mapping_validator = and_(*mapping_validator)

    return _DeepMapping(None, value_validator, mapping_validator)


def x_deep_mapping__mutmut_13(
    key_validator=None, value_validator=None, mapping_validator=None
):
    """
    A validator that performs deep validation of a dictionary.

    All validators are optional, but at least one of *key_validator* or
    *value_validator* must be provided.

    Args:
        key_validator: Validator(s) to apply to dictionary keys.

        value_validator: Validator(s) to apply to dictionary values.

        mapping_validator:
            Validator(s) to apply to top-level mapping attribute.

    .. versionadded:: 19.1.0

    .. versionchanged:: 25.4.0
       *key_validator* and *value_validator* are now optional, but at least one
       of them must be provided.

    .. versionchanged:: 25.4.0
       *key_validator*, *value_validator*, and *mapping_validator* can now be a
       list or tuple of validators.

    Raises:
        TypeError: If any sub-validator fails on validation.

        ValueError:
            If neither *key_validator* nor *value_validator* is provided on
            instantiation.
    """
    if key_validator is None and value_validator is None:
        msg = (
            "At least one of key_validator or value_validator must be provided"
        )
        raise ValueError(msg)

    if isinstance(key_validator, (list, tuple)):
        key_validator = and_(*key_validator)
    if isinstance(value_validator, (list, tuple)):
        value_validator = and_(*value_validator)
    if isinstance(mapping_validator, (list, tuple)):
        mapping_validator = and_(*mapping_validator)

    return _DeepMapping(key_validator, None, mapping_validator)


def x_deep_mapping__mutmut_14(
    key_validator=None, value_validator=None, mapping_validator=None
):
    """
    A validator that performs deep validation of a dictionary.

    All validators are optional, but at least one of *key_validator* or
    *value_validator* must be provided.

    Args:
        key_validator: Validator(s) to apply to dictionary keys.

        value_validator: Validator(s) to apply to dictionary values.

        mapping_validator:
            Validator(s) to apply to top-level mapping attribute.

    .. versionadded:: 19.1.0

    .. versionchanged:: 25.4.0
       *key_validator* and *value_validator* are now optional, but at least one
       of them must be provided.

    .. versionchanged:: 25.4.0
       *key_validator*, *value_validator*, and *mapping_validator* can now be a
       list or tuple of validators.

    Raises:
        TypeError: If any sub-validator fails on validation.

        ValueError:
            If neither *key_validator* nor *value_validator* is provided on
            instantiation.
    """
    if key_validator is None and value_validator is None:
        msg = (
            "At least one of key_validator or value_validator must be provided"
        )
        raise ValueError(msg)

    if isinstance(key_validator, (list, tuple)):
        key_validator = and_(*key_validator)
    if isinstance(value_validator, (list, tuple)):
        value_validator = and_(*value_validator)
    if isinstance(mapping_validator, (list, tuple)):
        mapping_validator = and_(*mapping_validator)

    return _DeepMapping(key_validator, value_validator, None)


def x_deep_mapping__mutmut_15(
    key_validator=None, value_validator=None, mapping_validator=None
):
    """
    A validator that performs deep validation of a dictionary.

    All validators are optional, but at least one of *key_validator* or
    *value_validator* must be provided.

    Args:
        key_validator: Validator(s) to apply to dictionary keys.

        value_validator: Validator(s) to apply to dictionary values.

        mapping_validator:
            Validator(s) to apply to top-level mapping attribute.

    .. versionadded:: 19.1.0

    .. versionchanged:: 25.4.0
       *key_validator* and *value_validator* are now optional, but at least one
       of them must be provided.

    .. versionchanged:: 25.4.0
       *key_validator*, *value_validator*, and *mapping_validator* can now be a
       list or tuple of validators.

    Raises:
        TypeError: If any sub-validator fails on validation.

        ValueError:
            If neither *key_validator* nor *value_validator* is provided on
            instantiation.
    """
    if key_validator is None and value_validator is None:
        msg = (
            "At least one of key_validator or value_validator must be provided"
        )
        raise ValueError(msg)

    if isinstance(key_validator, (list, tuple)):
        key_validator = and_(*key_validator)
    if isinstance(value_validator, (list, tuple)):
        value_validator = and_(*value_validator)
    if isinstance(mapping_validator, (list, tuple)):
        mapping_validator = and_(*mapping_validator)

    return _DeepMapping(value_validator, mapping_validator)


def x_deep_mapping__mutmut_16(
    key_validator=None, value_validator=None, mapping_validator=None
):
    """
    A validator that performs deep validation of a dictionary.

    All validators are optional, but at least one of *key_validator* or
    *value_validator* must be provided.

    Args:
        key_validator: Validator(s) to apply to dictionary keys.

        value_validator: Validator(s) to apply to dictionary values.

        mapping_validator:
            Validator(s) to apply to top-level mapping attribute.

    .. versionadded:: 19.1.0

    .. versionchanged:: 25.4.0
       *key_validator* and *value_validator* are now optional, but at least one
       of them must be provided.

    .. versionchanged:: 25.4.0
       *key_validator*, *value_validator*, and *mapping_validator* can now be a
       list or tuple of validators.

    Raises:
        TypeError: If any sub-validator fails on validation.

        ValueError:
            If neither *key_validator* nor *value_validator* is provided on
            instantiation.
    """
    if key_validator is None and value_validator is None:
        msg = (
            "At least one of key_validator or value_validator must be provided"
        )
        raise ValueError(msg)

    if isinstance(key_validator, (list, tuple)):
        key_validator = and_(*key_validator)
    if isinstance(value_validator, (list, tuple)):
        value_validator = and_(*value_validator)
    if isinstance(mapping_validator, (list, tuple)):
        mapping_validator = and_(*mapping_validator)

    return _DeepMapping(key_validator, mapping_validator)


def x_deep_mapping__mutmut_17(
    key_validator=None, value_validator=None, mapping_validator=None
):
    """
    A validator that performs deep validation of a dictionary.

    All validators are optional, but at least one of *key_validator* or
    *value_validator* must be provided.

    Args:
        key_validator: Validator(s) to apply to dictionary keys.

        value_validator: Validator(s) to apply to dictionary values.

        mapping_validator:
            Validator(s) to apply to top-level mapping attribute.

    .. versionadded:: 19.1.0

    .. versionchanged:: 25.4.0
       *key_validator* and *value_validator* are now optional, but at least one
       of them must be provided.

    .. versionchanged:: 25.4.0
       *key_validator*, *value_validator*, and *mapping_validator* can now be a
       list or tuple of validators.

    Raises:
        TypeError: If any sub-validator fails on validation.

        ValueError:
            If neither *key_validator* nor *value_validator* is provided on
            instantiation.
    """
    if key_validator is None and value_validator is None:
        msg = (
            "At least one of key_validator or value_validator must be provided"
        )
        raise ValueError(msg)

    if isinstance(key_validator, (list, tuple)):
        key_validator = and_(*key_validator)
    if isinstance(value_validator, (list, tuple)):
        value_validator = and_(*value_validator)
    if isinstance(mapping_validator, (list, tuple)):
        mapping_validator = and_(*mapping_validator)

    return _DeepMapping(key_validator, value_validator, )

x_deep_mapping__mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
'x_deep_mapping__mutmut_1': x_deep_mapping__mutmut_1, 
    'x_deep_mapping__mutmut_2': x_deep_mapping__mutmut_2, 
    'x_deep_mapping__mutmut_3': x_deep_mapping__mutmut_3, 
    'x_deep_mapping__mutmut_4': x_deep_mapping__mutmut_4, 
    'x_deep_mapping__mutmut_5': x_deep_mapping__mutmut_5, 
    'x_deep_mapping__mutmut_6': x_deep_mapping__mutmut_6, 
    'x_deep_mapping__mutmut_7': x_deep_mapping__mutmut_7, 
    'x_deep_mapping__mutmut_8': x_deep_mapping__mutmut_8, 
    'x_deep_mapping__mutmut_9': x_deep_mapping__mutmut_9, 
    'x_deep_mapping__mutmut_10': x_deep_mapping__mutmut_10, 
    'x_deep_mapping__mutmut_11': x_deep_mapping__mutmut_11, 
    'x_deep_mapping__mutmut_12': x_deep_mapping__mutmut_12, 
    'x_deep_mapping__mutmut_13': x_deep_mapping__mutmut_13, 
    'x_deep_mapping__mutmut_14': x_deep_mapping__mutmut_14, 
    'x_deep_mapping__mutmut_15': x_deep_mapping__mutmut_15, 
    'x_deep_mapping__mutmut_16': x_deep_mapping__mutmut_16, 
    'x_deep_mapping__mutmut_17': x_deep_mapping__mutmut_17
}
x_deep_mapping__mutmut_orig.__name__ = 'x_deep_mapping'


@attrs(repr=False, frozen=True, slots=True)
class _NumberValidator:
    bound = attrib()
    compare_op = attrib()
    compare_func = attrib()

    def __call__(self, inst, attr, value):
        """
        We use a callable class to be able to change the ``__repr__``.
        """
        if not self.compare_func(value, self.bound):
            msg = f"'{attr.name}' must be {self.compare_op} {self.bound}: {value}"
            raise ValueError(msg)

    def __repr__(self):
        return f"<Validator for x {self.compare_op} {self.bound}>"


def lt(val):
    args = [val]# type: ignore
    kwargs = {}# type: ignore
    return _mutmut_trampoline(x_lt__mutmut_orig, x_lt__mutmut_mutants, args, kwargs, None)


def x_lt__mutmut_orig(val):
    """
    A validator that raises `ValueError` if the initializer is called with a
    number larger or equal to *val*.

    The validator uses `operator.lt` to compare the values.

    Args:
        val: Exclusive upper bound for values.

    .. versionadded:: 21.3.0
    """
    return _NumberValidator(val, "<", operator.lt)


def x_lt__mutmut_1(val):
    """
    A validator that raises `ValueError` if the initializer is called with a
    number larger or equal to *val*.

    The validator uses `operator.lt` to compare the values.

    Args:
        val: Exclusive upper bound for values.

    .. versionadded:: 21.3.0
    """
    return _NumberValidator(None, "<", operator.lt)


def x_lt__mutmut_2(val):
    """
    A validator that raises `ValueError` if the initializer is called with a
    number larger or equal to *val*.

    The validator uses `operator.lt` to compare the values.

    Args:
        val: Exclusive upper bound for values.

    .. versionadded:: 21.3.0
    """
    return _NumberValidator(val, None, operator.lt)


def x_lt__mutmut_3(val):
    """
    A validator that raises `ValueError` if the initializer is called with a
    number larger or equal to *val*.

    The validator uses `operator.lt` to compare the values.

    Args:
        val: Exclusive upper bound for values.

    .. versionadded:: 21.3.0
    """
    return _NumberValidator(val, "<", None)


def x_lt__mutmut_4(val):
    """
    A validator that raises `ValueError` if the initializer is called with a
    number larger or equal to *val*.

    The validator uses `operator.lt` to compare the values.

    Args:
        val: Exclusive upper bound for values.

    .. versionadded:: 21.3.0
    """
    return _NumberValidator("<", operator.lt)


def x_lt__mutmut_5(val):
    """
    A validator that raises `ValueError` if the initializer is called with a
    number larger or equal to *val*.

    The validator uses `operator.lt` to compare the values.

    Args:
        val: Exclusive upper bound for values.

    .. versionadded:: 21.3.0
    """
    return _NumberValidator(val, operator.lt)


def x_lt__mutmut_6(val):
    """
    A validator that raises `ValueError` if the initializer is called with a
    number larger or equal to *val*.

    The validator uses `operator.lt` to compare the values.

    Args:
        val: Exclusive upper bound for values.

    .. versionadded:: 21.3.0
    """
    return _NumberValidator(val, "<", )


def x_lt__mutmut_7(val):
    """
    A validator that raises `ValueError` if the initializer is called with a
    number larger or equal to *val*.

    The validator uses `operator.lt` to compare the values.

    Args:
        val: Exclusive upper bound for values.

    .. versionadded:: 21.3.0
    """
    return _NumberValidator(val, "XX<XX", operator.lt)

x_lt__mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
'x_lt__mutmut_1': x_lt__mutmut_1, 
    'x_lt__mutmut_2': x_lt__mutmut_2, 
    'x_lt__mutmut_3': x_lt__mutmut_3, 
    'x_lt__mutmut_4': x_lt__mutmut_4, 
    'x_lt__mutmut_5': x_lt__mutmut_5, 
    'x_lt__mutmut_6': x_lt__mutmut_6, 
    'x_lt__mutmut_7': x_lt__mutmut_7
}
x_lt__mutmut_orig.__name__ = 'x_lt'


def le(val):
    args = [val]# type: ignore
    kwargs = {}# type: ignore
    return _mutmut_trampoline(x_le__mutmut_orig, x_le__mutmut_mutants, args, kwargs, None)


def x_le__mutmut_orig(val):
    """
    A validator that raises `ValueError` if the initializer is called with a
    number greater than *val*.

    The validator uses `operator.le` to compare the values.

    Args:
        val: Inclusive upper bound for values.

    .. versionadded:: 21.3.0
    """
    return _NumberValidator(val, "<=", operator.le)


def x_le__mutmut_1(val):
    """
    A validator that raises `ValueError` if the initializer is called with a
    number greater than *val*.

    The validator uses `operator.le` to compare the values.

    Args:
        val: Inclusive upper bound for values.

    .. versionadded:: 21.3.0
    """
    return _NumberValidator(None, "<=", operator.le)


def x_le__mutmut_2(val):
    """
    A validator that raises `ValueError` if the initializer is called with a
    number greater than *val*.

    The validator uses `operator.le` to compare the values.

    Args:
        val: Inclusive upper bound for values.

    .. versionadded:: 21.3.0
    """
    return _NumberValidator(val, None, operator.le)


def x_le__mutmut_3(val):
    """
    A validator that raises `ValueError` if the initializer is called with a
    number greater than *val*.

    The validator uses `operator.le` to compare the values.

    Args:
        val: Inclusive upper bound for values.

    .. versionadded:: 21.3.0
    """
    return _NumberValidator(val, "<=", None)


def x_le__mutmut_4(val):
    """
    A validator that raises `ValueError` if the initializer is called with a
    number greater than *val*.

    The validator uses `operator.le` to compare the values.

    Args:
        val: Inclusive upper bound for values.

    .. versionadded:: 21.3.0
    """
    return _NumberValidator("<=", operator.le)


def x_le__mutmut_5(val):
    """
    A validator that raises `ValueError` if the initializer is called with a
    number greater than *val*.

    The validator uses `operator.le` to compare the values.

    Args:
        val: Inclusive upper bound for values.

    .. versionadded:: 21.3.0
    """
    return _NumberValidator(val, operator.le)


def x_le__mutmut_6(val):
    """
    A validator that raises `ValueError` if the initializer is called with a
    number greater than *val*.

    The validator uses `operator.le` to compare the values.

    Args:
        val: Inclusive upper bound for values.

    .. versionadded:: 21.3.0
    """
    return _NumberValidator(val, "<=", )


def x_le__mutmut_7(val):
    """
    A validator that raises `ValueError` if the initializer is called with a
    number greater than *val*.

    The validator uses `operator.le` to compare the values.

    Args:
        val: Inclusive upper bound for values.

    .. versionadded:: 21.3.0
    """
    return _NumberValidator(val, "XX<=XX", operator.le)

x_le__mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
'x_le__mutmut_1': x_le__mutmut_1, 
    'x_le__mutmut_2': x_le__mutmut_2, 
    'x_le__mutmut_3': x_le__mutmut_3, 
    'x_le__mutmut_4': x_le__mutmut_4, 
    'x_le__mutmut_5': x_le__mutmut_5, 
    'x_le__mutmut_6': x_le__mutmut_6, 
    'x_le__mutmut_7': x_le__mutmut_7
}
x_le__mutmut_orig.__name__ = 'x_le'


def ge(val):
    args = [val]# type: ignore
    kwargs = {}# type: ignore
    return _mutmut_trampoline(x_ge__mutmut_orig, x_ge__mutmut_mutants, args, kwargs, None)


def x_ge__mutmut_orig(val):
    """
    A validator that raises `ValueError` if the initializer is called with a
    number smaller than *val*.

    The validator uses `operator.ge` to compare the values.

    Args:
        val: Inclusive lower bound for values

    .. versionadded:: 21.3.0
    """
    return _NumberValidator(val, ">=", operator.ge)


def x_ge__mutmut_1(val):
    """
    A validator that raises `ValueError` if the initializer is called with a
    number smaller than *val*.

    The validator uses `operator.ge` to compare the values.

    Args:
        val: Inclusive lower bound for values

    .. versionadded:: 21.3.0
    """
    return _NumberValidator(None, ">=", operator.ge)


def x_ge__mutmut_2(val):
    """
    A validator that raises `ValueError` if the initializer is called with a
    number smaller than *val*.

    The validator uses `operator.ge` to compare the values.

    Args:
        val: Inclusive lower bound for values

    .. versionadded:: 21.3.0
    """
    return _NumberValidator(val, None, operator.ge)


def x_ge__mutmut_3(val):
    """
    A validator that raises `ValueError` if the initializer is called with a
    number smaller than *val*.

    The validator uses `operator.ge` to compare the values.

    Args:
        val: Inclusive lower bound for values

    .. versionadded:: 21.3.0
    """
    return _NumberValidator(val, ">=", None)


def x_ge__mutmut_4(val):
    """
    A validator that raises `ValueError` if the initializer is called with a
    number smaller than *val*.

    The validator uses `operator.ge` to compare the values.

    Args:
        val: Inclusive lower bound for values

    .. versionadded:: 21.3.0
    """
    return _NumberValidator(">=", operator.ge)


def x_ge__mutmut_5(val):
    """
    A validator that raises `ValueError` if the initializer is called with a
    number smaller than *val*.

    The validator uses `operator.ge` to compare the values.

    Args:
        val: Inclusive lower bound for values

    .. versionadded:: 21.3.0
    """
    return _NumberValidator(val, operator.ge)


def x_ge__mutmut_6(val):
    """
    A validator that raises `ValueError` if the initializer is called with a
    number smaller than *val*.

    The validator uses `operator.ge` to compare the values.

    Args:
        val: Inclusive lower bound for values

    .. versionadded:: 21.3.0
    """
    return _NumberValidator(val, ">=", )


def x_ge__mutmut_7(val):
    """
    A validator that raises `ValueError` if the initializer is called with a
    number smaller than *val*.

    The validator uses `operator.ge` to compare the values.

    Args:
        val: Inclusive lower bound for values

    .. versionadded:: 21.3.0
    """
    return _NumberValidator(val, "XX>=XX", operator.ge)

x_ge__mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
'x_ge__mutmut_1': x_ge__mutmut_1, 
    'x_ge__mutmut_2': x_ge__mutmut_2, 
    'x_ge__mutmut_3': x_ge__mutmut_3, 
    'x_ge__mutmut_4': x_ge__mutmut_4, 
    'x_ge__mutmut_5': x_ge__mutmut_5, 
    'x_ge__mutmut_6': x_ge__mutmut_6, 
    'x_ge__mutmut_7': x_ge__mutmut_7
}
x_ge__mutmut_orig.__name__ = 'x_ge'


def gt(val):
    args = [val]# type: ignore
    kwargs = {}# type: ignore
    return _mutmut_trampoline(x_gt__mutmut_orig, x_gt__mutmut_mutants, args, kwargs, None)


def x_gt__mutmut_orig(val):
    """
    A validator that raises `ValueError` if the initializer is called with a
    number smaller or equal to *val*.

    The validator uses `operator.gt` to compare the values.

    Args:
       val: Exclusive lower bound for values

    .. versionadded:: 21.3.0
    """
    return _NumberValidator(val, ">", operator.gt)


def x_gt__mutmut_1(val):
    """
    A validator that raises `ValueError` if the initializer is called with a
    number smaller or equal to *val*.

    The validator uses `operator.gt` to compare the values.

    Args:
       val: Exclusive lower bound for values

    .. versionadded:: 21.3.0
    """
    return _NumberValidator(None, ">", operator.gt)


def x_gt__mutmut_2(val):
    """
    A validator that raises `ValueError` if the initializer is called with a
    number smaller or equal to *val*.

    The validator uses `operator.gt` to compare the values.

    Args:
       val: Exclusive lower bound for values

    .. versionadded:: 21.3.0
    """
    return _NumberValidator(val, None, operator.gt)


def x_gt__mutmut_3(val):
    """
    A validator that raises `ValueError` if the initializer is called with a
    number smaller or equal to *val*.

    The validator uses `operator.gt` to compare the values.

    Args:
       val: Exclusive lower bound for values

    .. versionadded:: 21.3.0
    """
    return _NumberValidator(val, ">", None)


def x_gt__mutmut_4(val):
    """
    A validator that raises `ValueError` if the initializer is called with a
    number smaller or equal to *val*.

    The validator uses `operator.gt` to compare the values.

    Args:
       val: Exclusive lower bound for values

    .. versionadded:: 21.3.0
    """
    return _NumberValidator(">", operator.gt)


def x_gt__mutmut_5(val):
    """
    A validator that raises `ValueError` if the initializer is called with a
    number smaller or equal to *val*.

    The validator uses `operator.gt` to compare the values.

    Args:
       val: Exclusive lower bound for values

    .. versionadded:: 21.3.0
    """
    return _NumberValidator(val, operator.gt)


def x_gt__mutmut_6(val):
    """
    A validator that raises `ValueError` if the initializer is called with a
    number smaller or equal to *val*.

    The validator uses `operator.gt` to compare the values.

    Args:
       val: Exclusive lower bound for values

    .. versionadded:: 21.3.0
    """
    return _NumberValidator(val, ">", )


def x_gt__mutmut_7(val):
    """
    A validator that raises `ValueError` if the initializer is called with a
    number smaller or equal to *val*.

    The validator uses `operator.gt` to compare the values.

    Args:
       val: Exclusive lower bound for values

    .. versionadded:: 21.3.0
    """
    return _NumberValidator(val, "XX>XX", operator.gt)

x_gt__mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
'x_gt__mutmut_1': x_gt__mutmut_1, 
    'x_gt__mutmut_2': x_gt__mutmut_2, 
    'x_gt__mutmut_3': x_gt__mutmut_3, 
    'x_gt__mutmut_4': x_gt__mutmut_4, 
    'x_gt__mutmut_5': x_gt__mutmut_5, 
    'x_gt__mutmut_6': x_gt__mutmut_6, 
    'x_gt__mutmut_7': x_gt__mutmut_7
}
x_gt__mutmut_orig.__name__ = 'x_gt'


@attrs(repr=False, frozen=True, slots=True)
class _MaxLengthValidator:
    max_length = attrib()

    def __call__(self, inst, attr, value):
        """
        We use a callable class to be able to change the ``__repr__``.
        """
        if len(value) > self.max_length:
            msg = f"Length of '{attr.name}' must be <= {self.max_length}: {len(value)}"
            raise ValueError(msg)

    def __repr__(self):
        return f"<max_len validator for {self.max_length}>"


def max_len(length):
    args = [length]# type: ignore
    kwargs = {}# type: ignore
    return _mutmut_trampoline(x_max_len__mutmut_orig, x_max_len__mutmut_mutants, args, kwargs, None)


def x_max_len__mutmut_orig(length):
    """
    A validator that raises `ValueError` if the initializer is called
    with a string or iterable that is longer than *length*.

    Args:
        length (int): Maximum length of the string or iterable

    .. versionadded:: 21.3.0
    """
    return _MaxLengthValidator(length)


def x_max_len__mutmut_1(length):
    """
    A validator that raises `ValueError` if the initializer is called
    with a string or iterable that is longer than *length*.

    Args:
        length (int): Maximum length of the string or iterable

    .. versionadded:: 21.3.0
    """
    return _MaxLengthValidator(None)

x_max_len__mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
'x_max_len__mutmut_1': x_max_len__mutmut_1
}
x_max_len__mutmut_orig.__name__ = 'x_max_len'


@attrs(repr=False, frozen=True, slots=True)
class _MinLengthValidator:
    min_length = attrib()

    def __call__(self, inst, attr, value):
        """
        We use a callable class to be able to change the ``__repr__``.
        """
        if len(value) < self.min_length:
            msg = f"Length of '{attr.name}' must be >= {self.min_length}: {len(value)}"
            raise ValueError(msg)

    def __repr__(self):
        return f"<min_len validator for {self.min_length}>"


def min_len(length):
    args = [length]# type: ignore
    kwargs = {}# type: ignore
    return _mutmut_trampoline(x_min_len__mutmut_orig, x_min_len__mutmut_mutants, args, kwargs, None)


def x_min_len__mutmut_orig(length):
    """
    A validator that raises `ValueError` if the initializer is called
    with a string or iterable that is shorter than *length*.

    Args:
        length (int): Minimum length of the string or iterable

    .. versionadded:: 22.1.0
    """
    return _MinLengthValidator(length)


def x_min_len__mutmut_1(length):
    """
    A validator that raises `ValueError` if the initializer is called
    with a string or iterable that is shorter than *length*.

    Args:
        length (int): Minimum length of the string or iterable

    .. versionadded:: 22.1.0
    """
    return _MinLengthValidator(None)

x_min_len__mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
'x_min_len__mutmut_1': x_min_len__mutmut_1
}
x_min_len__mutmut_orig.__name__ = 'x_min_len'


@attrs(repr=False, slots=True, unsafe_hash=True)
class _SubclassOfValidator:
    type = attrib()

    def __call__(self, inst, attr, value):
        """
        We use a callable class to be able to change the ``__repr__``.
        """
        if not issubclass(value, self.type):
            msg = f"'{attr.name}' must be a subclass of {self.type!r} (got {value!r})."
            raise TypeError(
                msg,
                attr,
                self.type,
                value,
            )

    def __repr__(self):
        return f"<subclass_of validator for type {self.type!r}>"


def _subclass_of(type):
    args = [type]# type: ignore
    kwargs = {}# type: ignore
    return _mutmut_trampoline(x__subclass_of__mutmut_orig, x__subclass_of__mutmut_mutants, args, kwargs, None)


def x__subclass_of__mutmut_orig(type):
    """
    A validator that raises a `TypeError` if the initializer is called with a
    wrong type for this particular attribute (checks are performed using
    `issubclass` therefore it's also valid to pass a tuple of types).

    Args:
        type (type | tuple[type, ...]): The type(s) to check for.

    Raises:
        TypeError:
            With a human readable error message, the attribute (of type
            `attrs.Attribute`), the expected type, and the value it got.
    """
    return _SubclassOfValidator(type)


def x__subclass_of__mutmut_1(type):
    """
    A validator that raises a `TypeError` if the initializer is called with a
    wrong type for this particular attribute (checks are performed using
    `issubclass` therefore it's also valid to pass a tuple of types).

    Args:
        type (type | tuple[type, ...]): The type(s) to check for.

    Raises:
        TypeError:
            With a human readable error message, the attribute (of type
            `attrs.Attribute`), the expected type, and the value it got.
    """
    return _SubclassOfValidator(None)

x__subclass_of__mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
'x__subclass_of__mutmut_1': x__subclass_of__mutmut_1
}
x__subclass_of__mutmut_orig.__name__ = 'x__subclass_of'


@attrs(repr=False, slots=True, unsafe_hash=True)
class _NotValidator:
    validator = attrib()
    msg = attrib(
        converter=default_if_none(
            "not_ validator child '{validator!r}' "
            "did not raise a captured error"
        )
    )
    exc_types = attrib(
        validator=deep_iterable(
            member_validator=_subclass_of(Exception),
            iterable_validator=instance_of(tuple),
        ),
    )

    def __call__(self, inst, attr, value):
        try:
            self.validator(inst, attr, value)
        except self.exc_types:
            pass  # suppress error to invert validity
        else:
            raise ValueError(
                self.msg.format(
                    validator=self.validator,
                    exc_types=self.exc_types,
                ),
                attr,
                self.validator,
                value,
                self.exc_types,
            )

    def __repr__(self):
        return f"<not_ validator wrapping {self.validator!r}, capturing {self.exc_types!r}>"


def not_(validator, *, msg=None, exc_types=(ValueError, TypeError)):
    args = [validator]# type: ignore
    kwargs = {'msg': msg, 'exc_types': exc_types}# type: ignore
    return _mutmut_trampoline(x_not___mutmut_orig, x_not___mutmut_mutants, args, kwargs, None)


def x_not___mutmut_orig(validator, *, msg=None, exc_types=(ValueError, TypeError)):
    """
    A validator that wraps and logically 'inverts' the validator passed to it.
    It will raise a `ValueError` if the provided validator *doesn't* raise a
    `ValueError` or `TypeError` (by default), and will suppress the exception
    if the provided validator *does*.

    Intended to be used with existing validators to compose logic without
    needing to create inverted variants, for example, ``not_(in_(...))``.

    Args:
        validator: A validator to be logically inverted.

        msg (str):
            Message to raise if validator fails. Formatted with keys
            ``exc_types`` and ``validator``.

        exc_types (tuple[type, ...]):
            Exception type(s) to capture. Other types raised by child
            validators will not be intercepted and pass through.

    Raises:
        ValueError:
            With a human readable error message, the attribute (of type
            `attrs.Attribute`), the validator that failed to raise an
            exception, the value it got, and the expected exception types.

    .. versionadded:: 22.2.0
    """
    try:
        exc_types = tuple(exc_types)
    except TypeError:
        exc_types = (exc_types,)
    return _NotValidator(validator, msg, exc_types)


def x_not___mutmut_1(validator, *, msg=None, exc_types=(ValueError, TypeError)):
    """
    A validator that wraps and logically 'inverts' the validator passed to it.
    It will raise a `ValueError` if the provided validator *doesn't* raise a
    `ValueError` or `TypeError` (by default), and will suppress the exception
    if the provided validator *does*.

    Intended to be used with existing validators to compose logic without
    needing to create inverted variants, for example, ``not_(in_(...))``.

    Args:
        validator: A validator to be logically inverted.

        msg (str):
            Message to raise if validator fails. Formatted with keys
            ``exc_types`` and ``validator``.

        exc_types (tuple[type, ...]):
            Exception type(s) to capture. Other types raised by child
            validators will not be intercepted and pass through.

    Raises:
        ValueError:
            With a human readable error message, the attribute (of type
            `attrs.Attribute`), the validator that failed to raise an
            exception, the value it got, and the expected exception types.

    .. versionadded:: 22.2.0
    """
    try:
        exc_types = None
    except TypeError:
        exc_types = (exc_types,)
    return _NotValidator(validator, msg, exc_types)


def x_not___mutmut_2(validator, *, msg=None, exc_types=(ValueError, TypeError)):
    """
    A validator that wraps and logically 'inverts' the validator passed to it.
    It will raise a `ValueError` if the provided validator *doesn't* raise a
    `ValueError` or `TypeError` (by default), and will suppress the exception
    if the provided validator *does*.

    Intended to be used with existing validators to compose logic without
    needing to create inverted variants, for example, ``not_(in_(...))``.

    Args:
        validator: A validator to be logically inverted.

        msg (str):
            Message to raise if validator fails. Formatted with keys
            ``exc_types`` and ``validator``.

        exc_types (tuple[type, ...]):
            Exception type(s) to capture. Other types raised by child
            validators will not be intercepted and pass through.

    Raises:
        ValueError:
            With a human readable error message, the attribute (of type
            `attrs.Attribute`), the validator that failed to raise an
            exception, the value it got, and the expected exception types.

    .. versionadded:: 22.2.0
    """
    try:
        exc_types = tuple(None)
    except TypeError:
        exc_types = (exc_types,)
    return _NotValidator(validator, msg, exc_types)


def x_not___mutmut_3(validator, *, msg=None, exc_types=(ValueError, TypeError)):
    """
    A validator that wraps and logically 'inverts' the validator passed to it.
    It will raise a `ValueError` if the provided validator *doesn't* raise a
    `ValueError` or `TypeError` (by default), and will suppress the exception
    if the provided validator *does*.

    Intended to be used with existing validators to compose logic without
    needing to create inverted variants, for example, ``not_(in_(...))``.

    Args:
        validator: A validator to be logically inverted.

        msg (str):
            Message to raise if validator fails. Formatted with keys
            ``exc_types`` and ``validator``.

        exc_types (tuple[type, ...]):
            Exception type(s) to capture. Other types raised by child
            validators will not be intercepted and pass through.

    Raises:
        ValueError:
            With a human readable error message, the attribute (of type
            `attrs.Attribute`), the validator that failed to raise an
            exception, the value it got, and the expected exception types.

    .. versionadded:: 22.2.0
    """
    try:
        exc_types = tuple(exc_types)
    except TypeError:
        exc_types = None
    return _NotValidator(validator, msg, exc_types)


def x_not___mutmut_4(validator, *, msg=None, exc_types=(ValueError, TypeError)):
    """
    A validator that wraps and logically 'inverts' the validator passed to it.
    It will raise a `ValueError` if the provided validator *doesn't* raise a
    `ValueError` or `TypeError` (by default), and will suppress the exception
    if the provided validator *does*.

    Intended to be used with existing validators to compose logic without
    needing to create inverted variants, for example, ``not_(in_(...))``.

    Args:
        validator: A validator to be logically inverted.

        msg (str):
            Message to raise if validator fails. Formatted with keys
            ``exc_types`` and ``validator``.

        exc_types (tuple[type, ...]):
            Exception type(s) to capture. Other types raised by child
            validators will not be intercepted and pass through.

    Raises:
        ValueError:
            With a human readable error message, the attribute (of type
            `attrs.Attribute`), the validator that failed to raise an
            exception, the value it got, and the expected exception types.

    .. versionadded:: 22.2.0
    """
    try:
        exc_types = tuple(exc_types)
    except TypeError:
        exc_types = (exc_types,)
    return _NotValidator(None, msg, exc_types)


def x_not___mutmut_5(validator, *, msg=None, exc_types=(ValueError, TypeError)):
    """
    A validator that wraps and logically 'inverts' the validator passed to it.
    It will raise a `ValueError` if the provided validator *doesn't* raise a
    `ValueError` or `TypeError` (by default), and will suppress the exception
    if the provided validator *does*.

    Intended to be used with existing validators to compose logic without
    needing to create inverted variants, for example, ``not_(in_(...))``.

    Args:
        validator: A validator to be logically inverted.

        msg (str):
            Message to raise if validator fails. Formatted with keys
            ``exc_types`` and ``validator``.

        exc_types (tuple[type, ...]):
            Exception type(s) to capture. Other types raised by child
            validators will not be intercepted and pass through.

    Raises:
        ValueError:
            With a human readable error message, the attribute (of type
            `attrs.Attribute`), the validator that failed to raise an
            exception, the value it got, and the expected exception types.

    .. versionadded:: 22.2.0
    """
    try:
        exc_types = tuple(exc_types)
    except TypeError:
        exc_types = (exc_types,)
    return _NotValidator(validator, None, exc_types)


def x_not___mutmut_6(validator, *, msg=None, exc_types=(ValueError, TypeError)):
    """
    A validator that wraps and logically 'inverts' the validator passed to it.
    It will raise a `ValueError` if the provided validator *doesn't* raise a
    `ValueError` or `TypeError` (by default), and will suppress the exception
    if the provided validator *does*.

    Intended to be used with existing validators to compose logic without
    needing to create inverted variants, for example, ``not_(in_(...))``.

    Args:
        validator: A validator to be logically inverted.

        msg (str):
            Message to raise if validator fails. Formatted with keys
            ``exc_types`` and ``validator``.

        exc_types (tuple[type, ...]):
            Exception type(s) to capture. Other types raised by child
            validators will not be intercepted and pass through.

    Raises:
        ValueError:
            With a human readable error message, the attribute (of type
            `attrs.Attribute`), the validator that failed to raise an
            exception, the value it got, and the expected exception types.

    .. versionadded:: 22.2.0
    """
    try:
        exc_types = tuple(exc_types)
    except TypeError:
        exc_types = (exc_types,)
    return _NotValidator(validator, msg, None)


def x_not___mutmut_7(validator, *, msg=None, exc_types=(ValueError, TypeError)):
    """
    A validator that wraps and logically 'inverts' the validator passed to it.
    It will raise a `ValueError` if the provided validator *doesn't* raise a
    `ValueError` or `TypeError` (by default), and will suppress the exception
    if the provided validator *does*.

    Intended to be used with existing validators to compose logic without
    needing to create inverted variants, for example, ``not_(in_(...))``.

    Args:
        validator: A validator to be logically inverted.

        msg (str):
            Message to raise if validator fails. Formatted with keys
            ``exc_types`` and ``validator``.

        exc_types (tuple[type, ...]):
            Exception type(s) to capture. Other types raised by child
            validators will not be intercepted and pass through.

    Raises:
        ValueError:
            With a human readable error message, the attribute (of type
            `attrs.Attribute`), the validator that failed to raise an
            exception, the value it got, and the expected exception types.

    .. versionadded:: 22.2.0
    """
    try:
        exc_types = tuple(exc_types)
    except TypeError:
        exc_types = (exc_types,)
    return _NotValidator(msg, exc_types)


def x_not___mutmut_8(validator, *, msg=None, exc_types=(ValueError, TypeError)):
    """
    A validator that wraps and logically 'inverts' the validator passed to it.
    It will raise a `ValueError` if the provided validator *doesn't* raise a
    `ValueError` or `TypeError` (by default), and will suppress the exception
    if the provided validator *does*.

    Intended to be used with existing validators to compose logic without
    needing to create inverted variants, for example, ``not_(in_(...))``.

    Args:
        validator: A validator to be logically inverted.

        msg (str):
            Message to raise if validator fails. Formatted with keys
            ``exc_types`` and ``validator``.

        exc_types (tuple[type, ...]):
            Exception type(s) to capture. Other types raised by child
            validators will not be intercepted and pass through.

    Raises:
        ValueError:
            With a human readable error message, the attribute (of type
            `attrs.Attribute`), the validator that failed to raise an
            exception, the value it got, and the expected exception types.

    .. versionadded:: 22.2.0
    """
    try:
        exc_types = tuple(exc_types)
    except TypeError:
        exc_types = (exc_types,)
    return _NotValidator(validator, exc_types)


def x_not___mutmut_9(validator, *, msg=None, exc_types=(ValueError, TypeError)):
    """
    A validator that wraps and logically 'inverts' the validator passed to it.
    It will raise a `ValueError` if the provided validator *doesn't* raise a
    `ValueError` or `TypeError` (by default), and will suppress the exception
    if the provided validator *does*.

    Intended to be used with existing validators to compose logic without
    needing to create inverted variants, for example, ``not_(in_(...))``.

    Args:
        validator: A validator to be logically inverted.

        msg (str):
            Message to raise if validator fails. Formatted with keys
            ``exc_types`` and ``validator``.

        exc_types (tuple[type, ...]):
            Exception type(s) to capture. Other types raised by child
            validators will not be intercepted and pass through.

    Raises:
        ValueError:
            With a human readable error message, the attribute (of type
            `attrs.Attribute`), the validator that failed to raise an
            exception, the value it got, and the expected exception types.

    .. versionadded:: 22.2.0
    """
    try:
        exc_types = tuple(exc_types)
    except TypeError:
        exc_types = (exc_types,)
    return _NotValidator(validator, msg, )

x_not___mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
'x_not___mutmut_1': x_not___mutmut_1, 
    'x_not___mutmut_2': x_not___mutmut_2, 
    'x_not___mutmut_3': x_not___mutmut_3, 
    'x_not___mutmut_4': x_not___mutmut_4, 
    'x_not___mutmut_5': x_not___mutmut_5, 
    'x_not___mutmut_6': x_not___mutmut_6, 
    'x_not___mutmut_7': x_not___mutmut_7, 
    'x_not___mutmut_8': x_not___mutmut_8, 
    'x_not___mutmut_9': x_not___mutmut_9
}
x_not___mutmut_orig.__name__ = 'x_not_'


@attrs(repr=False, slots=True, unsafe_hash=True)
class _OrValidator:
    validators = attrib()

    def __call__(self, inst, attr, value):
        for v in self.validators:
            try:
                v(inst, attr, value)
            except Exception:  # noqa: BLE001, PERF203, S112
                continue
            else:
                return

        msg = f"None of {self.validators!r} satisfied for value {value!r}"
        raise ValueError(msg)

    def __repr__(self):
        return f"<or validator wrapping {self.validators!r}>"


def or_(*validators):
    args = [*validators]# type: ignore
    kwargs = {}# type: ignore
    return _mutmut_trampoline(x_or___mutmut_orig, x_or___mutmut_mutants, args, kwargs, None)


def x_or___mutmut_orig(*validators):
    """
    A validator that composes multiple validators into one.

    When called on a value, it runs all wrapped validators until one of them is
    satisfied.

    Args:
        validators (~collections.abc.Iterable[typing.Callable]):
            Arbitrary number of validators.

    Raises:
        ValueError:
            If no validator is satisfied. Raised with a human-readable error
            message listing all the wrapped validators and the value that
            failed all of them.

    .. versionadded:: 24.1.0
    """
    vals = []
    for v in validators:
        vals.extend(v.validators if isinstance(v, _OrValidator) else [v])

    return _OrValidator(tuple(vals))


def x_or___mutmut_1(*validators):
    """
    A validator that composes multiple validators into one.

    When called on a value, it runs all wrapped validators until one of them is
    satisfied.

    Args:
        validators (~collections.abc.Iterable[typing.Callable]):
            Arbitrary number of validators.

    Raises:
        ValueError:
            If no validator is satisfied. Raised with a human-readable error
            message listing all the wrapped validators and the value that
            failed all of them.

    .. versionadded:: 24.1.0
    """
    vals = None
    for v in validators:
        vals.extend(v.validators if isinstance(v, _OrValidator) else [v])

    return _OrValidator(tuple(vals))


def x_or___mutmut_2(*validators):
    """
    A validator that composes multiple validators into one.

    When called on a value, it runs all wrapped validators until one of them is
    satisfied.

    Args:
        validators (~collections.abc.Iterable[typing.Callable]):
            Arbitrary number of validators.

    Raises:
        ValueError:
            If no validator is satisfied. Raised with a human-readable error
            message listing all the wrapped validators and the value that
            failed all of them.

    .. versionadded:: 24.1.0
    """
    vals = []
    for v in validators:
        vals.extend(None)

    return _OrValidator(tuple(vals))


def x_or___mutmut_3(*validators):
    """
    A validator that composes multiple validators into one.

    When called on a value, it runs all wrapped validators until one of them is
    satisfied.

    Args:
        validators (~collections.abc.Iterable[typing.Callable]):
            Arbitrary number of validators.

    Raises:
        ValueError:
            If no validator is satisfied. Raised with a human-readable error
            message listing all the wrapped validators and the value that
            failed all of them.

    .. versionadded:: 24.1.0
    """
    vals = []
    for v in validators:
        vals.extend(v.validators if isinstance(v, _OrValidator) else [v])

    return _OrValidator(None)


def x_or___mutmut_4(*validators):
    """
    A validator that composes multiple validators into one.

    When called on a value, it runs all wrapped validators until one of them is
    satisfied.

    Args:
        validators (~collections.abc.Iterable[typing.Callable]):
            Arbitrary number of validators.

    Raises:
        ValueError:
            If no validator is satisfied. Raised with a human-readable error
            message listing all the wrapped validators and the value that
            failed all of them.

    .. versionadded:: 24.1.0
    """
    vals = []
    for v in validators:
        vals.extend(v.validators if isinstance(v, _OrValidator) else [v])

    return _OrValidator(tuple(None))

x_or___mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
'x_or___mutmut_1': x_or___mutmut_1, 
    'x_or___mutmut_2': x_or___mutmut_2, 
    'x_or___mutmut_3': x_or___mutmut_3, 
    'x_or___mutmut_4': x_or___mutmut_4
}
x_or___mutmut_orig.__name__ = 'x_or_'

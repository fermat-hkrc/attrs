# SPDX-License-Identifier: MIT

"""
Property-based tests for `attr.setters`.
"""

import pytest

from hypothesis import given
from hypothesis import strategies as st

import attr

from attr import setters
from attr.exceptions import FrozenAttributeError


class TestSettersPipe:
    """
    Property-based tests for setters.pipe.
    """

    @given(st.integers())
    def test_pipe_single_setter_identity(self, value):
        """
        Property: pipe with a single identity setter returns the value unchanged.
        """

        def identity_setter(instance, attrib, new_value):
            return new_value

        piped = setters.pipe(identity_setter)

        @attr.s
        class C:
            x = attr.ib(on_setattr=piped)

        c = C(value)
        assert c.x == value

        # Test setting after initialization
        new_val = value + 1
        c.x = new_val
        assert c.x == new_val

    @given(st.integers(), st.integers())
    def test_pipe_multiple_setters_composition(self, initial, value):
        """
        Property: pipe composes setters in order.
        """

        def add_one(instance, attrib, new_value):
            return new_value + 1

        def multiply_two(instance, attrib, new_value):
            return new_value * 2

        # Should apply add_one first, then multiply_two
        # Result: (value + 1) * 2
        piped = setters.pipe(add_one, multiply_two)

        @attr.s
        class C:
            x = attr.ib(on_setattr=piped)

        c = C(initial)
        # on_setattr is not called during __init__, only on subsequent sets
        assert c.x == initial

        # Now set the value - this should trigger the pipe
        c.x = value
        expected = (value + 1) * 2
        assert c.x == expected

    @given(st.integers(), st.integers())
    def test_pipe_order_matters(self, initial, value):
        """
        Property: The order of setters in pipe matters.
        """

        def add_one(instance, attrib, new_value):
            return new_value + 1

        def multiply_two(instance, attrib, new_value):
            return new_value * 2

        # Order 1: add then multiply
        piped1 = setters.pipe(add_one, multiply_two)
        # Order 2: multiply then add
        piped2 = setters.pipe(multiply_two, add_one)

        @attr.s
        class C1:
            x = attr.ib(on_setattr=piped1)

        @attr.s
        class C2:
            x = attr.ib(on_setattr=piped2)

        c1 = C1(initial)
        c2 = C2(initial)

        # Set the value - this triggers the pipe
        c1.x = value
        c2.x = value

        # (value + 1) * 2 != value * 2 + 1 for most values
        expected1 = (value + 1) * 2
        expected2 = value * 2 + 1

        assert c1.x == expected1
        assert c2.x == expected2

        # They should be different for most values
        if value != 0:
            assert c1.x != c2.x

    @given(st.integers())
    def test_pipe_empty_is_identity(self, value):
        """
        Property: pipe with no setters acts as identity.
        """
        piped = setters.pipe()

        @attr.s
        class C:
            x = attr.ib(on_setattr=piped)

        c = C(value)
        assert c.x == value

    @given(st.integers(), st.integers())
    def test_pipe_with_convert(self, initial, new_value):
        """
        Property: pipe can include the convert setter.
        """

        def double(x):
            return x * 2

        piped = setters.pipe(setters.convert)

        @attr.s
        class C:
            x = attr.ib(converter=double, on_setattr=piped)

        c = C(initial)
        assert c.x == initial * 2

        c.x = new_value
        assert c.x == new_value * 2

    @given(st.integers(min_value=0, max_value=100))
    def test_pipe_with_validate(self, value):
        """
        Property: pipe can include the validate setter.
        """
        piped = setters.pipe(setters.validate)

        @attr.s
        class C:
            x = attr.ib(validator=attr.validators.ge(0), on_setattr=piped)

        # Valid value should work
        c = C(value)
        assert c.x == value

        # Invalid value should raise
        with pytest.raises(ValueError):
            c.x = -1


class TestFrozenSetter:
    """
    Property-based tests for setters.frozen.
    """

    @given(st.integers(), st.integers())
    def test_frozen_prevents_modification(self, initial, new_value):
        """
        Property: frozen setter prevents any modification after initialization.
        """

        @attr.s
        class C:
            x = attr.ib(on_setattr=setters.frozen)

        c = C(initial)
        assert c.x == initial

        # Attempting to modify should raise FrozenAttributeError
        with pytest.raises(FrozenAttributeError):
            c.x = new_value

        # Value should remain unchanged
        assert c.x == initial

    @given(st.integers())
    def test_frozen_allows_initialization(self, value):
        """
        Property: frozen setter allows setting during initialization.
        """

        @attr.s
        class C:
            x = attr.ib(on_setattr=setters.frozen)

        # Should be able to create instance
        c = C(value)
        assert c.x == value


class TestValidateSetter:
    """
    Property-based tests for setters.validate.
    """

    @given(st.integers(min_value=0, max_value=100), st.integers(min_value=0, max_value=100))
    def test_validate_accepts_valid_values(self, initial, new_value):
        """
        Property: validate setter accepts values that pass validation.
        """

        @attr.s
        class C:
            x = attr.ib(validator=attr.validators.ge(0), on_setattr=setters.validate)

        c = C(initial)
        c.x = new_value
        assert c.x == new_value

    @given(st.integers(min_value=0, max_value=100), st.integers(max_value=-1))
    def test_validate_rejects_invalid_values(self, initial, invalid_value):
        """
        Property: validate setter rejects values that fail validation.
        """

        @attr.s
        class C:
            x = attr.ib(validator=attr.validators.ge(0), on_setattr=setters.validate)

        c = C(initial)

        with pytest.raises(ValueError):
            c.x = invalid_value

        # Original value should be preserved
        assert c.x == initial

    @given(st.integers())
    def test_validate_no_validator_is_noop(self, value):
        """
        Property: validate setter with no validator acts as identity.
        """

        @attr.s
        class C:
            x = attr.ib(on_setattr=setters.validate)

        c = C(value)
        assert c.x == value

        new_value = value + 1
        c.x = new_value
        assert c.x == new_value


class TestConvertSetter:
    """
    Property-based tests for setters.convert.
    """

    @given(st.integers())
    def test_convert_applies_converter(self, value):
        """
        Property: convert setter applies the converter function.
        """

        def double(x):
            return x * 2

        @attr.s
        class C:
            x = attr.ib(converter=double, on_setattr=setters.convert)

        c = C(value)
        assert c.x == value * 2

        new_value = value + 1
        c.x = new_value
        assert c.x == new_value * 2

    @given(st.integers())
    def test_convert_no_converter_is_noop(self, value):
        """
        Property: convert setter with no converter acts as identity.
        """

        @attr.s
        class C:
            x = attr.ib(on_setattr=setters.convert)

        c = C(value)
        assert c.x == value

        new_value = value + 1
        c.x = new_value
        assert c.x == new_value

    @given(st.text())
    def test_convert_type_conversion(self, value):
        """
        Property: convert setter can perform type conversions.
        """

        @attr.s
        class C:
            x = attr.ib(converter=str.upper, on_setattr=setters.convert)

        c = C(value)
        assert c.x == value.upper()

        new_value = value + "test"
        c.x = new_value
        assert c.x == new_value.upper()

    @given(st.integers())
    def test_convert_idempotent_converter(self, value):
        """
        Property: Applying an idempotent converter multiple times gives same result.
        """

        def abs_converter(x):
            return abs(x)

        @attr.s
        class C:
            x = attr.ib(converter=abs_converter, on_setattr=setters.convert)

        c = C(value)
        first_result = c.x
        assert first_result == abs(value)

        # Setting to the same value should give same result
        c.x = value
        assert c.x == first_result


class TestSettersCombinations:
    """
    Property-based tests for combinations of setters.
    """

    @given(st.integers(min_value=0, max_value=100))
    def test_convert_then_validate(self, value):
        """
        Property: Converting then validating ensures converted value is valid.
        """

        def double(x):
            return x * 2

        piped = setters.pipe(setters.convert, setters.validate)

        @attr.s
        class C:
            x = attr.ib(
                converter=double,
                validator=attr.validators.le(200),
                on_setattr=piped,
            )

        c = C(value)
        assert c.x == value * 2

        # Setting a value that would be valid after conversion
        c.x = 50
        assert c.x == 100

        # Setting a value that would be invalid after conversion
        with pytest.raises(ValueError):
            c.x = 101  # Would become 202, which is > 200

    @given(st.integers())
    def test_validate_then_convert_order(self, value):
        """
        Property: Order of validate and convert matters.
        """

        def double(x):
            return x * 2

        # Validate before convert
        piped1 = setters.pipe(setters.validate, setters.convert)

        @attr.s
        class C1:
            x = attr.ib(
                converter=double,
                validator=attr.validators.ge(0),
                on_setattr=piped1,
            )

        # This validates the input value (before conversion)
        if value >= 0:
            c1 = C1(value)
            assert c1.x == value * 2
        else:
            with pytest.raises(ValueError):
                C1(value)

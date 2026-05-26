# SPDX-License-Identifier: MIT

"""
Property-based tests for `attr.validators`.
"""

import re

import pytest

from hypothesis import assume, given
from hypothesis import strategies as st

import attr

from attr.validators import (
    ge,
    gt,
    in_,
    instance_of,
    le,
    lt,
    max_len,
    min_len,
    not_,
    optional,
    or_,
)


class TestComparisonValidatorProperties:
    """
    Property-based tests for comparison validators (lt, le, gt, ge).
    """

    @given(st.integers(), st.integers())
    def test_lt_validator_correctness(self, bound, value):
        """
        Property: lt validator accepts values < bound and rejects values >= bound.
        """
        validator = lt(bound)

        @attr.s
        class C:
            x = attr.ib(validator=validator)

        if value < bound:
            # Should succeed
            C(value)
        else:
            # Should fail
            with pytest.raises(ValueError):
                C(value)

    @given(st.integers(), st.integers())
    def test_le_validator_correctness(self, bound, value):
        """
        Property: le validator accepts values <= bound and rejects values > bound.
        """
        validator = le(bound)

        @attr.s
        class C:
            x = attr.ib(validator=validator)

        if value <= bound:
            # Should succeed
            C(value)
        else:
            # Should fail
            with pytest.raises(ValueError):
                C(value)

    @given(st.integers(), st.integers())
    def test_gt_validator_correctness(self, bound, value):
        """
        Property: gt validator accepts values > bound and rejects values <= bound.
        """
        validator = gt(bound)

        @attr.s
        class C:
            x = attr.ib(validator=validator)

        if value > bound:
            # Should succeed
            C(value)
        else:
            # Should fail
            with pytest.raises(ValueError):
                C(value)

    @given(st.integers(), st.integers())
    def test_ge_validator_correctness(self, bound, value):
        """
        Property: ge validator accepts values >= bound and rejects values > bound.
        """
        validator = ge(bound)

        @attr.s
        class C:
            x = attr.ib(validator=validator)

        if value >= bound:
            # Should succeed
            C(value)
        else:
            # Should fail
            with pytest.raises(ValueError):
                C(value)

    @given(st.integers())
    def test_lt_le_relationship(self, bound):
        """
        Property: For any value, if lt(bound) passes, then le(bound) passes.
        """
        # If a value passes lt(bound), it must pass le(bound)
        # We test this by checking that le accepts a superset of lt's domain
        assume(bound > -1000)  # Avoid extreme values

        test_value = bound - 1

        @attr.s
        class C1:
            x = attr.ib(validator=lt(bound))

        @attr.s
        class C2:
            x = attr.ib(validator=le(bound))

        # This should succeed for both
        C1(test_value)
        C2(test_value)

        # But bound itself should only work for le
        with pytest.raises(ValueError):
            C1(bound)
        C2(bound)  # Should succeed

    @given(st.integers())
    def test_gt_ge_relationship(self, bound):
        """
        Property: For any value, if gt(bound) passes, then ge(bound) passes.
        """
        assume(bound < 1000)  # Avoid extreme values

        test_value = bound + 1

        @attr.s
        class C1:
            x = attr.ib(validator=gt(bound))

        @attr.s
        class C2:
            x = attr.ib(validator=ge(bound))

        # This should succeed for both
        C1(test_value)
        C2(test_value)

        # But bound itself should only work for ge
        with pytest.raises(ValueError):
            C1(bound)
        C2(bound)  # Should succeed


class TestLengthValidatorProperties:
    """
    Property-based tests for length validators (min_len, max_len).
    """

    @given(st.integers(min_value=0, max_value=100), st.lists(st.integers()))
    def test_min_len_correctness(self, min_length, lst):
        """
        Property: min_len validator accepts sequences with length >= min_length.
        """
        validator = min_len(min_length)

        @attr.s
        class C:
            x = attr.ib(validator=validator)

        if len(lst) >= min_length:
            C(lst)
        else:
            with pytest.raises(ValueError):
                C(lst)

    @given(st.integers(min_value=0, max_value=100), st.lists(st.integers()))
    def test_max_len_correctness(self, max_length, lst):
        """
        Property: max_len validator accepts sequences with length <= max_length.
        """
        validator = max_len(max_length)

        @attr.s
        class C:
            x = attr.ib(validator=validator)

        if len(lst) <= max_length:
            C(lst)
        else:
            with pytest.raises(ValueError):
                C(lst)

    @given(
        st.integers(min_value=0, max_value=50),
        st.integers(min_value=0, max_value=50),
        st.lists(st.integers()),
    )
    def test_min_max_len_combined(self, min_length, max_length, lst):
        """
        Property: Combining min_len and max_len creates a range validator.
        """
        assume(min_length <= max_length)

        @attr.s
        class C:
            x = attr.ib(validator=[min_len(min_length), max_len(max_length)])

        if min_length <= len(lst) <= max_length:
            C(lst)
        else:
            with pytest.raises(ValueError):
                C(lst)

    @given(st.integers(min_value=0, max_value=100), st.text())
    def test_min_len_works_on_strings(self, min_length, s):
        """
        Property: min_len works on strings as well as lists.
        """
        validator = min_len(min_length)

        @attr.s
        class C:
            x = attr.ib(validator=validator)

        if len(s) >= min_length:
            C(s)
        else:
            with pytest.raises(ValueError):
                C(s)


class TestInValidator:
    """
    Property-based tests for in_ validator.
    """

    @given(st.lists(st.integers(), min_size=1), st.integers())
    def test_in_validator_correctness(self, options, value):
        """
        Property: in_ validator accepts values in options and rejects others.
        """
        validator = in_(options)

        @attr.s
        class C:
            x = attr.ib(validator=validator)

        if value in options:
            C(value)
        else:
            with pytest.raises(ValueError):
                C(value)

    @given(st.sets(st.integers(), min_size=1), st.integers())
    def test_in_validator_with_set(self, options, value):
        """
        Property: in_ validator works with sets.
        """
        validator = in_(options)

        @attr.s
        class C:
            x = attr.ib(validator=validator)

        if value in options:
            C(value)
        else:
            with pytest.raises(ValueError):
                C(value)

    @given(st.lists(st.integers(), min_size=1))
    def test_in_validator_accepts_all_options(self, options):
        """
        Property: in_ validator accepts all values in its options list.
        """
        validator = in_(options)

        @attr.s
        class C:
            x = attr.ib(validator=validator)

        # All options should be valid
        for opt in options:
            C(opt)


class TestInstanceOfValidator:
    """
    Property-based tests for instance_of validator.
    """

    @given(st.integers())
    def test_instance_of_int(self, value):
        """
        Property: instance_of(int) accepts integers.
        """
        validator = instance_of(int)

        @attr.s
        class C:
            x = attr.ib(validator=validator)

        C(value)

    @given(st.text())
    def test_instance_of_str(self, value):
        """
        Property: instance_of(str) accepts strings.
        """
        validator = instance_of(str)

        @attr.s
        class C:
            x = attr.ib(validator=validator)

        C(value)

    @given(st.one_of(st.integers(), st.text()))
    def test_instance_of_rejects_wrong_type(self, value):
        """
        Property: instance_of(int) rejects non-integers.
        """
        validator = instance_of(int)

        @attr.s
        class C:
            x = attr.ib(validator=validator)

        if isinstance(value, int):
            C(value)
        else:
            with pytest.raises(TypeError):
                C(value)

    @given(st.integers())
    def test_instance_of_tuple_of_types(self, value):
        """
        Property: instance_of can accept a tuple of types.
        """
        validator = instance_of((int, str))

        @attr.s
        class C:
            x = attr.ib(validator=validator)

        # Integers should be accepted
        C(value)

        # Strings should also be accepted
        C("test")

        # But not other types
        with pytest.raises(TypeError):
            C([])


class TestOptionalValidator:
    """
    Property-based tests for optional validator.
    """

    @given(st.one_of(st.none(), st.integers()))
    def test_optional_allows_none(self, value):
        """
        Property: optional validator allows None and validates non-None values.
        """
        validator = optional(instance_of(int))

        @attr.s
        class C:
            x = attr.ib(validator=validator)

        if value is None or isinstance(value, int):
            C(value)
        else:
            with pytest.raises(TypeError):
                C(value)

    @given(st.integers(min_value=0))
    def test_optional_with_comparison(self, value):
        """
        Property: optional works with comparison validators.
        """
        validator = optional(ge(0))

        @attr.s
        class C:
            x = attr.ib(validator=validator)

        # None should be accepted
        C(None)

        # Non-negative integers should be accepted
        C(value)

        # Negative integers should be rejected
        with pytest.raises(ValueError):
            C(-1)


class TestNotValidator:
    """
    Property-based tests for not_ validator.
    """

    @given(st.integers())
    def test_not_inverts_validator(self, value):
        """
        Property: not_ inverts the logic of a validator.
        """
        # Create a validator that accepts values >= 0
        positive_validator = ge(0)
        # Invert it to accept values < 0
        negative_validator = not_(positive_validator)

        @attr.s
        class C:
            x = attr.ib(validator=negative_validator)

        if value < 0:
            C(value)
        else:
            with pytest.raises(ValueError):
                C(value)

    @given(st.lists(st.integers()))
    def test_not_with_in_validator(self, value):
        """
        Property: not_ works with in_ validator.
        """
        options = [1, 2, 3]
        validator = not_(in_(options))

        @attr.s
        class C:
            x = attr.ib(validator=validator)

        if value not in options:
            C(value)
        else:
            with pytest.raises(ValueError):
                C(value)


class TestOrValidator:
    """
    Property-based tests for or_ validator.
    """

    @given(st.integers())
    def test_or_accepts_if_any_passes(self, value):
        """
        Property: or_ validator passes if any sub-validator passes.
        """
        # Accept values < 0 OR values > 10
        validator = or_(lt(0), gt(10))

        @attr.s
        class C:
            x = attr.ib(validator=validator)

        if value < 0 or value > 10:
            C(value)
        else:
            with pytest.raises(ValueError):
                C(value)

    @given(st.one_of(st.integers(), st.text()))
    def test_or_with_instance_of(self, value):
        """
        Property: or_ works with instance_of validators.
        """
        # Accept int OR str
        validator = or_(instance_of(int), instance_of(str))

        @attr.s
        class C:
            x = attr.ib(validator=validator)

        if isinstance(value, (int, str)):
            C(value)
        else:
            with pytest.raises((TypeError, ValueError)):
                C(value)


class TestValidatorComposition:
    """
    Property-based tests for validator composition.
    """

    @given(st.integers(min_value=0, max_value=100))
    def test_multiple_validators_all_must_pass(self, value):
        """
        Property: When multiple validators are specified, all must pass.
        """

        @attr.s
        class C:
            x = attr.ib(validator=[ge(0), le(100)])

        if 0 <= value <= 100:
            C(value)
        else:
            with pytest.raises(ValueError):
                C(value)

    @given(st.lists(st.integers(), max_size=50))
    def test_chained_length_and_type_validators(self, value):
        """
        Property: Type and length validators can be chained.
        """

        @attr.s
        class C:
            x = attr.ib(validator=[instance_of(list), max_len(50)])

        # Should succeed for lists with length <= 50
        C(value)

        # Should fail for non-lists
        with pytest.raises(TypeError):
            C("not a list")

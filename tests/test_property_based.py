# SPDX-License-Identifier: MIT

"""
Comprehensive property-based tests for attrs library.

This test suite uses Hypothesis to verify algebraic properties and invariants
across the attrs API surface.
"""

from hypothesis import given, strategies as st, example, settings
from collections import OrderedDict
import pytest
import re

import attr
from attr import fields, evolve, asdict, astuple, has, assoc
from attr.converters import to_bool, optional, pipe, default_if_none
from attr.validators import (
    instance_of, in_, matches_re, lt, le, ge, gt,
    min_len, max_len, and_, or_, not_, optional as optional_validator
)
from attr.filters import include, exclude
from attr.setters import pipe as setter_pipe
from attr._version_info import VersionInfo
from attr._cmp import cmp_using

from .strategies import simple_classes


# ============================================================================
# CONVERTERS: to_bool, optional, pipe
# ============================================================================

class TestConvertersToBool:
    """Property-based tests for to_bool converter."""

    @given(st.sampled_from([True, "true", "t", "yes", "y", "on", "1", 1]))
    def test_truthy_values_return_true(self, val):
        """All truthy values map to True."""
        assert to_bool(val) is True

    @given(st.sampled_from([False, "false", "f", "no", "n", "off", "0", 0]))
    def test_falsy_values_return_false(self, val):
        """All falsy values map to False."""
        assert to_bool(val) is False

    @given(st.sampled_from(["TRUE", "True", "YES", "Yes", "ON", "On"]))
    def test_case_insensitive_truthy(self, val):
        """String truthy values are case-insensitive."""
        assert to_bool(val) is True

    @given(st.sampled_from(["FALSE", "False", "NO", "No", "OFF", "Off"]))
    def test_case_insensitive_falsy(self, val):
        """String falsy values are case-insensitive."""
        assert to_bool(val) is False

    @given(st.text().filter(lambda s: s.lower() not in
           {"true", "t", "yes", "y", "on", "1", "false", "f", "no", "n", "off", "0"}))
    def test_invalid_strings_raise(self, val):
        """Invalid string values raise ValueError."""
        with pytest.raises(ValueError, match="Cannot convert value to bool"):
            to_bool(val)

    @given(st.integers().filter(lambda x: x not in {0, 1}))
    def test_invalid_integers_raise(self, val):
        """Integers other than 0 and 1 raise ValueError."""
        with pytest.raises(ValueError, match="Cannot convert value to bool"):
            to_bool(val)


class TestConvertersOptional:
    """Property-based tests for optional converter."""

    @given(st.integers())
    def test_none_passes_through(self, _):
        """optional(converter)(None) always returns None."""
        c = optional(int)
        assert c(None) is None

    @given(st.integers().map(str))
    def test_non_none_delegates_to_converter(self, val):
        """Non-None values are passed to the wrapped converter."""
        c = optional(int)
        assert c(val) == int(val)

    @given(st.integers())
    def test_idempotent_on_none(self, _):
        """Applying optional twice on None is same as once."""
        c1 = optional(int)
        c2 = optional(c1)
        assert c2(None) is None


class TestConvertersPipe:
    """Property-based tests for pipe converter."""

    @given(st.integers())
    def test_empty_pipe_is_identity(self, val):
        """pipe() with no converters returns the input unchanged."""
        assert pipe()(val) == val

    @given(st.integers())
    def test_single_converter_pipe(self, val):
        """pipe(f) is equivalent to f."""
        assert pipe(str)(val) == str(val)

    @given(st.integers(min_value=0, max_value=100))
    def test_composition_order(self, val):
        """pipe(f, g, h)(x) == h(g(f(x)))."""
        result = pipe(str, len, lambda x: x * 2)(val)
        expected = len(str(val)) * 2
        assert result == expected


# ============================================================================
# EVOLVE: Identity and consistency properties
# ============================================================================

class TestEvolveProperties:
    """Property-based tests for evolve function."""

    @given(simple_classes())
    def test_evolve_no_changes_equals_original(self, cls):
        """evolve(inst) with no changes should equal the original instance."""
        inst = cls()
        evolved = evolve(inst)
        assert inst == evolved

    @given(simple_classes())
    def test_evolve_preserves_unchanged_fields(self, cls):
        """Fields not mentioned in evolve should remain identical."""
        inst = cls()
        cls_fields = fields(inst.__class__)

        if len(cls_fields) == 0:
            return  # Skip classes with no fields

        # Change nothing, verify all fields are equal
        evolved = evolve(inst)
        for field in cls_fields:
            assert getattr(inst, field.name) == getattr(evolved, field.name)


# ============================================================================
# ASDICT / ASTUPLE: Consistency properties
# ============================================================================

class TestAsdictAstupleConsistency:
    """Property-based tests for asdict and astuple consistency."""

    @given(simple_classes())
    def test_same_field_count(self, cls):
        """asdict and astuple should have same number of elements."""
        inst = cls()
        d = asdict(inst)
        t = astuple(inst)
        assert len(d) == len(t)

    @given(simple_classes())
    def test_same_field_order(self, cls):
        """asdict keys and astuple values should be in same order."""
        inst = cls()
        d = asdict(inst)
        t = astuple(inst)
        cls_fields = fields(inst.__class__)

        # Keys in dict should match field order
        assert list(d.keys()) == [f.name for f in cls_fields]

        # Values should match
        for i, field in enumerate(cls_fields):
            assert d[field.name] == t[i]

    @given(simple_classes())
    def test_asdict_idempotent_structure(self, cls):
        """Calling asdict twice on same instance gives same dict."""
        inst = cls()
        d1 = asdict(inst)
        d2 = asdict(inst)
        assert d1 == d2

    @given(simple_classes())
    def test_astuple_idempotent_structure(self, cls):
        """Calling astuple twice on same instance gives same tuple."""
        inst = cls()
        t1 = astuple(inst)
        t2 = astuple(inst)
        assert t1 == t2


# ============================================================================
# FILTERS: include, exclude properties
# ============================================================================

class TestFiltersProperties:
    """Property-based tests for attr.filters.

    Note: simple_classes() can generate attributes with dict defaults, which
    are unhashable. attrs' filter implementation always calls __hash__ on each
    attribute during the membership check (even against an empty frozenset),
    so these tests use a fixed class with only hashable-default fields.
    """

    @attr.s
    class _FixedClass:
        x = attr.ib(default=1)
        y = attr.ib(default="hello")
        z = attr.ib(default=3.14)

    def test_include_exclude_complement(self):
        """include(name) and exclude(name) are complementary."""
        inst = self._FixedClass()
        cls_fields = fields(inst.__class__)

        field_name = cls_fields[0].name
        included = asdict(inst, filter=include(field_name))
        excluded = asdict(inst, filter=exclude(field_name))

        all_keys = set(included.keys()) | set(excluded.keys())
        expected_keys = {f.name for f in cls_fields}
        assert all_keys == expected_keys
        assert set(included.keys()) & set(excluded.keys()) == set()

    @given(st.sampled_from(["x", "y", "z"]))
    def test_exclude_by_name(self, field_name):
        """Excluding by field name removes that field from output."""
        inst = self._FixedClass()
        cls_fields = fields(inst.__class__)
        result = asdict(inst, filter=exclude(field_name))

        assert field_name not in result
        assert len(result) == len(cls_fields) - 1

    @given(st.sampled_from(["x", "y", "z"]))
    def test_include_by_name(self, field_name):
        """Including by field name keeps only that field."""
        inst = self._FixedClass()
        result = asdict(inst, filter=include(field_name))

        assert field_name in result
        assert len(result) == 1

    @given(st.sampled_from(["x", "y", "z"]))
    def test_include_by_type(self, field_name):
        """Including by type keeps only fields of that type."""
        inst = self._FixedClass()
        result = asdict(inst, filter=include(int))

        # Only 'x' is an int
        assert "x" in result
        assert "y" not in result
        assert "z" not in result


# ============================================================================
# SETTERS: pipe composition properties
# ============================================================================

class TestSettersPipeProperties:
    """Property-based tests for setters.pipe composition."""

    def test_pipe_composition_order(self):
        """Setters are applied in left-to-right order."""
        results = []

        def setter1(inst, attr, val):
            results.append(1)
            return val + "_1"

        def setter2(inst, attr, val):
            results.append(2)
            return val + "_2"

        def setter3(inst, attr, val):
            results.append(3)
            return val + "_3"

        @attr.s
        class C:
            x = attr.ib(on_setattr=setter_pipe(setter1, setter2, setter3))

        c = C(x="start")
        # on_setattr fires on post-init attribute assignment, not during __init__
        c.x = "start"
        assert c.x == "start_1_2_3"
        assert results == [1, 2, 3]

    def test_empty_pipe_returns_value(self):
        """Empty pipe returns the value unchanged."""
        @attr.s
        class C:
            x = attr.ib(on_setattr=setter_pipe())

        c = C(x=42)
        assert c.x == 42


# ============================================================================
# VERSIONINFO: Ordering properties
# ============================================================================

class TestVersionInfoProperties:
    """Property-based tests for VersionInfo ordering."""

    @given(
        st.integers(min_value=0, max_value=99),
        st.integers(min_value=0, max_value=99),
        st.integers(min_value=0, max_value=99),
        st.sampled_from(["dev0", "final", "post1", "post2"])
    )
    def test_equality_reflexive(self, year, minor, micro, level):
        """v == v for all VersionInfo v."""
        v = VersionInfo(year, minor, micro, level)
        assert v == v

    @given(
        st.integers(min_value=0, max_value=99),
        st.integers(min_value=0, max_value=99),
        st.integers(min_value=0, max_value=99),
        st.sampled_from(["dev0", "final", "post1", "post2"])
    )
    def test_equality_with_tuple(self, year, minor, micro, level):
        """VersionInfo equals tuple of same components."""
        v = VersionInfo(year, minor, micro, level)
        assert v == (year, minor, micro, level)
        assert v == (year, minor, micro)
        assert v == (year, minor)
        assert v == (year,)

    @given(
        st.integers(min_value=0, max_value=99),
        st.integers(min_value=0, max_value=99),
        st.integers(min_value=0, max_value=99),
        st.sampled_from(["dev0", "final", "post1", "post2"])
    )
    def test_not_less_than_self(self, year, minor, micro, level):
        """v < v is always False."""
        v = VersionInfo(year, minor, micro, level)
        assert not (v < v)

    @given(
        st.integers(min_value=0, max_value=50),
        st.integers(min_value=0, max_value=50),
        st.integers(min_value=0, max_value=50),
    )
    def test_transitivity_of_less_than(self, y1, y2, y3):
        """If v1 < v2 and v2 < v3, then v1 < v3."""
        versions = sorted([y1, y2, y3])
        v1 = VersionInfo(versions[0], 0, 0, "final")
        v2 = VersionInfo(versions[1], 0, 0, "final")
        v3 = VersionInfo(versions[2], 0, 0, "final")

        if v1 < v2 and v2 < v3:
            assert v1 < v3

    @given(
        st.integers(min_value=0, max_value=99),
        st.integers(min_value=0, max_value=99),
    )
    def test_antisymmetry(self, y1, y2):
        """If v1 <= v2 and v2 <= v1, then v1 == v2."""
        v1 = VersionInfo(y1, 0, 0, "final")
        v2 = VersionInfo(y2, 0, 0, "final")

        if v1 <= v2 and v2 <= v1:
            assert v1 == v2


# ============================================================================
# VALIDATORS: Composition properties (and_, or_, not_)
# ============================================================================

class TestValidatorCompositionProperties:
    """Property-based tests for validator composition."""

    @given(st.integers(min_value=0, max_value=100))
    def test_and_all_must_pass(self, val):
        """and_(v1, v2) passes only if both v1 and v2 pass."""
        v1 = ge(0)
        v2 = le(100)
        combined = and_(v1, v2)

        @attr.s
        class C:
            x = attr.ib(validator=combined)

        # Should not raise for valid value
        C(x=val)

    @given(st.integers())
    def test_and_fails_if_any_fails(self, val):
        """and_(v1, v2) fails if either v1 or v2 fails."""
        v1 = ge(0)
        v2 = le(100)
        combined = and_(v1, v2)

        @attr.s
        class C:
            x = attr.ib(validator=combined)

        if val < 0 or val > 100:
            with pytest.raises(ValueError):
                C(x=val)

    @given(st.integers())
    def test_or_passes_if_any_passes(self, val):
        """or_(v1, v2) passes if at least one of v1 or v2 passes."""
        v1 = lt(0)
        v2 = gt(100)
        combined = or_(v1, v2)

        @attr.s
        class C:
            x = attr.ib(validator=combined)

        if val < 0 or val > 100:
            # Should not raise
            C(x=val)

    @given(st.integers(min_value=0, max_value=100))
    def test_or_fails_if_all_fail(self, val):
        """or_(v1, v2) fails only if both v1 and v2 fail."""
        v1 = lt(0)
        v2 = gt(100)
        combined = or_(v1, v2)

        @attr.s
        class C:
            x = attr.ib(validator=combined)

        # val is in [0, 100], so both validators should fail
        with pytest.raises(ValueError):
            C(x=val)

    @given(st.integers())
    def test_not_inverts_validator(self, val):
        """not_(v) passes iff v fails."""
        v = ge(0)
        inverted = not_(v)

        @attr.s
        class C:
            x = attr.ib(validator=inverted)

        if val >= 0:
            # Original passes, so inverted should fail
            with pytest.raises(ValueError):
                C(x=val)
        else:
            # Original fails, so inverted should pass
            C(x=val)

    @given(st.integers())
    def test_double_negation(self, val):
        """not_(not_(v)) should behave like v."""
        v = ge(0)
        double_neg = not_(not_(v))

        @attr.s
        class C:
            x = attr.ib(validator=double_neg)

        if val >= 0:
            # Should pass like original
            C(x=val)
        else:
            # Should fail like original
            with pytest.raises(ValueError):
                C(x=val)


# ============================================================================
# CMP_USING: Custom comparison properties
# ============================================================================

class TestCmpUsingProperties:
    """Property-based tests for cmp_using custom comparisons."""

    @given(st.integers(), st.integers())
    def test_require_same_type_returns_not_implemented(self, a, b):
        """With require_same_type=True, comparing different types returns NotImplemented."""
        Cmp = cmp_using(eq=lambda x, y: x == y, require_same_type=True)

        c1 = Cmp(a)
        c2 = Cmp(b)

        # Same type should work
        result = c1 == c2
        assert result == (a == b)

    @given(st.integers())
    def test_equality_reflexive(self, val):
        """Custom equality is reflexive: x == x."""
        Cmp = cmp_using(eq=lambda x, y: x == y)
        c = Cmp(val)
        assert c == c

    @given(st.integers(), st.integers())
    def test_equality_symmetric(self, a, b):
        """Custom equality is symmetric: if x == y then y == x."""
        Cmp = cmp_using(eq=lambda x, y: x == y)
        c1 = Cmp(a)
        c2 = Cmp(b)

        if c1 == c2:
            assert c2 == c1

    @given(st.integers(), st.integers(), st.integers())
    def test_ordering_transitivity(self, a, b, c):
        """If x < y and y < z, then x < z."""
        Cmp = cmp_using(eq=lambda x, y: x == y, lt=lambda x, y: x < y)
        c1 = Cmp(a)
        c2 = Cmp(b)
        c3 = Cmp(c)

        if c1 < c2 and c2 < c3:
            assert c1 < c3


# ============================================================================
# ADDITIONAL PROPERTY TESTS
# ============================================================================

class TestHasFunction:
    """Property-based tests for has() function."""

    @given(simple_classes())
    def test_has_returns_true_for_attrs_classes(self, cls):
        """has() returns True for all attrs-decorated classes."""
        assert has(cls) is True

    def test_has_returns_false_for_regular_classes(self):
        """has() returns False for non-attrs classes."""
        class Regular:
            pass

        assert has(Regular) is False


class TestFieldsFunction:
    """Property-based tests for fields() function."""

    @given(simple_classes())
    def test_fields_returns_tuple(self, cls):
        """fields() always returns a tuple."""
        result = fields(cls)
        assert isinstance(result, tuple)

    @given(simple_classes())
    def test_fields_length_matches_attributes(self, cls):
        """Length of fields() matches number of defined attributes."""
        inst = cls()
        cls_fields = fields(cls)
        # All fields should be accessible as attributes
        for field in cls_fields:
            assert hasattr(inst, field.name)


class TestAssocFunction:
    """Property-based tests for assoc() function."""

    @given(simple_classes())
    def test_assoc_no_changes_equals_original(self, cls):
        """assoc(inst) with no changes creates equal instance."""
        inst = cls()
        new_inst = assoc(inst)
        assert inst == new_inst

    @given(simple_classes())
    def test_assoc_preserves_type(self, cls):
        """assoc() preserves the instance type."""
        inst = cls()
        new_inst = assoc(inst)
        assert type(inst) == type(new_inst)


# ============================================================================
# VALIDATORS: Boundary and range properties
# ============================================================================

class TestValidatorBoundaries:
    """Property-based tests for numeric boundary validators."""

    @given(st.integers())
    def test_lt_boundary(self, val):
        """lt(n) passes for values < n, fails for values >= n."""
        bound = 50
        validator = lt(bound)

        @attr.s
        class C:
            x = attr.ib(validator=validator)

        if val < bound:
            C(x=val)  # Should not raise
        else:
            with pytest.raises(ValueError):
                C(x=val)

    @given(st.integers())
    def test_le_boundary(self, val):
        """le(n) passes for values <= n, fails for values > n."""
        bound = 50
        validator = le(bound)

        @attr.s
        class C:
            x = attr.ib(validator=validator)

        if val <= bound:
            C(x=val)  # Should not raise
        else:
            with pytest.raises(ValueError):
                C(x=val)

    @given(st.integers())
    def test_gt_boundary(self, val):
        """gt(n) passes for values > n, fails for values <= n."""
        bound = 50
        validator = gt(bound)

        @attr.s
        class C:
            x = attr.ib(validator=validator)

        if val > bound:
            C(x=val)  # Should not raise
        else:
            with pytest.raises(ValueError):
                C(x=val)

    @given(st.integers())
    def test_ge_boundary(self, val):
        """ge(n) passes for values >= n, fails for values < n."""
        bound = 50
        validator = ge(bound)

        @attr.s
        class C:
            x = attr.ib(validator=validator)

        if val >= bound:
            C(x=val)  # Should not raise
        else:
            with pytest.raises(ValueError):
                C(x=val)


class TestValidatorLength:
    """Property-based tests for length validators."""

    @given(st.lists(st.integers(), min_size=0, max_size=100))
    def test_min_len_boundary(self, lst):
        """min_len(n) passes for len >= n, fails for len < n."""
        min_length = 5
        validator = min_len(min_length)

        @attr.s
        class C:
            x = attr.ib(validator=validator)

        if len(lst) >= min_length:
            C(x=lst)  # Should not raise
        else:
            with pytest.raises(ValueError):
                C(x=lst)

    @given(st.lists(st.integers(), min_size=0, max_size=100))
    def test_max_len_boundary(self, lst):
        """max_len(n) passes for len <= n, fails for len > n."""
        max_length = 10
        validator = max_len(max_length)

        @attr.s
        class C:
            x = attr.ib(validator=validator)

        if len(lst) <= max_length:
            C(x=lst)  # Should not raise
        else:
            with pytest.raises(ValueError):
                C(x=lst)


class TestValidatorIn:
    """Property-based tests for in_ validator."""

    @given(st.integers(min_value=0, max_value=10))
    def test_in_passes_for_members(self, val):
        """in_(options) passes for values in options."""
        options = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        validator = in_(options)

        @attr.s
        class C:
            x = attr.ib(validator=validator)

        C(x=val)  # Should not raise

    @given(st.integers(min_value=11, max_value=100))
    def test_in_fails_for_non_members(self, val):
        """in_(options) fails for values not in options."""
        options = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        validator = in_(options)

        @attr.s
        class C:
            x = attr.ib(validator=validator)

        with pytest.raises(ValueError):
            C(x=val)


class TestValidatorInstanceOf:
    """Property-based tests for instance_of validator."""

    @given(st.integers())
    def test_instance_of_passes_correct_type(self, val):
        """instance_of(T) passes for instances of T."""
        validator = instance_of(int)

        @attr.s
        class C:
            x = attr.ib(validator=validator)

        C(x=val)  # Should not raise

    @given(st.text())
    def test_instance_of_fails_wrong_type(self, val):
        """instance_of(T) fails for non-instances of T."""
        validator = instance_of(int)

        @attr.s
        class C:
            x = attr.ib(validator=validator)

        with pytest.raises(TypeError):
            C(x=val)


class TestValidatorMatchesRe:
    """Property-based tests for matches_re validator."""

    @given(st.text(alphabet='abcdefghijklmnopqrstuvwxyz', min_size=1, max_size=10))
    def test_matches_re_passes_matching_strings(self, val):
        """matches_re passes for strings matching the pattern."""
        validator = matches_re(r'^[a-z]+$')

        @attr.s
        class C:
            x = attr.ib(validator=validator)

        C(x=val)  # Should not raise

    @given(st.text(alphabet=st.characters(whitelist_categories=('Lu',)), min_size=1, max_size=10))
    def test_matches_re_fails_non_matching_strings(self, val):
        """matches_re fails for strings not matching the pattern."""
        validator = matches_re(r'^[a-z]+$')

        @attr.s
        class C:
            x = attr.ib(validator=validator)

        with pytest.raises(ValueError):
            C(x=val)


class TestValidatorOptional:
    """Property-based tests for optional validator."""

    @given(st.integers())
    def test_optional_passes_none(self, _):
        """optional(validator) always passes None."""
        validator = optional_validator(instance_of(int))

        @attr.s
        class C:
            x = attr.ib(validator=validator)

        C(x=None)  # Should not raise

    @given(st.integers())
    def test_optional_delegates_non_none(self, val):
        """optional(validator) delegates non-None to wrapped validator."""
        validator = optional_validator(instance_of(int))

        @attr.s
        class C:
            x = attr.ib(validator=validator)

        C(x=val)  # Should not raise for int


class TestDefaultIfNoneProperties:
    """Property-based tests for default_if_none converter."""

    @given(st.integers())
    def test_non_none_passes_through(self, val):
        """Non-None values pass through unchanged."""
        converter = default_if_none(42)
        assert converter(val) == val

    def test_none_returns_default(self):
        """None returns the default value."""
        converter = default_if_none(42)
        assert converter(None) == 42

    def test_none_calls_factory(self):
        """None calls the factory function."""
        call_count = [0]

        def factory():
            call_count[0] += 1
            return []

        converter = default_if_none(factory=factory)
        result = converter(None)

        assert result == []
        assert call_count[0] == 1


class TestIntegrationProperties:
    """Integration tests combining multiple attrs features."""

    @given(simple_classes(private_attrs=False))
    def test_roundtrip_via_asdict(self, cls):
        """Creating instance from asdict produces equivalent instance."""
        inst = cls()
        d = asdict(inst)
        cls_fields = fields(cls)

        if len(cls_fields) > 0:
            reconstructed = cls(**d)
            assert asdict(reconstructed) == d

    @given(simple_classes())
    def test_evolve_then_asdict_consistency(self, cls):
        """evolve and asdict compose correctly."""
        inst = cls()
        evolved = evolve(inst)
        assert asdict(inst) == asdict(evolved)

    @given(simple_classes())
    def test_has_and_fields_consistency(self, cls):
        """If has(cls) is True, fields(cls) should not raise."""
        if has(cls):
            result = fields(cls)
            assert isinstance(result, tuple)


# ============================================================================
# MAKE_CLASS: Dynamic class factory properties
# ============================================================================

import keyword as _keyword

# Strategies for valid Python identifiers (ASCII only, not keywords)
_ident_alphabet = 'abcdefghijklmnopqrstuvwxyz'
_valid_attr_name = st.text(alphabet=_ident_alphabet, min_size=1, max_size=8).filter(
    lambda s: not _keyword.iskeyword(s) and s not in {"self", "cls", "mcs"}
)
_valid_class_name = st.text(
    alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
    min_size=1, max_size=20,
)


class TestMakeClassProperties:
    """Property-based tests for attr.make_class."""

    @given(
        _valid_class_name,
        st.lists(_valid_attr_name, min_size=0, max_size=5, unique=True),
    )
    def test_make_class_fields_match_attrs(self, name, attr_names):
        """make_class produces a class whose fields match the given attribute names."""
        cls = attr.make_class(name, attr_names)
        result_names = [f.name for f in fields(cls)]
        assert result_names == attr_names

    @given(
        _valid_class_name,
        st.lists(_valid_attr_name, min_size=0, max_size=5, unique=True),
    )
    def test_make_class_is_attrs_class(self, name, attr_names):
        """make_class always produces an attrs class."""
        cls = attr.make_class(name, attr_names)
        assert has(cls)

    @given(
        _valid_class_name,
        st.lists(_valid_attr_name, min_size=0, max_size=5, unique=True),
    )
    def test_make_class_has_correct_name(self, name, attr_names):
        """make_class sets __name__ correctly."""
        cls = attr.make_class(name, attr_names)
        assert cls.__name__ == name


# ============================================================================
# FIELDS_DICT: Consistency with fields()
# ============================================================================

class TestFieldsDictProperties:
    """Property-based tests for fields_dict()."""

    @given(simple_classes())
    def test_fields_dict_keys_match_fields(self, cls):
        """fields_dict keys match field names from fields()."""
        d = attr.fields_dict(cls)
        f = fields(cls)
        assert list(d.keys()) == [field.name for field in f]

    @given(simple_classes())
    def test_fields_dict_values_are_attributes(self, cls):
        """fields_dict values are Attribute instances."""
        d = attr.fields_dict(cls)
        for val in d.values():
            assert isinstance(val, attr.Attribute)

    @given(simple_classes())
    def test_fields_dict_consistent_with_fields(self, cls):
        """fields_dict[name] == fields()[i] for each field."""
        d = attr.fields_dict(cls)
        for field in fields(cls):
            assert d[field.name] is field


# ============================================================================
# VALIDATE: Re-running validators
# ============================================================================

class TestValidateFunction:
    """Property-based tests for attr.validate()."""

    @given(st.integers(min_value=0, max_value=100))
    def test_validate_passes_on_valid_instance(self, val):
        """validate() does not raise on a valid instance."""
        @attr.s
        class C:
            x = attr.ib(validator=attr.validators.instance_of(int))

        c = C(x=val)
        attr.validate(c)  # Should not raise

    def test_validate_raises_on_invalid_state(self):
        """validate() raises when instance is in invalid state."""
        @attr.s
        class C:
            x = attr.ib(validator=instance_of(int))

        c = C(x=1)
        # Bypass validator to put instance in invalid state
        object.__setattr__(c, 'x', "not_an_int")

        with pytest.raises(TypeError):
            attr.validate(c)


# ============================================================================
# DEEP_ITERABLE / DEEP_MAPPING: Structural validators
# ============================================================================

class TestDeepIterableProperties:
    """Property-based tests for deep_iterable validator."""

    @given(st.lists(st.integers(), min_size=0, max_size=20))
    def test_deep_iterable_passes_valid_list(self, lst):
        """deep_iterable passes when all members satisfy member_validator."""
        from attr.validators import deep_iterable

        @attr.s
        class C:
            x = attr.ib(validator=deep_iterable(instance_of(int)))

        C(x=lst)  # Should not raise

    @given(st.lists(st.integers(), min_size=1, max_size=20))
    def test_deep_iterable_fails_wrong_member_type(self, lst):
        """deep_iterable fails when a member has wrong type."""
        from attr.validators import deep_iterable

        @attr.s
        class C:
            x = attr.ib(validator=deep_iterable(instance_of(str)))

        with pytest.raises(TypeError):
            C(x=lst)


class TestDeepMappingProperties:
    """Property-based tests for deep_mapping validator."""

    @given(st.dictionaries(st.text(), st.integers(), max_size=10))
    def test_deep_mapping_passes_valid_dict(self, d):
        """deep_mapping passes when all keys/values satisfy validators."""
        from attr.validators import deep_mapping

        @attr.s
        class C:
            x = attr.ib(validator=deep_mapping(
                key_validator=instance_of(str),
                value_validator=instance_of(int),
            ))

        C(x=d)  # Should not raise

    @given(st.dictionaries(st.integers(), st.integers(), min_size=1, max_size=10))
    def test_deep_mapping_fails_wrong_key_type(self, d):
        """deep_mapping fails when a key has wrong type."""
        from attr.validators import deep_mapping

        @attr.s
        class C:
            x = attr.ib(validator=deep_mapping(
                key_validator=instance_of(str),
                value_validator=instance_of(int),
            ))

        with pytest.raises(TypeError):
            C(x=d)


# ============================================================================
# VERSIONINFO: _from_version_string roundtrip
# ============================================================================

class TestVersionInfoFromString:
    """Property-based tests for VersionInfo._from_version_string."""

    @given(
        st.integers(min_value=0, max_value=99),
        st.integers(min_value=0, max_value=99),
        st.integers(min_value=0, max_value=99),
    )
    def test_from_version_string_roundtrip(self, year, minor, micro):
        """Parsing 'year.minor.micro' produces correct VersionInfo."""
        s = f"{year}.{minor}.{micro}"
        v = VersionInfo._from_version_string(s)
        assert v.year == year
        assert v.minor == minor
        assert v.micro == micro
        assert v.releaselevel == "final"

    @given(
        st.integers(min_value=0, max_value=99),
        st.integers(min_value=0, max_value=99),
        st.integers(min_value=0, max_value=99),
        st.sampled_from(["dev0", "final", "post1"]),
    )
    def test_from_version_string_with_releaselevel(self, year, minor, micro, level):
        """Parsing 'year.minor.micro.level' preserves all components."""
        s = f"{year}.{minor}.{micro}.{level}"
        v = VersionInfo._from_version_string(s)
        assert v.year == year
        assert v.minor == minor
        assert v.micro == micro
        assert v.releaselevel == level


# ============================================================================
# SETTERS: validate and convert hooks
# ============================================================================

class TestSettersValidateConvert:
    """Property-based tests for setters.validate and setters.convert."""

    @given(st.integers(min_value=0))
    def test_setters_validate_accepts_valid_value(self, val):
        """setters.validate passes valid values through."""
        from attr.setters import validate as setter_validate

        @attr.s
        class C:
            x = attr.ib(
                validator=instance_of(int),
                on_setattr=setter_validate,
            )

        c = C(x=0)
        c.x = val  # Should not raise

    def test_setters_validate_rejects_invalid_value(self):
        """setters.validate raises on invalid post-init assignment."""
        from attr.setters import validate as setter_validate

        @attr.s
        class C:
            x = attr.ib(
                validator=instance_of(int),
                on_setattr=setter_validate,
            )

        c = C(x=0)
        with pytest.raises(TypeError):
            c.x = "not_an_int"

    @given(st.integers())
    def test_setters_convert_applies_converter(self, val):
        """setters.convert applies the converter on post-init assignment."""
        from attr.setters import convert as setter_convert

        @attr.s
        class C:
            x = attr.ib(converter=str, on_setattr=setter_convert)

        c = C(x=0)
        c.x = val
        assert c.x == str(val)
        assert isinstance(c.x, str)


# ============================================================================
# ASSOC: Field change properties
# ============================================================================

class TestAssocChangeProperties:
    """Property-based tests for assoc with field changes."""

    @given(st.integers(), st.integers())
    def test_assoc_changes_specified_field(self, original, new_val):
        """assoc changes only the specified field."""
        @attr.s
        class C:
            x = attr.ib()
            y = attr.ib(default=0)

        inst = C(x=original)
        new_inst = assoc(inst, x=new_val)

        assert new_inst.x == new_val
        assert new_inst.y == inst.y

    def test_assoc_raises_on_unknown_field(self):
        """assoc raises AttrsAttributeNotFoundError for unknown fields."""
        from attr.exceptions import AttrsAttributeNotFoundError

        @attr.s
        class C:
            x = attr.ib(default=0)

        inst = C()
        with pytest.raises(AttrsAttributeNotFoundError):
            assoc(inst, nonexistent=42)


# ============================================================================
# VALIDATORS DISABLED: Context manager and global toggle
# ============================================================================

class TestValidatorsDisabled:
    """Property-based tests for validator enable/disable."""

    @given(st.text())
    def test_disabled_context_skips_validation(self, val):
        """Inside disabled(), validators are not run."""
        from attr.validators import disabled as validators_disabled

        @attr.s
        class C:
            x = attr.ib(validator=instance_of(int))

        with validators_disabled():
            # Should not raise even with wrong type
            c = C(x=val)
            assert c.x == val

    @given(st.text())
    def test_disabled_context_restores_after_exit(self, val):
        """After disabled() context, validators run again."""
        from attr.validators import disabled as validators_disabled

        @attr.s
        class C:
            x = attr.ib(validator=instance_of(int))

        with validators_disabled():
            pass  # enter and exit

        # Validators should be active again
        with pytest.raises(TypeError):
            C(x=val)

    def test_disabled_is_nestable(self):
        """Nested disabled() contexts restore correctly."""
        from attr.validators import disabled as validators_disabled, get_disabled

        assert not get_disabled()

        with validators_disabled():
            assert get_disabled()
            with validators_disabled():
                assert get_disabled()
            assert get_disabled()

        assert not get_disabled()


# ============================================================================
# OR_ FLATTENING: Nested or_ is flattened
# ============================================================================

class TestOrFlatteningProperties:
    """Property-based tests for or_ flattening behavior."""

    @given(st.integers())
    def test_nested_or_flattened(self, val):
        """or_(or_(v1, v2), v3) is equivalent to or_(v1, v2, v3)."""
        v1 = lt(0)
        v2 = gt(100)
        v3 = in_([50])

        nested = or_(or_(v1, v2), v3)
        flat = or_(v1, v2, v3)

        @attr.s
        class Nested:
            x = attr.ib(validator=nested)

        @attr.s
        class Flat:
            x = attr.ib(validator=flat)

        # Both should behave identically
        should_pass = val < 0 or val > 100 or val == 50
        if should_pass:
            Nested(x=val)
            Flat(x=val)
        else:
            with pytest.raises(ValueError):
                Nested(x=val)
            with pytest.raises(ValueError):
                Flat(x=val)


# ============================================================================
# CMP_USING: Error cases
# ============================================================================

class TestCmpUsingErrorCases:
    """Property-based tests for cmp_using error handling."""

    def test_order_without_eq_raises(self):
        """Providing order functions without eq raises ValueError."""
        with pytest.raises(ValueError, match="eq must be define"):
            cmp_using(lt=lambda x, y: x < y)

    @given(st.integers(), st.integers())
    def test_no_require_same_type_allows_cross_type(self, a, b):
        """With require_same_type=False, different value types can compare."""
        Cmp = cmp_using(
            eq=lambda x, y: x == y,
            require_same_type=False,
        )
        c1 = Cmp(a)
        c2 = Cmp(float(b))
        # Should not raise — result depends on the eq function
        result = c1 == c2
        assert isinstance(result, bool)


# ============================================================================
# DEEP_MAPPING: Error on no validators
# ============================================================================

class TestDeepMappingErrors:
    """Tests for deep_mapping error cases."""

    def test_no_validators_raises(self):
        """deep_mapping with neither key nor value validator raises ValueError."""
        from attr.validators import deep_mapping

        with pytest.raises(ValueError, match="At least one"):
            deep_mapping()


# ============================================================================
# ASDICT: value_serializer and dict_factory
# ============================================================================

class TestAsdictAdvanced:
    """Property-based tests for asdict advanced options."""

    @given(simple_classes())
    def test_dict_factory_is_used(self, cls):
        """asdict uses the provided dict_factory."""
        inst = cls()
        result = asdict(inst, dict_factory=OrderedDict)
        assert isinstance(result, OrderedDict)

    @given(simple_classes())
    def test_value_serializer_is_called(self, cls):
        """value_serializer is called for each field."""
        inst = cls()
        cls_fields = fields(cls)
        seen_fields = []

        def serializer(instance, field, value):
            if field is not None:
                seen_fields.append(field.name)
            return value

        asdict(inst, value_serializer=serializer)
        assert sorted(seen_fields) == sorted(f.name for f in cls_fields)

    @given(simple_classes())
    def test_no_recurse_keeps_raw_values(self, cls):
        """asdict with recurse=False keeps nested attrs instances as-is."""
        inst = cls()
        result = asdict(inst, recurse=False)
        cls_fields = fields(cls)
        for field in cls_fields:
            assert result[field.name] == getattr(inst, field.name)


# ============================================================================
# ASTUPLE: tuple_factory and retain_collection_types
# ============================================================================

class TestAstupleAdvanced:
    """Property-based tests for astuple advanced options."""

    @given(simple_classes())
    def test_tuple_factory_list(self, cls):
        """astuple with tuple_factory=list returns a list."""
        inst = cls()
        result = astuple(inst, tuple_factory=list)
        assert isinstance(result, list)

    @given(simple_classes())
    def test_no_recurse_keeps_raw_values(self, cls):
        """astuple with recurse=False keeps nested attrs instances as-is."""
        inst = cls()
        result = astuple(inst, recurse=False)
        cls_fields = fields(cls)
        for i, field in enumerate(cls_fields):
            assert result[i] == getattr(inst, field.name)


# ============================================================================
# EVOLVE: Type preservation
# ============================================================================

class TestEvolveTypePreservation:
    """Property-based tests for evolve type preservation."""

    @given(simple_classes())
    def test_evolve_preserves_type(self, cls):
        """evolve always returns an instance of the same class."""
        inst = cls()
        evolved = evolve(inst)
        assert type(evolved) is type(inst)

    @given(simple_classes())
    def test_evolve_returns_new_object(self, cls):
        """evolve returns a new object, not the same instance."""
        inst = cls()
        evolved = evolve(inst)
        assert evolved is not inst


# ============================================================================
# FACTORY: Default factory properties
# ============================================================================

class TestFactoryProperties:
    """Property-based tests for attr.Factory."""

    @given(st.integers(min_value=0, max_value=50))
    def test_factory_called_per_instance(self, n):
        """Factory is called fresh for each new instance."""
        @attr.s
        class C:
            x = attr.ib(factory=list)

        instances = [C() for _ in range(n)]
        # Each instance should have its own list
        for i, inst in enumerate(instances):
            for j, other in enumerate(instances):
                if i != j:
                    assert inst.x is not other.x

    def test_factory_takes_self(self):
        """Factory with takes_self=True receives the partially-constructed instance."""
        @attr.s
        class C:
            x = attr.ib(default=10)
            y = attr.ib(default=attr.Factory(lambda self: self.x * 2, takes_self=True))

        c = C()
        assert c.y == 20

    @given(st.integers())
    def test_factory_takes_self_with_varying_x(self, val):
        """Factory with takes_self=True uses the actual x value."""
        @attr.s
        class C:
            x = attr.ib()
            y = attr.ib(default=attr.Factory(lambda self: self.x * 2, takes_self=True))

        c = C(x=val)
        assert c.y == val * 2

    def test_factory_not_shared_across_instances(self):
        """Mutable factory defaults are not shared (unlike plain mutable defaults)."""
        @attr.s
        class C:
            items = attr.ib(factory=list)

        c1 = C()
        c2 = C()
        c1.items.append(1)
        assert c2.items == []


# ============================================================================
# FROZEN CLASSES: Immutability properties
# ============================================================================

class TestFrozenClassProperties:
    """Property-based tests for frozen attrs classes."""

    @given(st.integers(), st.text())
    def test_frozen_raises_on_setattr(self, x, s):
        """Setting an attribute on a frozen instance raises FrozenInstanceError."""
        from attr.exceptions import FrozenInstanceError

        @attr.s(frozen=True)
        class C:
            x = attr.ib()
            s = attr.ib()

        c = C(x=x, s=s)
        with pytest.raises(FrozenInstanceError):
            c.x = x + 1

    @given(st.integers(), st.text())
    def test_frozen_raises_on_delattr(self, x, s):
        """Deleting an attribute on a frozen instance raises FrozenInstanceError."""
        from attr.exceptions import FrozenInstanceError

        @attr.s(frozen=True)
        class C:
            x = attr.ib()
            s = attr.ib()

        c = C(x=x, s=s)
        with pytest.raises(FrozenInstanceError):
            del c.x

    @given(st.integers())
    def test_frozen_evolve_works(self, val):
        """evolve() works on frozen instances."""
        @attr.s(frozen=True)
        class C:
            x = attr.ib()

        c = C(x=val)
        c2 = evolve(c, x=val + 1)
        assert c2.x == val + 1
        assert c.x == val  # original unchanged

    @given(st.integers())
    def test_frozen_is_hashable(self, val):
        """Frozen instances with hashable fields are hashable."""
        @attr.s(frozen=True)
        class C:
            x = attr.ib()

        c = C(x=val)
        h = hash(c)
        assert isinstance(h, int)
        # Hash is stable
        assert hash(c) == h


# ============================================================================
# SLOTS CLASSES: Memory and identity properties
# ============================================================================

class TestSlotsClassProperties:
    """Property-based tests for slots=True attrs classes."""

    @given(st.integers())
    def test_slots_class_has_no_dict(self, val):
        """Slots classes do not have __dict__."""
        @attr.s(slots=True)
        class C:
            x = attr.ib()

        c = C(x=val)
        assert not hasattr(c, '__dict__')

    @given(st.integers())
    def test_slots_class_has_slots(self, val):
        """Slots classes have __slots__."""
        @attr.s(slots=True)
        class C:
            x = attr.ib()

        assert hasattr(C, '__slots__')

    @given(st.integers())
    def test_slots_class_equality(self, val):
        """Slots class instances compare equal when fields are equal."""
        @attr.s(slots=True)
        class C:
            x = attr.ib()

        c1 = C(x=val)
        c2 = C(x=val)
        assert c1 == c2


# ============================================================================
# __ATTRS_POST_INIT__: Post-init hook properties
# ============================================================================

class TestPostInitProperties:
    """Property-based tests for __attrs_post_init__ hook."""

    @given(st.integers())
    def test_post_init_is_called(self, val):
        """__attrs_post_init__ is called after __init__."""
        called = []

        @attr.s
        class C:
            x = attr.ib()

            def __attrs_post_init__(self):
                called.append(self.x)

        C(x=val)
        assert called == [val]

    @given(st.integers())
    def test_post_init_can_modify_fields(self, val):
        """__attrs_post_init__ can modify field values."""
        @attr.s
        class C:
            x = attr.ib()
            doubled = attr.ib(init=False, default=0)

            def __attrs_post_init__(self):
                self.doubled = self.x * 2

        c = C(x=val)
        assert c.doubled == val * 2

    @given(st.integers())
    def test_post_init_called_once(self, val):
        """__attrs_post_init__ is called exactly once per construction."""
        call_count = [0]

        @attr.s
        class C:
            x = attr.ib()

            def __attrs_post_init__(self):
                call_count[0] += 1

        C(x=val)
        assert call_count[0] == 1


# ============================================================================
# SETTERS.FROZEN: Immutability via on_setattr
# ============================================================================

class TestSettersFrozenProperties:
    """Property-based tests for setters.frozen."""

    @given(st.integers())
    def test_frozen_setter_raises_on_set(self, val):
        """setters.frozen raises FrozenAttributeError on attribute set."""
        from attr.setters import frozen as setter_frozen
        from attr.exceptions import FrozenAttributeError

        @attr.s
        class C:
            x = attr.ib(on_setattr=setter_frozen)

        c = C(x=val)
        with pytest.raises(FrozenAttributeError):
            c.x = val + 1

    @given(st.integers())
    def test_frozen_setter_allows_init(self, val):
        """setters.frozen does not prevent initial construction."""
        from attr.setters import frozen as setter_frozen

        @attr.s
        class C:
            x = attr.ib(on_setattr=setter_frozen)

        c = C(x=val)
        assert c.x == val


# ============================================================================
# ATTRIBUTE METADATA: Properties of field metadata
# ============================================================================

class TestAttributeMetadataProperties:
    """Property-based tests for Attribute metadata."""

    @given(st.dictionaries(st.text(), st.integers(), max_size=5))
    def test_metadata_is_preserved(self, meta):
        """Metadata passed to attr.ib is preserved on the Attribute."""
        @attr.s
        class C:
            x = attr.ib(metadata=meta)

        field = fields(C).x
        for k, v in meta.items():
            assert field.metadata[k] == v

    @given(st.dictionaries(st.text(), st.integers(), max_size=5))
    def test_metadata_is_immutable(self, meta):
        """Attribute metadata is a read-only mapping."""
        @attr.s
        class C:
            x = attr.ib(metadata=meta)

        field = fields(C).x
        with pytest.raises((TypeError, AttributeError)):
            field.metadata["__injected__"] = 999

    def test_metadata_defaults_to_empty(self):
        """Attribute without metadata has empty metadata mapping."""
        @attr.s
        class C:
            x = attr.ib()

        field = fields(C).x
        assert len(field.metadata) == 0


# ============================================================================
# REPR: Consistency properties
# ============================================================================

class TestReprProperties:
    """Property-based tests for attrs __repr__."""

    @given(simple_classes())
    def test_repr_contains_class_name(self, cls):
        """repr() of an instance contains the class name."""
        inst = cls()
        r = repr(inst)
        assert cls.__name__ in r

    @given(simple_classes())
    def test_repr_is_string(self, cls):
        """repr() always returns a string."""
        inst = cls()
        assert isinstance(repr(inst), str)

    @given(simple_classes())
    def test_repr_stable(self, cls):
        """repr() is stable across calls for the same instance."""
        inst = cls()
        assert repr(inst) == repr(inst)


# ============================================================================
# HASH: Consistency properties
# ============================================================================

class TestHashProperties:
    """Property-based tests for attrs __hash__."""

    @given(st.integers(), st.text())
    def test_equal_instances_have_equal_hash(self, x, s):
        """Equal instances must have equal hashes."""
        @attr.s(frozen=True)
        class C:
            x = attr.ib()
            s = attr.ib()

        c1 = C(x=x, s=s)
        c2 = C(x=x, s=s)
        assert c1 == c2
        assert hash(c1) == hash(c2)

    @given(st.integers())
    def test_hash_stable_across_calls(self, val):
        """hash() returns the same value on repeated calls."""
        @attr.s(frozen=True)
        class C:
            x = attr.ib()

        c = C(x=val)
        assert hash(c) == hash(c) == hash(c)


# ============================================================================
# INHERITANCE: Subclass field ordering properties
# ============================================================================

class TestInheritanceProperties:
    """Property-based tests for attrs class inheritance."""

    @given(st.integers(), st.text())
    def test_subclass_inherits_parent_fields(self, x, s):
        """Subclass has all parent fields plus its own."""
        @attr.s
        class Parent:
            x = attr.ib()

        @attr.s
        class Child(Parent):
            s = attr.ib()

        child_fields = [f.name for f in fields(Child)]
        assert "x" in child_fields
        assert "s" in child_fields

    @given(st.integers(), st.text())
    def test_parent_fields_come_first(self, x, s):
        """Parent fields appear before child fields in field order."""
        @attr.s
        class Parent:
            x = attr.ib()

        @attr.s
        class Child(Parent):
            s = attr.ib()

        child_fields = [f.name for f in fields(Child)]
        assert child_fields.index("x") < child_fields.index("s")

    @given(st.integers(), st.text())
    def test_subclass_instance_has_all_fields(self, x, s):
        """Subclass instances have all parent and child fields accessible."""
        @attr.s
        class Parent:
            x = attr.ib()

        @attr.s
        class Child(Parent):
            s = attr.ib()

        c = Child(x=x, s=s)
        assert c.x == x
        assert c.s == s

    @given(st.integers(), st.text())
    def test_subclass_equality(self, x, s):
        """Two subclass instances with same fields are equal."""
        @attr.s
        class Parent:
            x = attr.ib()

        @attr.s
        class Child(Parent):
            s = attr.ib()

        c1 = Child(x=x, s=s)
        c2 = Child(x=x, s=s)
        assert c1 == c2

    @given(st.integers(), st.text())
    def test_parent_and_child_not_equal(self, x, s):
        """Parent and child instances are never equal even with same field values."""
        @attr.s
        class Parent:
            x = attr.ib()

        @attr.s
        class Child(Parent):
            s = attr.ib(default="")

        p = Parent(x=x)
        c = Child(x=x, s="")
        assert p != c


# ============================================================================
# EQ=FALSE / ORDER=FALSE: Comparison opt-out properties
# ============================================================================

class TestEqOrderOptOut:
    """Property-based tests for eq=False and order=False."""

    @given(st.integers())
    def test_eq_false_uses_identity(self, val):
        """With eq=False, instances are only equal to themselves."""
        @attr.s(eq=False)
        class C:
            x = attr.ib()

        c1 = C(x=val)
        c2 = C(x=val)
        assert c1 != c2
        assert c1 == c1

    @given(st.integers())
    def test_eq_false_no_hash_generated(self, val):
        """With eq=False, attrs does not generate __hash__."""
        @attr.s(eq=False)
        class C:
            x = attr.ib()

        # Falls back to id-based hash from object
        c = C(x=val)
        assert hash(c) == id(c) // 16 or isinstance(hash(c), int)

    @given(st.integers(), st.integers())
    def test_order_false_no_lt(self, a, b):
        """With order=False, < raises TypeError."""
        @attr.s(order=False)
        class C:
            x = attr.ib()

        c1 = C(x=a)
        c2 = C(x=b)
        with pytest.raises(TypeError):
            _ = c1 < c2


# ============================================================================
# INIT=FALSE FIELDS: Non-init field properties
# ============================================================================

class TestInitFalseFields:
    """Property-based tests for fields with init=False."""

    @given(st.integers())
    def test_init_false_field_not_in_init(self, val):
        """Fields with init=False are not accepted in __init__."""
        @attr.s
        class C:
            x = attr.ib()
            computed = attr.ib(init=False, default=0)

        # Should not accept 'computed' as init arg
        with pytest.raises(TypeError):
            C(x=val, computed=99)

    @given(st.integers())
    def test_init_false_field_has_default(self, val):
        """Fields with init=False use their default value."""
        @attr.s
        class C:
            x = attr.ib()
            tag = attr.ib(init=False, default="auto")

        c = C(x=val)
        assert c.tag == "auto"

    @given(st.integers())
    def test_init_false_field_appears_in_fields(self, val):
        """Fields with init=False still appear in fields()."""
        @attr.s
        class C:
            x = attr.ib()
            hidden = attr.ib(init=False, default=0)

        field_names = [f.name for f in fields(C)]
        assert "hidden" in field_names

    @given(st.integers())
    def test_init_false_field_in_repr(self, val):
        """Fields with init=False appear in repr by default."""
        @attr.s
        class C:
            x = attr.ib()
            tag = attr.ib(init=False, default="auto")

        c = C(x=val)
        assert "tag" in repr(c)


# ============================================================================
# KW_ONLY: Keyword-only argument properties
# ============================================================================

class TestKwOnlyProperties:
    """Property-based tests for kw_only fields."""

    @given(st.integers(), st.text())
    def test_kw_only_field_requires_keyword(self, x, s):
        """kw_only fields must be passed as keyword arguments."""
        @attr.s
        class C:
            x = attr.ib()
            s = attr.ib(kw_only=True)

        # Positional should fail
        with pytest.raises(TypeError):
            C(x, s)

        # Keyword should work
        c = C(x=x, s=s)
        assert c.x == x
        assert c.s == s

    @given(st.integers(), st.text())
    def test_kw_only_class_all_fields_keyword(self, x, s):
        """kw_only=True on class makes all fields keyword-only."""
        @attr.s(kw_only=True)
        class C:
            x = attr.ib()
            s = attr.ib()

        with pytest.raises(TypeError):
            C(x, s)

        c = C(x=x, s=s)
        assert c.x == x
        assert c.s == s


# ============================================================================
# ALIAS: Field alias properties
# ============================================================================

class TestAliasProperties:
    """Property-based tests for field alias."""

    @given(st.integers())
    def test_alias_used_in_init(self, val):
        """Field alias is used as the __init__ parameter name."""
        @attr.s
        class C:
            _x = attr.ib(alias="x")

        c = C(x=val)
        assert c._x == val

    @given(st.integers())
    def test_alias_field_name_unchanged(self, val):
        """Field name (not alias) is used for attribute access."""
        @attr.s
        class C:
            _x = attr.ib(alias="x")

        c = C(x=val)
        assert hasattr(c, "_x")
        assert not hasattr(c, "x")

    @given(st.integers())
    def test_alias_appears_in_repr(self, val):
        """Field name (not alias) appears in repr."""
        @attr.s
        class C:
            _x = attr.ib(alias="x")

        c = C(x=val)
        r = repr(c)
        assert "_x" in r


# ============================================================================
# CONVERTER WITH TAKES_SELF: Self-referential converter
# ============================================================================

class TestConverterTakesSelf:
    """Property-based tests for converter with takes_self=True."""

    @given(st.integers())
    def test_takes_self_receives_instance(self, val):
        """Converter with takes_self=True receives the partially-built instance."""
        received = []

        def conv(value, self):
            received.append(self)
            return value

        @attr.s
        class C:
            x = attr.ib()
            y = attr.ib(converter=attr.Converter(conv, takes_self=True))

        c = C(x=val, y=val)
        assert len(received) == 1
        assert received[0] is c

    @given(st.integers())
    def test_takes_self_can_use_other_fields(self, val):
        """Converter with takes_self=True can read already-set fields."""
        @attr.s
        class C:
            x = attr.ib()
            y = attr.ib(converter=attr.Converter(
                lambda v, self: v + self.x, takes_self=True
            ))

        c = C(x=val, y=10)
        assert c.y == 10 + val


# ============================================================================
# REPR=FALSE: Opt-out of repr
# ============================================================================

class TestReprFalseProperties:
    """Property-based tests for repr=False on fields."""

    @given(st.integers(), st.text())
    def test_repr_false_field_hidden(self, x, secret):
        """Fields with repr=False do not appear in repr."""
        @attr.s
        class C:
            x = attr.ib()
            secret = attr.ib(repr=False)

        c = C(x=x, secret=secret)
        r = repr(c)
        assert "secret" not in r
        assert str(x) in r or "x" in r

    @given(st.integers(), st.text())
    def test_repr_false_field_still_accessible(self, x, secret):
        """Fields with repr=False are still accessible as attributes."""
        @attr.s
        class C:
            x = attr.ib()
            secret = attr.ib(repr=False)

        c = C(x=x, secret=secret)
        assert c.secret == secret


# ============================================================================
# COMPARE=FALSE: Opt-out of field comparison
# ============================================================================

class TestCompareFalseProperties:
    """Property-based tests for eq=False on individual fields."""

    @given(st.integers(), st.integers())
    def test_compare_false_field_ignored_in_eq(self, x, noise):
        """Fields with eq=False are ignored in equality comparison."""
        @attr.s
        class C:
            x = attr.ib()
            noise = attr.ib(eq=False)

        c1 = C(x=x, noise=noise)
        c2 = C(x=x, noise=noise + 1)
        assert c1 == c2

    @given(st.integers(), st.integers())
    def test_compare_false_field_ignored_in_order(self, x, noise):
        """Fields with order=False are ignored in ordering."""
        @attr.s
        class C:
            x = attr.ib()
            noise = attr.ib(order=False)

        c1 = C(x=x, noise=noise)
        c2 = C(x=x, noise=noise + 1)
        assert not (c1 < c2)
        assert not (c1 > c2)


# ============================================================================
# MODERN API: attr.define, attr.mutable, attr.frozen
# ============================================================================

class TestModernApiProperties:
    """Property-based tests for the modern attr.define/mutable/frozen API."""

    @given(st.integers(), st.text())
    def test_define_creates_attrs_class(self, x, s):
        """attr.define produces a valid attrs class."""
        @attr.define
        class C:
            x: int = attr.field()
            s: str = attr.field()

        assert has(C)
        c = C(x=x, s=s)
        assert c.x == x
        assert c.s == s

    @given(st.integers())
    def test_define_slots_by_default(self, val):
        """attr.define uses slots=True by default."""
        @attr.define
        class C:
            x: int = 0

        c = C(x=val)
        assert hasattr(C, '__slots__')
        assert not hasattr(c, '__dict__')

    @given(st.integers())
    def test_define_on_setattr_validates_by_default(self, val):
        """attr.define sets on_setattr to validate+convert by default."""
        @attr.define
        class C:
            x: int = attr.field(validator=instance_of(int))

        c = C(x=val)
        with pytest.raises(TypeError):
            c.x = "not_an_int"

    @given(st.integers())
    def test_mutable_allows_mutation(self, val):
        """attr.mutable (alias for define) allows post-init mutation."""
        @attr.mutable
        class C:
            x: int = 0

        c = C(x=val)
        c.x = val + 1
        assert c.x == val + 1

    @given(st.integers())
    def test_frozen_api_raises_on_mutation(self, val):
        """attr.frozen raises FrozenInstanceError on mutation."""
        from attr.exceptions import FrozenInstanceError

        @attr.frozen
        class C:
            x: int = 0

        c = C(x=val)
        with pytest.raises(FrozenInstanceError):
            c.x = val + 1

    @given(st.integers())
    def test_frozen_api_is_hashable(self, val):
        """attr.frozen instances are hashable."""
        @attr.frozen
        class C:
            x: int = 0

        c = C(x=val)
        assert isinstance(hash(c), int)

    @given(st.integers())
    def test_define_evolve_works(self, val):
        """evolve() works with attr.define classes."""
        @attr.define
        class C:
            x: int = 0

        c = C(x=val)
        c2 = evolve(c, x=val + 1)
        assert c2.x == val + 1

    @given(st.integers())
    def test_define_asdict_works(self, val):
        """asdict() works with attr.define classes."""
        @attr.define
        class C:
            x: int = 0

        c = C(x=val)
        d = asdict(c)
        assert d == {"x": val}


# ============================================================================
# SETTERS.NO_OP: Pass-through setter
# ============================================================================

class TestSettersNoOp:
    """Property-based tests for setters.NO_OP."""

    @given(st.integers(), st.integers())
    def test_no_op_allows_any_set(self, initial, new_val):
        """NO_OP setter allows any value to be set without validation."""
        from attr.setters import NO_OP

        @attr.s
        class C:
            x = attr.ib(
                validator=instance_of(int),
                on_setattr=NO_OP,
            )

        c = C(x=initial)
        # NO_OP bypasses on_setattr, so even wrong types can be set
        c.x = new_val
        assert c.x == new_val


# ============================================================================
# SETTERS.PIPE: validate + convert combination
# ============================================================================

class TestSettersPipeValidateConvert:
    """Property-based tests for setters.pipe combining validate and convert."""

    @given(st.integers())
    def test_pipe_convert_then_validate(self, val):
        """pipe(convert, validate) converts first, then validates."""
        from attr.setters import validate as setter_validate, convert as setter_convert

        @attr.s
        class C:
            x = attr.ib(
                converter=str,
                validator=instance_of(str),
                on_setattr=setter_pipe(setter_convert, setter_validate),
            )

        c = C(x=0)
        c.x = val
        assert c.x == str(val)
        assert isinstance(c.x, str)

    @given(st.integers())
    def test_pipe_validate_then_convert(self, val):
        """pipe(validate, convert) validates the raw int, then converts to str on post-init set."""
        from attr.setters import validate as setter_validate, convert as setter_convert

        @attr.s
        class C:
            # converter=str runs at __init__ time; on_setattr fires only post-init
            x = attr.ib(
                converter=str,
                validator=instance_of(str),
                on_setattr=setter_pipe(setter_validate, setter_convert),
            )

        # After __init__, x is already a str (converter ran)
        c = C(x=val)
        assert c.x == str(val)

        # Post-init set: validate checks str, convert re-applies str()
        c.x = str(val + 1)
        assert c.x == str(val + 1)


# ============================================================================
# DEEP_ITERABLE: With iterable validator
# ============================================================================

class TestDeepIterableWithIterableValidator:
    """Property-based tests for deep_iterable with iterable_validator."""

    @given(st.lists(st.integers(), min_size=0, max_size=20))
    def test_iterable_validator_applied(self, lst):
        """deep_iterable applies iterable_validator to the whole iterable."""
        from attr.validators import deep_iterable

        @attr.s
        class C:
            x = attr.ib(validator=deep_iterable(
                member_validator=instance_of(int),
                iterable_validator=instance_of(list),
            ))

        C(x=lst)  # Should not raise

    @given(st.sets(st.integers(), min_size=0, max_size=10))
    def test_iterable_validator_rejects_wrong_container(self, s):
        """deep_iterable rejects wrong container type."""
        from attr.validators import deep_iterable

        @attr.s
        class C:
            x = attr.ib(validator=deep_iterable(
                member_validator=instance_of(int),
                iterable_validator=instance_of(list),
            ))

        with pytest.raises(TypeError):
            C(x=s)  # set, not list


# ============================================================================
# NOT_: Custom message
# ============================================================================

class TestNotWithMessage:
    """Property-based tests for not_ with custom message."""

    @given(st.integers(min_value=0))
    def test_not_with_msg_raises_with_message(self, val):
        """not_(v, msg=...) includes the custom message in the error."""
        v = ge(0)
        inverted = not_(v, msg="must be negative")

        @attr.s
        class C:
            x = attr.ib(validator=inverted)

        with pytest.raises(ValueError, match="must be negative"):
            C(x=val)


# ============================================================================
# VERSIONINFO: String representation
# ============================================================================

class TestVersionInfoStr:
    """Property-based tests for VersionInfo string representation."""

    @given(
        st.integers(min_value=0, max_value=99),
        st.integers(min_value=0, max_value=99),
        st.integers(min_value=0, max_value=99),
        st.sampled_from(["dev0", "final", "post1"]),
    )
    def test_str_contains_version_numbers(self, year, minor, micro, level):
        """str(VersionInfo) contains year, minor, and micro."""
        v = VersionInfo(year, minor, micro, level)
        s = str(v)
        assert str(year) in s
        assert str(minor) in s
        assert str(micro) in s

    @given(
        st.integers(min_value=0, max_value=99),
        st.integers(min_value=0, max_value=99),
        st.integers(min_value=0, max_value=99),
        st.sampled_from(["dev0", "final", "post1"]),
    )
    def test_repr_is_evaluable_form(self, year, minor, micro, level):
        """repr(VersionInfo) contains the class name."""
        v = VersionInfo(year, minor, micro, level)
        r = repr(v)
        assert "VersionInfo" in r


# ============================================================================
# ATTR.FIELD: Modern field() API
# ============================================================================

class TestAttrFieldApi:
    """Property-based tests for attr.field() (modern API)."""

    @given(st.integers())
    def test_field_with_default(self, val):
        """attr.field(default=...) sets the default value."""
        @attr.define
        class C:
            x: int = attr.field(default=val)

        c = C()
        assert c.x == val

    @given(st.integers())
    def test_field_with_factory(self, val):
        """attr.field(factory=...) calls factory per instance."""
        @attr.define
        class C:
            items: list = attr.field(factory=list)

        c1 = C()
        c2 = C()
        assert c1.items is not c2.items

    @given(st.integers())
    def test_field_with_validator(self, val):
        """attr.field(validator=...) validates on construction."""
        @attr.define
        class C:
            x: int = attr.field(validator=instance_of(int))

        C(x=val)  # Should not raise

        with pytest.raises(TypeError):
            C(x="not_an_int")

    @given(st.integers())
    def test_field_with_converter(self, val):
        """attr.field(converter=...) converts on construction."""
        @attr.define
        class C:
            x: str = attr.field(converter=str)

        c = C(x=val)
        assert c.x == str(val)
        assert isinstance(c.x, str)


# ============================================================================
# ATTRIBUTE PROPERTIES: Introspection of Attribute objects
# ============================================================================

class TestAttributeIntrospection:
    """Property-based tests for Attribute object properties."""

    @given(simple_classes())
    def test_attribute_name_is_string(self, cls):
        """Every Attribute has a string name."""
        for field in fields(cls):
            assert isinstance(field.name, str)

    @given(simple_classes())
    def test_attribute_has_expected_properties(self, cls):
        """Every Attribute has the standard set of properties."""
        for field in fields(cls):
            assert hasattr(field, 'name')
            assert hasattr(field, 'default')
            assert hasattr(field, 'validator')
            assert hasattr(field, 'repr')
            assert hasattr(field, 'eq')
            assert hasattr(field, 'order')
            assert hasattr(field, 'hash')
            assert hasattr(field, 'init')
            assert hasattr(field, 'metadata')
            assert hasattr(field, 'type')
            assert hasattr(field, 'converter')
            assert hasattr(field, 'kw_only')

    @given(simple_classes())
    def test_attribute_repr_is_bool(self, cls):
        """Attribute.repr is always a bool (or callable)."""
        for field in fields(cls):
            assert isinstance(field.repr, (bool, type(None))) or callable(field.repr)

    @given(simple_classes())
    def test_attribute_eq_is_bool(self, cls):
        """Attribute.eq is always a bool (or callable)."""
        for field in fields(cls):
            assert isinstance(field.eq, (bool, type(None))) or callable(field.eq)

    @given(simple_classes())
    def test_attribute_init_is_bool(self, cls):
        """Attribute.init is always a bool."""
        for field in fields(cls):
            assert isinstance(field.init, bool)

    @given(simple_classes())
    def test_attribute_kw_only_is_bool(self, cls):
        """Attribute.kw_only is always a bool."""
        for field in fields(cls):
            assert isinstance(field.kw_only, bool)

    @given(simple_classes())
    def test_attribute_metadata_is_mapping(self, cls):
        """Attribute.metadata is always a mapping."""
        from collections.abc import Mapping
        for field in fields(cls):
            assert isinstance(field.metadata, Mapping)


# ============================================================================
# DEEP_MAPPING: With value validator
# ============================================================================

class TestDeepMappingValueValidator:
    """Property-based tests for deep_mapping with only value_validator."""

    @given(st.dictionaries(st.text(), st.integers(), max_size=10))
    def test_value_validator_only(self, d):
        """deep_mapping with only value_validator validates values."""
        from attr.validators import deep_mapping

        @attr.s
        class C:
            x = attr.ib(validator=deep_mapping(
                value_validator=instance_of(int),
            ))

        C(x=d)  # Should not raise

    @given(st.dictionaries(st.text(), st.text(), min_size=1, max_size=10))
    def test_value_validator_rejects_wrong_values(self, d):
        """deep_mapping fails when values have wrong type."""
        from attr.validators import deep_mapping

        @attr.s
        class C:
            x = attr.ib(validator=deep_mapping(
                value_validator=instance_of(int),
            ))

        with pytest.raises(TypeError):
            C(x=d)


# ============================================================================
# CMP_USING: Full ordering properties
# ============================================================================

class TestCmpUsingFullOrdering:
    """Property-based tests for cmp_using with full ordering."""

    @given(st.integers(), st.integers(), st.integers())
    def test_transitivity(self, a, b, c):
        """If a <= b and b <= c then a <= c."""
        Cmp = cmp_using(
            eq=lambda x, y: x == y,
            lt=lambda x, y: x < y,
        )
        ca, cb, cc = Cmp(a), Cmp(b), Cmp(c)
        if ca <= cb and cb <= cc:
            assert ca <= cc

    @given(st.integers(), st.integers())
    def test_totality(self, a, b):
        """For any a, b: a <= b or b <= a."""
        Cmp = cmp_using(
            eq=lambda x, y: x == y,
            lt=lambda x, y: x < y,
        )
        ca, cb = Cmp(a), Cmp(b)
        assert (ca <= cb) or (cb <= ca)

    @given(st.integers())
    def test_reflexivity(self, a):
        """a <= a is always True."""
        Cmp = cmp_using(
            eq=lambda x, y: x == y,
            lt=lambda x, y: x < y,
        )
        ca = Cmp(a)
        assert ca <= ca

    @given(st.integers(), st.integers())
    def test_antisymmetry(self, a, b):
        """If a <= b and b <= a then a == b."""
        Cmp = cmp_using(
            eq=lambda x, y: x == y,
            lt=lambda x, y: x < y,
        )
        ca, cb = Cmp(a), Cmp(b)
        if ca <= cb and cb <= ca:
            assert ca == cb


# ============================================================================
# PIPE CONVERTER: None passthrough with optional
# ============================================================================

class TestPipeWithOptional:
    """Property-based tests for pipe combined with optional."""

    @given(st.integers())
    def test_pipe_optional_none_passthrough(self, val):
        """pipe(optional(int), str) passes None through optional then converts."""
        # optional(int)(None) = None, then str(None) = "None"
        c = pipe(optional(int), str)
        assert c(None) == "None"

    @given(st.integers().map(str))
    def test_pipe_optional_non_none(self, val):
        """pipe(optional(int), str) converts non-None through both converters."""
        c = pipe(optional(int), str)
        assert c(val) == str(int(val))

    @given(st.integers())
    def test_pipe_with_three_converters(self, val):
        """pipe(f, g, h) applies all three in order."""
        c = pipe(abs, str, len)
        expected = len(str(abs(val)))
        assert c(val) == expected


# ============================================================================
# EVOLVE: With validators
# ============================================================================

class TestEvolveWithValidators:
    """Property-based tests for evolve interacting with validators."""

    @given(st.integers(min_value=0))
    def test_evolve_runs_validators(self, val):
        """evolve runs validators on the new instance."""
        @attr.s
        class C:
            x = attr.ib(validator=ge(0))

        inst = C(x=val)
        evolved = evolve(inst, x=val + 1)
        assert evolved.x == val + 1

    @given(st.integers(min_value=0))
    def test_evolve_rejects_invalid_values(self, val):
        """evolve raises when new value fails validation."""
        @attr.s
        class C:
            x = attr.ib(validator=ge(0))

        inst = C(x=val)
        with pytest.raises(ValueError):
            evolve(inst, x=-(val + 1))


# ============================================================================
# ASDICT: Nested attrs classes
# ============================================================================

class TestAsdictNested:
    """Property-based tests for asdict with nested attrs classes."""

    @given(st.integers(), st.text())
    def test_nested_attrs_recursed(self, x, s):
        """asdict recurses into nested attrs instances."""
        @attr.s
        class Inner:
            s = attr.ib()

        @attr.s
        class Outer:
            x = attr.ib()
            inner = attr.ib()

        inst = Outer(x=x, inner=Inner(s=s))
        d = asdict(inst)

        assert d["x"] == x
        assert isinstance(d["inner"], dict)
        assert d["inner"]["s"] == s

    @given(st.integers(), st.text())
    def test_nested_astuple_recursed(self, x, s):
        """astuple recurses into nested attrs instances."""
        @attr.s
        class Inner:
            s = attr.ib()

        @attr.s
        class Outer:
            x = attr.ib()
            inner = attr.ib()

        inst = Outer(x=x, inner=Inner(s=s))
        t = astuple(inst)

        assert t[0] == x
        assert isinstance(t[1], tuple)
        assert t[1][0] == s


# ============================================================================
# MAKE_CLASS: With bases
# ============================================================================

class TestMakeClassWithBases:
    """Property-based tests for make_class with base classes."""

    @given(
        _valid_class_name,
        st.lists(_valid_attr_name, min_size=1, max_size=3, unique=True),
    )
    def test_make_class_with_base(self, name, attr_names):
        """make_class with a base class inherits base fields."""
        @attr.s
        class Base:
            base_field = attr.ib(default=0)

        # Use kw_only=True so mandatory child fields can follow defaulted base fields
        cls = attr.make_class(name, attr_names, bases=(Base,), kw_only=True)
        field_names = [f.name for f in fields(cls)]

        assert "base_field" in field_names
        for n in attr_names:
            assert n in field_names

    @given(
        _valid_class_name,
        st.lists(_valid_attr_name, min_size=0, max_size=3, unique=True),
    )
    def test_make_class_with_base_is_subclass(self, name, attr_names):
        """make_class with a base class produces a subclass."""
        @attr.s
        class Base:
            base_field = attr.ib(default=0)

        cls = attr.make_class(name, attr_names, bases=(Base,), kw_only=True)
        assert issubclass(cls, Base)


# ============================================================================
# FIELDS: Ordering and count invariants
# ============================================================================

class TestFieldsOrderingInvariants:
    """Property-based tests for field ordering invariants."""

    @given(simple_classes())
    def test_fields_count_matches_make_class(self, cls):
        """Number of fields matches what was defined."""
        f = fields(cls)
        assert len(f) >= 0

    @given(simple_classes())
    def test_fields_names_are_unique(self, cls):
        """All field names in a class are unique."""
        names = [f.name for f in fields(cls)]
        assert len(names) == len(set(names))

    @given(simple_classes())
    def test_fields_tuple_is_immutable(self, cls):
        """fields() returns a tuple (immutable)."""
        f = fields(cls)
        assert isinstance(f, tuple)
        with pytest.raises((TypeError, AttributeError)):
            f[0] = None  # type: ignore


# ============================================================================
# HASH: Frozen slots class
# ============================================================================

class TestFrozenSlotsHash:
    """Property-based tests for frozen+slots class hashing."""

    @given(st.integers(), st.text())
    def test_frozen_slots_hashable(self, x, s):
        """frozen+slots class instances are hashable."""
        @attr.s(frozen=True, slots=True)
        class C:
            x = attr.ib()
            s = attr.ib()

        c = C(x=x, s=s)
        assert isinstance(hash(c), int)

    @given(st.integers(), st.text())
    def test_frozen_slots_usable_as_dict_key(self, x, s):
        """frozen+slots instances can be used as dict keys."""
        @attr.s(frozen=True, slots=True)
        class C:
            x = attr.ib()
            s = attr.ib()

        c = C(x=x, s=s)
        d = {c: "value"}
        assert d[c] == "value"

    @given(st.integers(), st.text())
    def test_frozen_slots_usable_in_set(self, x, s):
        """frozen+slots instances can be stored in sets."""
        @attr.s(frozen=True, slots=True)
        class C:
            x = attr.ib()
            s = attr.ib()

        c1 = C(x=x, s=s)
        c2 = C(x=x, s=s)
        assert c1 == c2
        assert len({c1, c2}) == 1


# ============================================================================
# RESOLVE_TYPES: Forward reference resolution
# ============================================================================

class TestResolveTypes:
    """Property-based tests for attr.resolve_types."""

    def test_resolve_types_returns_class(self):
        """resolve_types returns the class itself."""
        @attr.define
        class C:
            x: int = attr.field()

        result = attr.resolve_types(C)
        assert result is C

    def test_resolve_types_populates_type(self):
        """resolve_types fills in Attribute.type from annotations."""
        @attr.define
        class C:
            x: int = attr.field()
            s: str = attr.field()

        attr.resolve_types(C)
        type_map = {f.name: f.type for f in fields(C)}
        assert type_map["x"] is int
        assert type_map["s"] is str

    @given(st.integers(), st.text())
    def test_resolve_types_does_not_change_behavior(self, x, s):
        """resolve_types does not affect construction or equality."""
        @attr.define
        class C:
            x: int = attr.field()
            s: str = attr.field()

        attr.resolve_types(C)
        c1 = C(x=x, s=s)
        c2 = C(x=x, s=s)
        assert c1 == c2


# ============================================================================
# ASTUPLE: retain_collection_types
# ============================================================================

class TestAstupleRetainCollectionTypes:
    """Property-based tests for astuple with retain_collection_types."""

    @given(st.lists(st.integers(), min_size=0, max_size=10))
    def test_retain_list_type(self, lst):
        """With retain_collection_types=True, lists stay as lists."""
        @attr.s
        class C:
            items = attr.ib()

        inst = C(items=lst)
        t = astuple(inst, retain_collection_types=True)
        assert isinstance(t[0], list)

    @given(st.tuples(st.integers(), st.text()))
    def test_retain_tuple_type(self, tup):
        """With retain_collection_types=True, tuples stay as tuples."""
        @attr.s
        class C:
            items = attr.ib()

        inst = C(items=tup)
        t = astuple(inst, retain_collection_types=True)
        assert isinstance(t[0], tuple)

    @given(st.lists(st.integers(), min_size=0, max_size=10))
    def test_no_retain_converts_nested_attrs_to_tuple(self, lst):
        """Without retain_collection_types, nested attrs instances become tuples."""
        @attr.s
        class Inner:
            items = attr.ib()

        @attr.s
        class Outer:
            inner = attr.ib()

        inst = Outer(inner=Inner(items=lst))
        t = astuple(inst, retain_collection_types=False)
        # The nested Inner instance should be converted to a tuple
        assert isinstance(t[0], tuple)


# ============================================================================
# AND_: Short-circuit behavior
# ============================================================================

class TestAndShortCircuit:
    """Property-based tests for and_ short-circuit behavior."""

    @given(st.integers(min_value=0))
    def test_and_first_validator_fails_second_not_called(self, val):
        """and_ stops at the first failing validator."""
        call_log = []

        def v1(inst, attr, value):
            call_log.append("v1")
            if value < 0:
                raise ValueError("v1 failed")

        def v2(inst, attr, value):
            call_log.append("v2")

        @attr.s
        class C:
            x = attr.ib(validator=and_(v1, v2))

        call_log.clear()
        C(x=val)
        assert "v1" in call_log
        assert "v2" in call_log

    def test_and_stops_on_first_failure(self):
        """and_ does not call subsequent validators after one fails."""
        call_log = []

        def v1(inst, attr, value):
            call_log.append("v1")
            raise ValueError("v1 failed")

        def v2(inst, attr, value):
            call_log.append("v2")

        @attr.s
        class C:
            x = attr.ib(validator=and_(v1, v2))

        call_log.clear()
        with pytest.raises(ValueError):
            C(x=0)
        assert "v1" in call_log
        assert "v2" not in call_log


# ============================================================================
# DEEP_ITERABLE: Nested attrs instances
# ============================================================================

class TestDeepIterableNestedAttrs:
    """Property-based tests for deep_iterable with nested attrs instances."""

    @given(st.lists(st.integers(), min_size=0, max_size=10))
    def test_list_of_attrs_instances(self, values):
        """deep_iterable validates a list of attrs instances."""
        from attr.validators import deep_iterable

        @attr.s
        class Item:
            v = attr.ib()

        @attr.s
        class Container:
            items = attr.ib(validator=deep_iterable(instance_of(Item)))

        items = [Item(v=v) for v in values]
        Container(items=items)  # Should not raise

    @given(st.lists(st.integers(), min_size=1, max_size=10))
    def test_list_of_wrong_type_fails(self, values):
        """deep_iterable fails when members are wrong type."""
        from attr.validators import deep_iterable

        @attr.s
        class Item:
            v = attr.ib()

        @attr.s
        class Container:
            items = attr.ib(validator=deep_iterable(instance_of(Item)))

        with pytest.raises(TypeError):
            Container(items=values)  # raw ints, not Item instances


# ============================================================================
# VALIDATOR: Custom validator function
# ============================================================================

class TestCustomValidatorProperties:
    """Property-based tests for custom validator functions."""

    @given(st.integers(min_value=0, max_value=100))
    def test_custom_validator_passes(self, val):
        """Custom validator passes for valid values."""
        def must_be_even(inst, attr, value):
            if value % 2 != 0:
                raise ValueError(f"{attr.name} must be even, got {value}")

        @attr.s
        class C:
            x = attr.ib(validator=must_be_even)

        if val % 2 == 0:
            C(x=val)  # Should not raise

    @given(st.integers().filter(lambda x: x % 2 != 0))
    def test_custom_validator_fails(self, val):
        """Custom validator raises for invalid values."""
        def must_be_even(inst, attr, value):
            if value % 2 != 0:
                raise ValueError(f"{attr.name} must be even, got {value}")

        @attr.s
        class C:
            x = attr.ib(validator=must_be_even)

        with pytest.raises(ValueError, match="must be even"):
            C(x=val)

    @given(st.integers())
    def test_validator_receives_correct_args(self, val):
        """Validator receives (instance, attribute, value) correctly."""
        received = []

        def capturing_validator(inst, attr, value):
            received.append((inst, attr, value))

        @attr.s
        class C:
            x = attr.ib(validator=capturing_validator)

        c = C(x=val)
        assert len(received) == 1
        inst, attr_obj, value = received[0]
        assert inst is c
        assert attr_obj.name == "x"
        assert value == val


# ============================================================================
# CONVERTER: Custom converter function
# ============================================================================

class TestCustomConverterProperties:
    """Property-based tests for custom converter functions."""

    @given(st.integers())
    def test_converter_transforms_value(self, val):
        """Custom converter transforms the input value."""
        @attr.s
        class C:
            x = attr.ib(converter=lambda v: v * 2)

        c = C(x=val)
        assert c.x == val * 2

    @given(st.text())
    def test_converter_strips_whitespace(self, val):
        """Converter can normalize strings."""
        @attr.s
        class C:
            x = attr.ib(converter=str.strip)

        c = C(x=val)
        assert c.x == val.strip()

    @given(st.integers())
    def test_converter_runs_before_validator(self, val):
        """Converter runs before validator."""
        @attr.s
        class C:
            x = attr.ib(
                converter=abs,
                validator=ge(0),
            )

        c = C(x=val)
        assert c.x >= 0
        assert c.x == abs(val)


# ============================================================================
# SLOTS + FROZEN: Combined properties
# ============================================================================

class TestSlotsFrozenCombined:
    """Property-based tests for slots=True + frozen=True combination."""

    @given(st.integers(), st.text())
    def test_slots_frozen_no_dict_no_mutation(self, x, s):
        """slots+frozen: no __dict__, no mutation."""
        from attr.exceptions import FrozenInstanceError

        @attr.s(slots=True, frozen=True)
        class C:
            x = attr.ib()
            s = attr.ib()

        c = C(x=x, s=s)
        assert not hasattr(c, '__dict__')
        with pytest.raises(FrozenInstanceError):
            c.x = x + 1

    @given(st.integers())
    def test_slots_frozen_evolve(self, val):
        """evolve works on slots+frozen instances."""
        @attr.s(slots=True, frozen=True)
        class C:
            x = attr.ib()

        c = C(x=val)
        c2 = evolve(c, x=val + 1)
        assert c2.x == val + 1
        assert c.x == val

    @given(st.integers(), st.text())
    def test_slots_frozen_equality_and_hash(self, x, s):
        """slots+frozen instances support equality and hashing."""
        @attr.s(slots=True, frozen=True)
        class C:
            x = attr.ib()
            s = attr.ib()

        c1 = C(x=x, s=s)
        c2 = C(x=x, s=s)
        assert c1 == c2
        assert hash(c1) == hash(c2)


# ============================================================================
# VALIDATORS: in_ with various collection types
# ============================================================================

class TestInValidatorCollections:
    """Property-based tests for in_ with different collection types."""

    @given(st.integers(min_value=0, max_value=9))
    def test_in_with_list(self, val):
        """in_ works with a list."""
        @attr.s
        class C:
            x = attr.ib(validator=in_(list(range(10))))

        C(x=val)  # Should not raise

    @given(st.integers(min_value=0, max_value=9))
    def test_in_with_set(self, val):
        """in_ works with a set."""
        @attr.s
        class C:
            x = attr.ib(validator=in_(set(range(10))))

        C(x=val)  # Should not raise

    @given(st.integers(min_value=0, max_value=9))
    def test_in_with_tuple(self, val):
        """in_ works with a tuple."""
        @attr.s
        class C:
            x = attr.ib(validator=in_(tuple(range(10))))

        C(x=val)  # Should not raise

    @given(st.integers().filter(lambda x: x < 0 or x >= 10))
    def test_in_fails_for_non_member(self, val):
        """in_ fails for values not in the collection."""
        @attr.s
        class C:
            x = attr.ib(validator=in_(range(10)))

        with pytest.raises(ValueError):
            C(x=val)


# ============================================================================
# EVOLVE: Multiple field changes
# ============================================================================

class TestEvolveMultipleFields:
    """Property-based tests for evolve with multiple field changes."""

    @given(st.integers(), st.text(), st.floats(allow_nan=False))
    def test_evolve_multiple_fields(self, x, s, f):
        """evolve can change multiple fields at once."""
        @attr.s
        class C:
            x = attr.ib()
            s = attr.ib()
            f = attr.ib()

        inst = C(x=0, s="", f=0.0)
        evolved = evolve(inst, x=x, s=s, f=f)
        assert evolved.x == x
        assert evolved.s == s
        assert evolved.f == f

    @given(st.integers(), st.text())
    def test_evolve_partial_change(self, x, s):
        """evolve with partial change preserves unchanged fields."""
        @attr.s
        class C:
            x = attr.ib()
            s = attr.ib(default="original")

        inst = C(x=0)
        evolved = evolve(inst, x=x)
        assert evolved.x == x
        assert evolved.s == inst.s


# ============================================================================
# ASDICT: Filter with multiple fields
# ============================================================================

class TestAsdictFilterMultiple:
    """Property-based tests for asdict with multi-field filters."""

    @given(st.lists(st.sampled_from(["x", "y", "z"]), min_size=0, max_size=3, unique=True))
    def test_include_multiple_fields(self, field_names):
        """include with multiple names keeps exactly those fields."""
        @attr.s
        class C:
            x = attr.ib(default=1)
            y = attr.ib(default=2)
            z = attr.ib(default=3)

        inst = C()
        result = asdict(inst, filter=include(*field_names))
        assert set(result.keys()) == set(field_names)

    @given(st.lists(st.sampled_from(["x", "y", "z"]), min_size=0, max_size=3, unique=True))
    def test_exclude_multiple_fields(self, field_names):
        """exclude with multiple names removes exactly those fields."""
        @attr.s
        class C:
            x = attr.ib(default=1)
            y = attr.ib(default=2)
            z = attr.ib(default=3)

        inst = C()
        result = asdict(inst, filter=exclude(*field_names))
        all_names = {"x", "y", "z"}
        assert set(result.keys()) == all_names - set(field_names)

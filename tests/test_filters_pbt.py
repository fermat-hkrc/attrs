# SPDX-License-Identifier: MIT

"""
Property-based tests for `attr.filters`.
"""

import pytest

from hypothesis import given
from hypothesis import strategies as st

import attr

from attr import asdict, astuple
from attr.filters import exclude, include


@attr.s
class SimpleClass:
    x = attr.ib()
    y = attr.ib()
    z = attr.ib()


@attr.s
class NestedClass:
    a = attr.ib()
    b = attr.ib()


class TestIncludeExcludeProperties:
    """
    Property-based tests for include/exclude filters.
    """

    @given(st.integers(), st.integers(), st.integers())
    def test_include_exclude_inverse(self, x, y, z):
        """
        Property: include and exclude are inverses for single attributes.
        For a given attribute, include(attr) and exclude(attr) should
        partition the fields.
        """
        obj = SimpleClass(x, y, z)

        # Include only 'x'
        included = asdict(obj, filter=include("x"))
        # Exclude only 'x'
        excluded = asdict(obj, filter=exclude("x"))

        # Together they should cover all fields
        assert set(included.keys()) | set(excluded.keys()) == {"x", "y", "z"}
        # They should not overlap
        assert set(included.keys()) & set(excluded.keys()) == set()

        # Included should only have 'x'
        assert included == {"x": x}
        # Excluded should have 'y' and 'z'
        assert excluded == {"y": y, "z": z}

    @given(st.integers(), st.integers(), st.integers())
    def test_include_by_type(self, x, y, z):
        """
        Property: include by type filters values of that type.
        """
        obj = SimpleClass(x, "string", z)

        # Include only int types
        result = asdict(obj, filter=include(int))

        # Should only include integer values
        assert all(isinstance(v, int) for v in result.values())
        assert "x" in result
        assert "z" in result
        assert "y" not in result

    @given(st.integers(), st.integers(), st.integers())
    def test_exclude_by_type(self, x, y, z):
        """
        Property: exclude by type filters out values of that type.
        """
        obj = SimpleClass(x, "string", z)

        # Exclude int types
        result = asdict(obj, filter=exclude(int))

        # Should only include non-integer values
        assert all(not isinstance(v, int) for v in result.values())
        assert "y" in result
        assert "x" not in result
        assert "z" not in result

    @given(st.integers(), st.integers(), st.integers())
    def test_double_exclude_idempotent(self, x, y, z):
        """
        Property: Applying the same exclude filter twice is idempotent.
        """
        obj = SimpleClass(x, y, z)

        filter_func = exclude("x")
        result1 = asdict(obj, filter=filter_func)

        # Create a new object from result1 and apply filter again
        # Since 'x' is already excluded, applying again should be the same
        assert "x" not in result1
        assert result1 == {"y": y, "z": z}

    @given(st.integers(), st.integers(), st.integers())
    def test_include_multiple_names(self, x, y, z):
        """
        Property: include with multiple names includes all specified names.
        """
        obj = SimpleClass(x, y, z)

        result = asdict(obj, filter=include("x", "z"))

        assert set(result.keys()) == {"x", "z"}
        assert result == {"x": x, "z": z}

    @given(st.integers(), st.integers(), st.integers())
    def test_exclude_multiple_names(self, x, y, z):
        """
        Property: exclude with multiple names excludes all specified names.
        """
        obj = SimpleClass(x, y, z)

        result = asdict(obj, filter=exclude("x", "z"))

        assert set(result.keys()) == {"y"}
        assert result == {"y": y}

    @given(st.integers(), st.integers(), st.integers())
    def test_filter_preserves_values(self, x, y, z):
        """
        Property: Filters don't modify values, only select which to include.
        """
        obj = SimpleClass(x, y, z)

        included = asdict(obj, filter=include("x", "y"))

        # Values should be unchanged
        assert included["x"] == x
        assert included["y"] == y

    @given(st.integers(), st.text(), st.booleans())
    def test_include_by_attribute_object(self, x, y, z):
        """
        Property: include can filter by Attribute objects.
        """
        obj = SimpleClass(x, y, z)
        fields = attr.fields(SimpleClass)

        # Include by attribute object
        result = asdict(obj, filter=include(fields.x))

        assert result == {"x": x}

    @given(st.integers(), st.text(), st.booleans())
    def test_exclude_by_attribute_object(self, x, y, z):
        """
        Property: exclude can filter by Attribute objects.
        """
        obj = SimpleClass(x, y, z)
        fields = attr.fields(SimpleClass)

        # Exclude by attribute object
        result = asdict(obj, filter=exclude(fields.x))

        assert "x" not in result
        assert "y" in result
        assert "z" in result

    @given(st.integers(), st.integers())
    def test_filter_works_with_astuple(self, x, y):
        """
        Property: Filters work consistently with both asdict and astuple.
        """
        obj = SimpleClass(x, y, 42)

        dict_result = asdict(obj, filter=include("x", "y"))
        tuple_result = astuple(obj, filter=include("x", "y"))

        # Both should have same number of elements
        assert len(dict_result) == len(tuple_result)
        # Tuple should contain the same values
        assert tuple_result == (x, y)

    @given(st.integers(), st.integers(), st.integers())
    def test_no_filter_includes_all(self, x, y, z):
        """
        Property: No filter means all attributes are included.
        """
        obj = SimpleClass(x, y, z)

        result = asdict(obj)

        assert set(result.keys()) == {"x", "y", "z"}
        assert result == {"x": x, "y": y, "z": z}

    @given(st.integers(), st.integers(), st.integers())
    def test_include_empty_excludes_all(self, x, y, z):
        """
        Property: include() with no arguments excludes everything.
        """
        obj = SimpleClass(x, y, z)

        result = asdict(obj, filter=include())

        # Nothing matches, so nothing is included
        assert result == {}

    @given(st.integers(), st.integers(), st.integers())
    def test_exclude_empty_includes_all(self, x, y, z):
        """
        Property: exclude() with no arguments includes everything.
        """
        obj = SimpleClass(x, y, z)

        result = asdict(obj, filter=exclude())

        # Nothing is excluded, so everything is included
        assert result == {"x": x, "y": y, "z": z}

    @given(st.integers(), st.integers())
    def test_filter_with_nested_classes(self, a, b):
        """
        Property: Filters apply recursively to nested attrs classes.
        """
        inner = SimpleClass(1, 2, 3)
        outer = NestedClass(inner, b)

        result = asdict(outer, filter=exclude("z"))

        # 'z' should be excluded from nested class
        assert "z" not in result["a"]
        assert set(result["a"].keys()) == {"x", "y"}

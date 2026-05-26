# SPDX-License-Identifier: MIT

"""
Property-based tests for `attr._version_info.VersionInfo`.
"""

import pytest

from hypothesis import assume, given
from hypothesis import strategies as st

from attr._version_info import VersionInfo


# Strategy for generating valid version components
years = st.integers(min_value=0, max_value=9999)
minors = st.integers(min_value=0, max_value=999)
micros = st.integers(min_value=0, max_value=999)
releaselevels = st.sampled_from(["dev0", "dev1", "final", "post1", "post2"])


@st.composite
def version_infos(draw):
    """Generate valid VersionInfo instances."""
    return VersionInfo(
        year=draw(years),
        minor=draw(minors),
        micro=draw(micros),
        releaselevel=draw(releaselevels),
    )


@st.composite
def version_tuples(draw):
    """Generate valid version tuples (1-4 elements)."""
    length = draw(st.integers(min_value=1, max_value=4))
    if length == 1:
        return (draw(years),)
    elif length == 2:
        return (draw(years), draw(minors))
    elif length == 3:
        return (draw(years), draw(minors), draw(micros))
    else:
        return (draw(years), draw(minors), draw(micros), draw(releaselevels))


class TestVersionInfoProperties:
    """
    Property-based tests for VersionInfo.
    """

    @given(version_infos())
    def test_equality_reflexive(self, v):
        """
        Property: Equality is reflexive - v == v.
        """
        assert v == v
        assert not (v != v)

    @given(version_infos(), version_infos())
    def test_equality_symmetric(self, v1, v2):
        """
        Property: Equality is symmetric - if v1 == v2, then v2 == v1.
        """
        if v1 == v2:
            assert v2 == v1
        if v1 != v2:
            assert v2 != v1

    @given(version_infos(), version_infos(), version_infos())
    def test_equality_transitive(self, v1, v2, v3):
        """
        Property: Equality is transitive - if v1 == v2 and v2 == v3, then v1 == v3.
        """
        if v1 == v2 and v2 == v3:
            assert v1 == v3

    @given(version_infos())
    def test_ordering_reflexive(self, v):
        """
        Property: v <= v and v >= v.
        """
        assert v <= v
        assert v >= v
        assert not (v < v)
        assert not (v > v)

    @given(version_infos(), version_infos())
    def test_ordering_antisymmetric(self, v1, v2):
        """
        Property: If v1 <= v2 and v2 <= v1, then v1 == v2.
        """
        if v1 <= v2 and v2 <= v1:
            assert v1 == v2

    @given(version_infos(), version_infos(), version_infos())
    def test_ordering_transitive(self, v1, v2, v3):
        """
        Property: If v1 <= v2 and v2 <= v3, then v1 <= v3.
        """
        if v1 <= v2 and v2 <= v3:
            assert v1 <= v3

    @given(version_infos(), version_infos())
    def test_ordering_total(self, v1, v2):
        """
        Property: Total ordering - either v1 <= v2 or v2 <= v1.
        """
        assert v1 <= v2 or v2 <= v1

    @given(version_infos(), version_infos())
    def test_less_than_implies_not_greater(self, v1, v2):
        """
        Property: If v1 < v2, then not (v1 > v2).
        """
        if v1 < v2:
            assert not (v1 > v2)
            assert v1 != v2

    @given(version_infos(), version_infos())
    def test_equal_implies_not_less_or_greater(self, v1, v2):
        """
        Property: If v1 == v2, then not (v1 < v2) and not (v1 > v2).
        """
        if v1 == v2:
            assert not (v1 < v2)
            assert not (v1 > v2)

    @given(version_infos())
    def test_hash_consistency(self, v):
        """
        Property: Hash is consistent across multiple calls.
        """
        h1 = hash(v)
        h2 = hash(v)
        assert h1 == h2

    @given(version_infos(), version_infos())
    def test_equal_objects_same_hash(self, v1, v2):
        """
        Property: Equal objects must have equal hashes.
        """
        if v1 == v2:
            assert hash(v1) == hash(v2)

    @given(version_infos(), version_tuples())
    def test_comparison_with_tuple(self, v, t):
        """
        Property: VersionInfo can be compared with tuples.
        """
        # Should not raise an exception
        result = v == t
        assert isinstance(result, bool)

        result = v < t
        assert isinstance(result, bool)

    @given(version_infos())
    def test_tuple_roundtrip_full(self, v):
        """
        Property: Converting to tuple and back preserves equality.
        """
        t = (v.year, v.minor, v.micro, v.releaselevel)
        assert v == t

    @given(version_infos())
    def test_tuple_comparison_prefix(self, v):
        """
        Property: VersionInfo compares correctly with tuple prefixes.
        """
        # Compare with 1-element tuple
        t1 = (v.year,)
        assert v == t1 or v < t1 or v > t1

        # Compare with 2-element tuple
        t2 = (v.year, v.minor)
        assert v == t2 or v < t2 or v > t2

        # Compare with 3-element tuple
        t3 = (v.year, v.minor, v.micro)
        assert v == t3 or v < t3 or v > t3

    @given(years, minors, micros, releaselevels)
    def test_construction_preserves_values(self, year, minor, micro, releaselevel):
        """
        Property: Constructor preserves the values passed to it.
        """
        v = VersionInfo(year, minor, micro, releaselevel)
        assert v.year == year
        assert v.minor == minor
        assert v.micro == micro
        assert v.releaselevel == releaselevel

    @given(version_infos())
    def test_frozen_immutable(self, v):
        """
        Property: VersionInfo is frozen and cannot be modified.
        """
        with pytest.raises(AttributeError):
            v.year = 999

        with pytest.raises(AttributeError):
            v.minor = 999

    @given(years, minors, micros)
    def test_releaselevel_ordering(self, year, minor, micro):
        """
        Property: Release levels are ordered: dev0 < final < post1 < post2.
        """
        dev = VersionInfo(year, minor, micro, "dev0")
        final = VersionInfo(year, minor, micro, "final")
        post1 = VersionInfo(year, minor, micro, "post1")
        post2 = VersionInfo(year, minor, micro, "post2")

        assert dev < final < post1 < post2

    @given(years, minors, micros, releaselevels)
    def test_year_dominates(self, year, minor, micro, releaselevel):
        """
        Property: Year is the most significant component.
        """
        assume(year < 9999)
        v1 = VersionInfo(year, minor, micro, releaselevel)
        v2 = VersionInfo(year + 1, 0, 0, "dev0")

        assert v1 < v2

    @given(years, minors, micros, releaselevels)
    def test_minor_dominates_micro(self, year, minor, micro, releaselevel):
        """
        Property: Minor version dominates micro version.
        """
        assume(minor < 999)
        v1 = VersionInfo(year, minor, micro, releaselevel)
        v2 = VersionInfo(year, minor + 1, 0, "dev0")

        assert v1 < v2

    @given(years, minors, micros, releaselevels)
    def test_micro_dominates_releaselevel(self, year, minor, micro, releaselevel):
        """
        Property: Micro version dominates release level.
        """
        assume(micro < 999)
        v1 = VersionInfo(year, minor, micro, "post2")
        v2 = VersionInfo(year, minor, micro + 1, "dev0")

        assert v1 < v2

    @given(version_infos())
    def test_comparison_with_invalid_type_returns_notimplemented(self, v):
        """
        Property: Comparing with invalid types returns NotImplemented.
        """
        # Comparing with string should return NotImplemented
        result = v.__eq__("not a version")
        assert result == NotImplemented

        result = v.__lt__("not a version")
        assert result == NotImplemented

    @given(version_infos())
    def test_comparison_with_invalid_tuple_length(self, v):
        """
        Property: Comparing with tuples of invalid length returns NotImplemented.
        """
        # Empty tuple
        result = v.__eq__(())
        assert result == NotImplemented

        # 5-element tuple
        result = v.__eq__((1, 2, 3, 4, 5))
        assert result == NotImplemented

    @given(years, minors, micros, st.one_of(st.just("final"), releaselevels))
    def test_from_version_string_roundtrip(self, year, minor, micro, releaselevel):
        """
        Property: Parsing a version string and converting back preserves structure.
        """
        # Build a valid version string
        if releaselevel == "final":
            version_str = f"{year}.{minor}.{micro}"
        else:
            version_str = f"{year}.{minor}.{micro}.{releaselevel}"

        v = VersionInfo._from_version_string(version_str)

        assert v.year == year
        assert v.minor == minor
        assert v.micro == micro
        if releaselevel == "final":
            assert v.releaselevel == "final"
        else:
            assert v.releaselevel == releaselevel

    @given(version_infos(), version_infos())
    def test_max_min_consistency(self, v1, v2):
        """
        Property: max and min work correctly with VersionInfo.
        """
        max_v = max(v1, v2)
        min_v = min(v1, v2)

        assert max_v >= v1 and max_v >= v2
        assert min_v <= v1 and min_v <= v2
        assert max_v >= min_v

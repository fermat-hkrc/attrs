# Property-Based Testing Coverage Summary

This document summarizes the property-based tests added to the attrs project.

## Overview

Added **80 new property-based tests** across 4 new test files, covering critical functionality in the attrs library that was previously tested only with example-based tests.

## New Test Files

### 1. `test_filters_pbt.py` (14 tests)
Tests for `attr.filters` module (include/exclude filters for asdict/astuple).

**Properties tested:**
- **Inverse relationship**: `include` and `exclude` are inverses - together they partition all fields
- **Type filtering**: Filters correctly select/reject values by type
- **Idempotence**: Applying the same filter multiple times has the same effect
- **Value preservation**: Filters don't modify values, only select which to include
- **Multiple names**: Filters work correctly with multiple field names
- **Attribute objects**: Filters work with Attribute objects, not just names
- **Consistency**: Filters work the same way with both `asdict` and `astuple`
- **Empty filters**: Edge cases with no arguments behave correctly
- **Nested classes**: Filters apply recursively to nested attrs classes

### 2. `test_version_info_pbt.py` (24 tests)
Tests for `attr._version_info.VersionInfo` class (version comparison and ordering).

**Properties tested:**
- **Equality properties**: Reflexive, symmetric, transitive
- **Ordering properties**: Reflexive, antisymmetric, transitive, total ordering
- **Consistency**: Less-than implies not greater, equal implies neither less nor greater
- **Hash consistency**: Hash values are consistent and equal objects have equal hashes
- **Tuple comparison**: VersionInfo correctly compares with tuples of various lengths
- **Roundtrip**: Converting to tuple and back preserves equality
- **Construction**: Constructor preserves input values
- **Immutability**: VersionInfo is frozen and cannot be modified
- **Component ordering**: Year > minor > micro > releaselevel in significance
- **Release level ordering**: dev0 < final < post1 < post2
- **String parsing**: `_from_version_string` correctly parses version strings
- **Max/min operations**: Work correctly with VersionInfo instances

### 3. `test_validators_pbt.py` (25 tests)
Tests for `attr.validators` module (validation functions).

**Properties tested:**

#### Comparison validators (lt, le, gt, ge):
- **Correctness**: Each validator accepts/rejects values according to its comparison
- **Relationships**: `lt` is stricter than `le`, `gt` is stricter than `ge`

#### Length validators (min_len, max_len):
- **Correctness**: Accept sequences within length bounds
- **Combination**: min_len + max_len creates a range validator
- **Type support**: Work on both lists and strings

#### in_ validator:
- **Correctness**: Accepts values in options, rejects others
- **Type support**: Works with lists, sets, and other containers
- **Completeness**: All options are valid values

#### instance_of validator:
- **Type checking**: Correctly validates instance types
- **Rejection**: Rejects wrong types
- **Multiple types**: Works with tuple of types

#### optional validator:
- **None handling**: Allows None values
- **Validation**: Validates non-None values correctly
- **Composition**: Works with other validators

#### not_ validator:
- **Inversion**: Correctly inverts validator logic

#### or_ validator:
- **Disjunction**: Passes if any sub-validator passes
- **Composition**: Works with multiple validator types

#### Validator composition:
- **Conjunction**: Multiple validators all must pass
- **Chaining**: Type and length validators can be chained

### 4. `test_setters_pbt.py` (17 tests)
Tests for `attr.setters` module (on_setattr hooks).

**Properties tested:**

#### pipe setter:
- **Identity**: Single identity setter returns value unchanged
- **Composition**: Multiple setters compose in order
- **Order matters**: Different orders produce different results
- **Empty pipe**: No setters acts as identity
- **Integration**: Works with convert and validate setters

#### frozen setter:
- **Immutability**: Prevents modification after initialization
- **Initialization**: Allows setting during __init__

#### validate setter:
- **Validation**: Accepts valid values, rejects invalid ones
- **No validator**: Acts as identity when no validator present
- **Preservation**: Original value preserved on validation failure

#### convert setter:
- **Conversion**: Applies converter function correctly
- **No converter**: Acts as identity when no converter present
- **Type conversion**: Performs type conversions correctly
- **Idempotence**: Idempotent converters work correctly

#### Setter combinations:
- **Convert then validate**: Ensures converted value is valid
- **Order matters**: Validate-then-convert vs convert-then-validate produce different results

## Property Types Used

The tests employ various property-based testing patterns:

1. **Algebraic properties**: Reflexivity, symmetry, transitivity, associativity, commutativity
2. **Inverse operations**: encode/decode, include/exclude
3. **Idempotence**: Applying operation multiple times has same effect as once
4. **Invariants**: Properties that hold before and after operations
5. **Consistency**: Operations behave consistently across different contexts
6. **Boundary conditions**: Edge cases like empty inputs, None values
7. **Composition**: Properties of combined operations
8. **Correctness**: Operations produce expected results for all inputs

## Benefits

These property-based tests provide:

1. **Broader coverage**: Test thousands of input combinations automatically
2. **Edge case discovery**: Hypothesis finds corner cases developers might miss
3. **Regression prevention**: Properties ensure behavior remains consistent
4. **Documentation**: Properties serve as executable specifications
5. **Confidence**: Mathematical properties provide strong correctness guarantees

## Running the Tests

```bash
# Run all new property-based tests
pytest tests/test_filters_pbt.py tests/test_version_info_pbt.py tests/test_validators_pbt.py tests/test_setters_pbt.py -v

# Run with coverage
pytest tests/test_*_pbt.py --cov=attr --cov-report=html

# Run with specific Hypothesis settings
pytest tests/test_*_pbt.py --hypothesis-seed=12345
```

## Test Statistics

- **Total new tests**: 80
- **Total test files**: 4
- **Lines of test code**: ~700
- **Functions covered**: 20+
- **Execution time**: ~6 seconds (all tests)

## Integration with Existing Tests

These property-based tests complement the existing example-based tests in:
- `test_converters.py`
- `test_funcs.py`
- `test_validators.py`
- `test_make.py`

The property-based tests focus on mathematical properties and invariants, while example-based tests cover specific use cases and regression scenarios.

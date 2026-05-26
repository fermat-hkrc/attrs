# Quick Reference: Property-Based Tests for attrs

## Test Files Overview

| File | Tests | Module Tested | Key Focus |
|------|-------|---------------|-----------|
| `test_filters_pbt.py` | 14 | `attr.filters` | Include/exclude filter properties |
| `test_version_info_pbt.py` | 24 | `attr._version_info` | Version comparison & ordering |
| `test_validators_pbt.py` | 25 | `attr.validators` | Validator correctness & composition |
| `test_setters_pbt.py` | 17 | `attr.setters` | Setter hooks & composition |
| **Total** | **80** | | |

## Running Tests

```bash
# All new property-based tests
pytest tests/test_*_pbt.py -v

# Specific module
pytest tests/test_filters_pbt.py -v

# With coverage
pytest tests/test_*_pbt.py --cov=attr --cov-report=term-missing

# Quick run (quiet mode)
pytest tests/test_*_pbt.py -q

# With specific Hypothesis seed (for reproducibility)
pytest tests/test_*_pbt.py --hypothesis-seed=12345
```

## Key Properties Tested

### Filters (`test_filters_pbt.py`)
- ✓ Include/exclude are inverses
- ✓ Type-based filtering
- ✓ Idempotence
- ✓ Value preservation
- ✓ Nested class recursion

### VersionInfo (`test_version_info_pbt.py`)
- ✓ Equality: reflexive, symmetric, transitive
- ✓ Ordering: total, transitive, antisymmetric
- ✓ Hash consistency
- ✓ Tuple comparison
- ✓ Component precedence
- ✓ Immutability

### Validators (`test_validators_pbt.py`)
- ✓ Comparison validators (lt, le, gt, ge)
- ✓ Length validators (min_len, max_len)
- ✓ Membership (in_)
- ✓ Type checking (instance_of)
- ✓ Optional handling
- ✓ Logical operations (not_, or_)
- ✓ Composition

### Setters (`test_setters_pbt.py`)
- ✓ Pipe composition
- ✓ Frozen immutability
- ✓ Validate correctness
- ✓ Convert application
- ✓ Setter combinations

## Example Properties

### Inverse Operations
```python
# Include and exclude partition fields
include(x) ∪ exclude(x) = all_fields
include(x) ∩ exclude(x) = ∅
```

### Transitivity
```python
# Ordering is transitive
∀ v1, v2, v3: (v1 ≤ v2 ∧ v2 ≤ v3) → v1 ≤ v3
```

### Composition
```python
# Pipe composes in order
pipe(f, g)(x) = g(f(x))
```

### Idempotence
```python
# Filters are idempotent
filter(filter(x)) = filter(x)
```

## Test Results

```
✓ test_filters_pbt.py:        14/14 passed
✓ test_version_info_pbt.py:   24/24 passed
✓ test_validators_pbt.py:     25/25 passed
✓ test_setters_pbt.py:        17/17 passed
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total:                      80/80 passed ✓
```

## Documentation

- `PBT_COVERAGE_SUMMARY.md` - Detailed coverage summary
- `PBT_IMPLEMENTATION_REPORT.md` - Full implementation report
- `QUICK_REFERENCE.md` - This file

## Integration

These tests integrate seamlessly with the existing test suite:
- No source code changes required
- No configuration changes needed
- Compatible with existing CI/CD pipelines
- Uses same Hypothesis configuration as existing tests

## Benefits

1. **Broader coverage**: Tests thousands of input combinations
2. **Edge case discovery**: Hypothesis finds corner cases automatically
3. **Mathematical rigor**: Properties provide strong correctness guarantees
4. **Living documentation**: Properties serve as executable specifications
5. **Regression prevention**: Ensures behavior consistency across changes

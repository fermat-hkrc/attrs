# attrs ccode PBT Mutation Score Report

## Overall Score: 58.8%

**Summary:**
- **Killed:** 60
- **Survived:** 42
- **Timeout:** 0
- **Error:** 0
- **Tested:** 102
- **Total:** 102

**Runtime:** 452.62 seconds (~7.5 minutes)

## Per-Target Breakdown

| Target | Killed | Tested | Score | Status |
|--------|--------|--------|-------|--------|
| **filters.exclude** | 8 | 8 | **100.0%** | ✅ Perfect |
| **filters.include** | 7 | 7 | **100.0%** | ✅ Perfect |
| **validators.instance_of** | 1 | 1 | **100.0%** | ✅ Perfect |
| **validators.max_len** | 1 | 1 | **100.0%** | ✅ Perfect |
| **validators.min_len** | 1 | 1 | **100.0%** | ✅ Perfect |
| **setters.validate** | 9 | 10 | **90.0%** | ✅ Excellent |
| **setters.pipe** | 7 | 8 | **87.5%** | ✅ Good |
| **validators.ge** | 5 | 7 | **71.4%** | ⚠️ Decent |
| **validators.gt** | 5 | 7 | **71.4%** | ⚠️ Decent |
| **validators.le** | 5 | 7 | **71.4%** | ⚠️ Decent |
| **validators.lt** | 5 | 7 | **71.4%** | ⚠️ Decent |
| **setters.convert** | 3 | 9 | **33.3%** | ❌ Weak |
| **validators.deep_iterable** | 2 | 6 | **33.3%** | ❌ Weak |
| **validators.optional** | 1 | 3 | **33.3%** | ❌ Weak |
| **validators.deep_mapping** | 0 | 10 | **0.0%** | ❌ Critical Gap |
| **validators.matches_re** | 0 | 10 | **0.0%** | ❌ Critical Gap |

## Test Suite Info

**Test Files:**
- `tests/test_validators_pbt.py` (536 lines)
- `tests/test_filters_pbt.py` (235 lines)
- `tests/test_setters_pbt.py` (410 lines)

**Total:** 80 PBT tests, 1,487 lines

## Highlights

### ✅ Perfect Coverage (100%)
5 targets with perfect mutation killing:
- All filter functions (include, exclude)
- Basic validators (instance_of, min_len, max_len)

### ⚠️ Decent Coverage (70-90%)
5 targets with good but improvable coverage:
- Comparison validators (lt, le, gt, ge) all at 71.4%
- Setter functions (validate 90%, pipe 87.5%)

### ❌ Critical Gaps (0-33%)
6 targets with significant weaknesses:
- **validators.deep_mapping**: 0% (0/10) - no mutants killed
- **validators.matches_re**: 0% (0/10) - no mutants killed
- **validators.deep_iterable**: 33.3% (2/6)
- **validators.optional**: 33.3% (1/3)
- **setters.convert**: 33.3% (3/9)

## Analysis

### Strengths
1. **Filters are well-tested** - 100% coverage on both include/exclude
2. **Basic validators work** - Simple validators have perfect coverage
3. **No timeouts or errors** - All mutants completed successfully

### Weaknesses
1. **Complex validators untested** - deep_mapping and matches_re have 0% coverage
2. **Regex validation gap** - matches_re has 10 mutants, none killed
3. **Deep structure gap** - deep_mapping has 10 mutants, none killed
4. **Converter weakness** - setters.convert only catches 33% of bugs

### Recommendations

**Priority 1: Fix 0% targets**
```python
# Add tests for validators.deep_mapping
@given(st.dictionaries(st.text(), st.integers()))
def test_deep_mapping_validates_nested_dicts(mapping):
    # Test that deep_mapping catches invalid nested values
    ...

# Add tests for validators.matches_re
@given(st.text())
def test_matches_re_validates_patterns(text):
    # Test regex validation with various patterns
    ...
```

**Priority 2: Improve weak targets (33%)**
- Add edge cases for `validators.optional`
- Test `validators.deep_iterable` with nested structures
- Test `setters.convert` with various conversion scenarios

**Priority 3: Push decent targets to 90%+**
- Add boundary tests for comparison validators (lt, le, gt, ge)

## Comparison with arrow

| Metric | attrs (ccode) | arrow (ccode) |
|--------|---------------|---------------|
| Overall Score | **58.8%** | **60.1%** |
| Tests | 80 | 99 |
| Mutants Tested | 102 | 752 |
| Perfect Targets | 5/16 (31%) | 6/17 (35%) |
| Zero Score Targets | 2/16 (13%) | 1/17 (6%) |

**Similar quality** - Both ccode suites achieve ~60% mutation score, indicating consistent test quality from the ccode agent.

## Next Steps

1. ✅ **Document results** - This report
2. ⏳ **Compare with self-evolve** - Waiting for self-evolve attrs PBT tests
3. 🎯 **Fix critical gaps** - Add tests for 0% targets
4. 📊 **Track improvements** - Re-run after adding tests

---

**Generated:** 2025-05-26
**Tool:** mutmut + custom runner
**Config:** max 10 mutants per target, 120s timeout

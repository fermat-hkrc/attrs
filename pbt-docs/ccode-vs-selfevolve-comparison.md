# attrs PBT Mutation Score Comparison: ccode vs self-evolve

## Setup

Both suites were tested against the **same 66 mutants** (max 5 per target)
generated from the same source files using the `pbt-scorer` framework.

| | ccode | self-evolve |
|--|--|--|
| **Branch** | `ccode` @ `fermat-hkrc/attrs` | `self-evolve` @ `fermat-hkrc/attrs` |
| **Test file** | `tests/test_validators_pbt.py` + `test_filters_pbt.py` + `test_setters_pbt.py` | `tests/test_pbt_attrs.py` |
| **Test count** | 80 | 143 |
| **Lines of code** | 1,487 | ~900 |

## Overall Score

| Metric | ccode | self-evolve | Δ |
|--------|-------|-------------|---|
| **Mutation Score** | **66.7%** | **69.7%** | **+3.0pp** ✅ |
| Killed | 44 | 46 | +2 |
| Survived | 22 | 20 | -2 |
| Timeout | 0 | 0 | — |
| Error | 0 | 0 | — |
| Tested | 66 | 66 | — |
| Runtime | ~2.5 min | ~4.7 min | +2.2 min |

## Per-Target Breakdown

| Target | ccode | self-evolve | Δ | Winner |
|--------|-------|-------------|---|--------|
| `filters.exclude` | 100% (5/5) | 100% (5/5) | 0pp | 🤝 Tie |
| `filters.include` | 100% (5/5) | 100% (5/5) | 0pp | 🤝 Tie |
| `setters.validate` | 100% (5/5) | 100% (5/5) | 0pp | 🤝 Tie |
| `validators.instance_of` | 100% (1/1) | 100% (1/1) | 0pp | 🤝 Tie |
| `validators.max_len` | 100% (1/1) | 100% (1/1) | 0pp | 🤝 Tie |
| `validators.min_len` | 100% (1/1) | 100% (1/1) | 0pp | 🤝 Tie |
| `validators.ge` | 80% (4/5) | 80% (4/5) | 0pp | 🤝 Tie |
| `validators.gt` | 80% (4/5) | 80% (4/5) | 0pp | 🤝 Tie |
| `validators.le` | 80% (4/5) | 80% (4/5) | 0pp | 🤝 Tie |
| `validators.lt` | 80% (4/5) | 80% (4/5) | 0pp | 🤝 Tie |
| `validators.deep_iterable` | 40% (2/5) | 40% (2/5) | 0pp | 🤝 Tie |
| **`validators.optional`** | **33.3% (1/3)** | **100% (3/3)** | **+66.7pp** | 🏆 self-evolve |
| **`validators.deep_mapping`** | **0% (0/5)** | **20% (1/5)** | **+20.0pp** | 🏆 self-evolve |
| **`validators.matches_re`** | **0% (0/5)** | **20% (1/5)** | **+20.0pp** | 🏆 self-evolve |
| **`setters.pipe`** | **80% (4/5)** | **60% (3/5)** | **-20.0pp** | 🏆 ccode |
| **`setters.convert`** | **60% (3/5)** | **40% (2/5)** | **-20.0pp** | 🏆 ccode |

## Summary

| Outcome | Count | Targets |
|---------|-------|---------|
| 🏆 self-evolve wins | 3 | `validators.optional`, `validators.deep_mapping`, `validators.matches_re` |
| 🏆 ccode wins | 2 | `setters.pipe`, `setters.convert` |
| 🤝 Tie | 11 | All others |

## Analysis

### Where self-evolve is better

1. **`validators.optional` (+66.7pp)** — self-evolve covers all 3 mutants perfectly
   vs ccode only killing 1/3.
2. **`validators.deep_mapping` (+20pp)** and **`validators.matches_re` (+20pp)**
   — both at 0% in ccode; self-evolve at least kills 1/5 in each.
   These remain the weakest targets for both agents.

### Where ccode is better

1. **`setters.pipe` (-20pp)** and **`setters.convert` (-20pp)** — ccode has
   dedicated test files for setters (`test_setters_pbt.py`) which appear to
   cover setter logic more precisely.

### Common weaknesses

Both suites share zero-or-low coverage on:
- `validators.deep_mapping` (0% ccode, 20% self-evolve)
- `validators.matches_re` (0% ccode, 20% self-evolve)
- `validators.deep_iterable` (40% both)

These are the best candidates for improving test quality in either suite.

## Conclusion

**self-evolve wins overall (+3.0pp)** on attrs, driven mainly by better
`validators.optional` coverage. However ccode wins on setter targets.

The difference is small (3pp) and within sampling noise for 5 mutants/target.
A more reliable comparison would require at least 20 mutants/target.

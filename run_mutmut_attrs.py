from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path


# Target functions to test - focusing on main utility functions
TARGET_IDS = {
    "validators.instance_of",
    "validators.in_",
    "validators.optional",
    "validators.matches_re",
    "validators.lt",
    "validators.le",
    "validators.gt",
    "validators.ge",
    "validators.min_len",
    "validators.max_len",
    "validators.deep_iterable",
    "validators.deep_mapping",
    "validators.and_",
    "validators.not_",
    "filters.include",
    "filters.exclude",
    "setters.frozen",
    "setters.validate",
    "setters.convert",
    "setters.pipe",
}

MUTANTS_DIR = Path("mutants")
RESULTS_JSON = Path("pbt-docs/mutmut-pbt-mutation-results.json")
REPORT_MD = Path("pbt-docs/mutmut-pbt-mutation-score.md")
TEST_FILES = [
    Path("tests/test_validators_pbt.py"),
    Path("tests/test_filters_pbt.py"),
    Path("tests/test_setters_pbt.py"),
]


@dataclass(frozen=True)
class Mutant:
    name: str
    source_path: Path


@dataclass(frozen=True)
class MutationResult:
    name: str
    source_path: Path
    status: str
    seconds: float
    detail: str = ""


@dataclass(frozen=True)
class MutationSummary:
    total: int
    killed: int
    survived: int
    timeout: int
    error: int
    tested: int
    mutation_score: float


def source_files_for_targets() -> list[Path]:
    """Return source files to mutate for attrs."""
    return [
        Path("src/attr/validators.py"),
        Path("src/attr/filters.py"),
        Path("src/attr/setters.py"),
    ]


def mutant_function_key(mutant_name: str) -> str:
    key = mutant_name.rsplit("__mutmut_", 1)[0]
    key = key.rsplit(".", 1)[-1]
    if key.startswith("x_"):
        key = key[2:]
    if "ǁ" in key:
        key = key.split("ǁ")[-1]
    return key.strip("_")


def normalize_target_id(source_path: Path, function_key: str) -> str | None:
    """Map source file + function to target ID."""
    if source_path == Path("src/attr/validators.py"):
        return f"validators.{function_key}"
    elif source_path == Path("src/attr/filters.py"):
        return f"filters.{function_key}"
    elif source_path == Path("src/attr/setters.py"):
        return f"setters.{function_key}"
    return None


def filter_mutants_to_targets(mutants: list[Mutant]) -> tuple[list[Mutant], list[Mutant]]:
    kept: list[Mutant] = []
    skipped: list[Mutant] = []
    for mutant in mutants:
        normalized = normalize_target_id(mutant.source_path, mutant_function_key(mutant.name))
        if normalized in TARGET_IDS:
            kept.append(mutant)
        else:
            skipped.append(mutant)
    return kept, skipped


def discover_mutants(mutants_dir: Path) -> list[Mutant]:
    mutants: list[Mutant] = []
    for meta_path in sorted(mutants_dir.rglob("*.py.meta")):
        data = json.loads(meta_path.read_text())
        source_path = meta_path.relative_to(mutants_dir).with_suffix("")
        for name in sorted(data.get("exit_code_by_key", {}).keys()):
            mutants.append(Mutant(name=name, source_path=source_path))
    return mutants


def _mutmut_main():
    import mutmut.__main__ as mm
    return mm


def generate_mutants(
    mutants_dir: Path = MUTANTS_DIR,
    max_mutants: int | None = None,
    max_mutants_per_target: int | None = None,
) -> None:
    mm = _mutmut_main()
    original_load_config = mm.load_config
    source_files = source_files_for_targets()

    def patched_load_config():
        cfg = original_load_config()
        cfg.paths_to_mutate = source_files
        cfg.also_copy = []
        return cfg

    mm.load_config = patched_load_config
    mm.ensure_config_loaded()
    mutants_dir.mkdir(parents=True, exist_ok=True)
    mm.copy_src_dir()
    mm.create_mutants(1)

    if max_mutants_per_target is not None:
        retained, _ = filter_mutants_to_targets(discover_mutants(mutants_dir))
        per_target: dict[str, int] = {}
        keep_names: set[str] = set()
        for mutant in retained:
            t = normalize_target_id(mutant.source_path, mutant_function_key(mutant.name))
            if t is None:
                continue
            if per_target.get(t, 0) >= max_mutants_per_target:
                continue
            per_target[t] = per_target.get(t, 0) + 1
            keep_names.add(mutant.name)
        for meta_path in sorted(mutants_dir.rglob("*.py.meta")):
            data = json.loads(meta_path.read_text())
            keys = data.get("exit_code_by_key", {})
            data["exit_code_by_key"] = {
                key: value for key, value in sorted(keys.items()) if key in keep_names
            }
            meta_path.write_text(json.dumps(data))
        print(f"limited mutants per target to {max_mutants_per_target}; kept {len(keep_names)}")
    elif max_mutants is not None:
        retained, _ = filter_mutants_to_targets(discover_mutants(mutants_dir))
        keep_names = {mutant.name for mutant in retained[:max_mutants]}
        for meta_path in sorted(mutants_dir.rglob("*.py.meta")):
            data = json.loads(meta_path.read_text())
            keys = data.get("exit_code_by_key", {})
            data["exit_code_by_key"] = {
                key: value for key, value in sorted(keys.items()) if key in keep_names
            }
            meta_path.write_text(json.dumps(data))
        print(f"limited mutants to {len(keep_names)}")


def summarize_results(results: list[MutationResult]) -> MutationSummary:
    killed = sum(r.status == "killed" for r in results)
    survived = sum(r.status == "survived" for r in results)
    timeout = sum(r.status == "timeout" for r in results)
    error = sum(r.status == "error" for r in results)
    tested = killed + survived + timeout
    mutation_score = (100.0 * killed / tested) if tested else 0.0
    return MutationSummary(
        total=len(results),
        killed=killed,
        survived=survived,
        timeout=timeout,
        error=error,
        tested=tested,
        mutation_score=mutation_score,
    )


def pytest_command() -> list[str]:
    return ["uv", "run", "pytest"] + [str(f) for f in TEST_FILES] + ["-q", "-x"]


def run_pytest_suite(timeout_seconds: int) -> tuple[str, float, str]:
    start = time.perf_counter()
    try:
        proc = subprocess.run(
            pytest_command(),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        elapsed = time.perf_counter() - start
        detail = ((proc.stdout or "") + "\n" + (proc.stderr or "")).strip()
        status = "survived" if proc.returncode == 0 else "killed"
        return status, elapsed, detail
    except subprocess.TimeoutExpired as exc:
        elapsed = time.perf_counter() - start
        detail = ((exc.stdout or "") + "\n" + (exc.stderr or "")).strip()
        return "timeout", elapsed, detail


def apply_mutant(mutant_name: str) -> None:
    subprocess.run([sys.executable, "-m", "mutmut", "apply", mutant_name], check=True)


def check_baseline(timeout_seconds: int = 60) -> None:
    status, _, detail = run_pytest_suite(timeout_seconds)
    if status != "survived":
        raise SystemExit(f"Baseline suite failed — fix tests before scoring.\n{detail}")


def score_mutants(
    mutants_dir: Path = MUTANTS_DIR,
    timeout_seconds: int = 300,
    limit: int | None = None,
    project_root: Path = Path("."),
) -> tuple[list[MutationResult], MutationSummary]:
    check_baseline()
    all_mutants = discover_mutants(mutants_dir)
    retained, _ = filter_mutants_to_targets(all_mutants)
    if limit is not None:
        retained = retained[:limit]

    results: list[MutationResult] = []
    source_files = {m.source_path for m in retained}
    originals = {sf: (project_root / sf).read_bytes() for sf in source_files}

    for i, mutant in enumerate(retained, 1):
        print(f"[{i}/{len(retained)}] testing {mutant.name}")
        try:
            apply_mutant(mutant.name)
            status, seconds, detail = run_pytest_suite(timeout_seconds)
            results.append(MutationResult(mutant.name, mutant.source_path, status, seconds, detail))
        except Exception as exc:
            results.append(MutationResult(mutant.name, mutant.source_path, "error", 0.0, str(exc)))
        finally:
            for sf, content in originals.items():
                (project_root / sf).write_bytes(content)

    summary = summarize_results(results)
    return results, summary


def write_results(
    results: list[MutationResult],
    summary: MutationSummary,
    results_json: Path = RESULTS_JSON,
    report_md: Path = REPORT_MD,
) -> None:
    results_json.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "summary": asdict(summary),
        "results": [{**asdict(r), "source_path": str(r.source_path)} for r in results],
    }
    results_json.write_text(json.dumps(data, indent=2))

    report_md.write_text(f"""# Mutation Score Report

**Overall Score:** {summary.mutation_score:.1f}%

- Total: {summary.total}
- Killed: {summary.killed}
- Survived: {summary.survived}
- Timeout: {summary.timeout}
- Error: {summary.error}
- Tested: {summary.tested}
""")
    print(f"wrote {results_json}")
    print(f"wrote {report_md}")


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    generate = sub.add_parser("generate")
    generate.add_argument("--max-mutants", type=int)
    generate.add_argument("--max-mutants-per-target", type=int)
    score = sub.add_parser("score")
    score.add_argument("--timeout", type=int, default=300)
    score.add_argument("--limit", type=int)
    args = parser.parse_args()

    if args.command == "generate":
        generate_mutants(
            max_mutants=args.max_mutants,
            max_mutants_per_target=args.max_mutants_per_target,
        )
        print("generated mutants")
        return

    if args.command == "score":
        results, summary = score_mutants(timeout_seconds=args.timeout, limit=args.limit)
        write_results(results, summary)
        print(f"mutation score: {summary.mutation_score:.1f}%")
        return


if __name__ == "__main__":
    main()

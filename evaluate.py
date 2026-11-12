"""Evaluate the Smart Task Parser against the golden dataset.

Usage:
    python evaluate.py              # live API calls (needs GOOGLE_API_KEY)
    python evaluate.py --dry-run    # schema/smoke only, no network

Reports:
  - schema adherence  (response validates as Task)
  - category accuracy
  - priority accuracy
  - field accuracy    (mean of category + priority)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from categoriser import categorise
from models import Category, Priority

DATASET_PATH = Path(__file__).resolve().parent / "tests" / "golden_dataset.json"


def _load_dotenv() -> None:
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        return
    import os

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def evaluate(dry_run: bool = False) -> int:
    dataset = json.loads(DATASET_PATH.read_text(encoding="utf-8"))

    schema_ok = 0
    cat_ok = 0
    pri_ok = 0
    attempted = 0
    skipped = 0
    failed = 0

    print(f"Evaluating {len(dataset)} tasks (dry_run={dry_run})\n")

    for entry in dataset:
        task = entry["task"]
        expected_cat = entry["expected_category"]
        expected_pri = entry["expected_priority"]
        try:
            result = categorise(task, dry_run=dry_run)
            attempted += 1
            schema_ok += 1

            cat_match = result.category == Category(expected_cat)
            pri_match = result.priority == Priority(expected_pri)
            cat_ok += int(cat_match)
            pri_ok += int(pri_match)

            status = "OK" if cat_match and pri_match else "MISS"
            print(
                f"[{status}] {task!r}\n"
                f"       got  cat={result.category.value} pri={result.priority.value} "
                f"conf={result.confidence:.2f} amb={result.is_ambiguous}\n"
                f"       want cat={expected_cat} pri={expected_pri}"
            )
        except Exception as exc:  # noqa: BLE001
            msg = str(exc)
            if any(t in msg for t in ("RESOURCE_EXHAUSTED", "rate limited", "503", "504")):
                print(f"[SKIP] {task!r} — API transient: {exc}")
                skipped += 1
                continue
            print(f"[FAIL] {task!r} — {exc}")
            failed += 1

    print("\n--- Summary ---")
    if attempted == 0:
        print("No tasks evaluated (all skipped or failed before a valid response).")
        return 1

    print(f"Schema adherence:  {schema_ok}/{attempted} ({100 * schema_ok / attempted:.1f}%)")
    print(f"Category accuracy: {cat_ok}/{attempted} ({100 * cat_ok / attempted:.1f}%)")
    print(f"Priority accuracy: {pri_ok}/{attempted} ({100 * pri_ok / attempted:.1f}%)")
    field_total = attempted * 2
    field_ok = cat_ok + pri_ok
    print(f"Field accuracy:    {field_ok}/{field_total} ({100 * field_ok / field_total:.1f}%)")
    print(f"Failed (hard):     {failed}")
    print(f"Skipped (API):     {skipped}")

    # dry-run always returns Other/Low, so accuracy will be low — that is expected
    if dry_run:
        print("\nNote: --dry-run uses a local heuristic fallback (Other/Low). "
              "Accuracy numbers are not meaningful in this mode.")
    return 0 if failed == 0 else 1


def main(argv=None) -> int:
    _load_dotenv()
    p = argparse.ArgumentParser(description="Evaluate against the golden dataset.")
    p.add_argument("--dry-run", action="store_true", help="No API calls")
    args = p.parse_args(argv)
    return evaluate(dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())

"""Interactive demo of the Smart Task Parser.

Runs a handful of sample tasks so a reviewer can see live output without
having to invent inputs. Requires GOOGLE_API_KEY (or .env).

    python demo.py
    python demo.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from categoriser import categorise


SAMPLES = [
    "Buy milk before Thursday",
    "Finish the quarterly report by EOD Friday",
    "Call mum this weekend",
    "Pay the electricity bill",
    "Schedule a dentist appointment",
    "This task is really vague, just do something I guess??",
]


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


def main(argv=None) -> int:
    _load_dotenv()
    p = argparse.ArgumentParser(description="Run sample tasks through the parser.")
    p.add_argument("--dry-run", action="store_true", help="No API calls")
    p.add_argument("--json", action="store_true", help="Print JSON only")
    args = p.parse_args(argv)

    print("SWYNEX Smart Task Parser — demo\n" + "-" * 40)
    for sample in SAMPLES:
        print(f"\nIN:  {sample}")
        try:
            result = categorise(sample, dry_run=args.dry_run)
        except RuntimeError as exc:
            print(f"ERR: {exc}", file=sys.stderr)
            return 2
        if args.json:
            print("OUT:", json.dumps(result.model_dump(), indent=2))
        else:
            flag = " [AMBIGUOUS]" if result.is_ambiguous else ""
            print(
                f"OUT: {result.task_description}\n"
                f"     category={result.category.value}  "
                f"priority={result.priority.value}  "
                f"deadline={result.deadline or 'none'}  "
                f"confidence={result.confidence:.2f}{flag}"
            )
    print("\n" + "-" * 40 + "\nDone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

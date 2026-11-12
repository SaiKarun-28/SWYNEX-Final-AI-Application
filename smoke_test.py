"""Offline self-check for the Smart Task Parser.

No frameworks, no API key, no network. Fails loudly if the schema, enum
coercion, prompt assembly, or ambiguity logic regresses.

Run:  python smoke_test.py
"""

from __future__ import annotations

import json
import sys

from categoriser import (
    AMBIGUITY_THRESHOLD,
    FEW_SHOTS,
    SYSTEM_PROMPT,
    _finalise,
    _normalise_schema,
    build_messages,
)
from models import Category, Priority, Task


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def run() -> None:
    # 1. Schema round-trips and enforces enums.
    t = Task(
        task_description="Buy milk",
        category="Shopping",
        priority="Medium",
        deadline=None,
        confidence=0.9,
        is_ambiguous=False,
    )
    _check(t.category is Category.Shopping, "category should coerce to enum")
    _check(t.priority is Priority.Medium, "priority should coerce to enum")
    dump = json.loads(t.model_dump_json())
    _check(dump["category"] == "Shopping", "enum must serialise as plain string")
    _check(dump["deadline"] is None, "null deadline must stay null")

    # 2. Invalid enum / missing field / out-of-range confidence all fail loudly.
    for bad in [
        {
            "task_description": "x",
            "category": "Teleporting",
            "priority": "Medium",
            "deadline": None,
            "confidence": 0.9,
            "is_ambiguous": False,
        },
        {
            "task_description": "x",
            "category": "Shopping",
            "priority": "Medium",
            "deadline": None,
            "confidence": 9.0,
            "is_ambiguous": False,
        },
        {
            "category": "Shopping",
            "priority": "Medium",
            "deadline": None,
            "confidence": 0.9,
        },  # missing required task_description
    ]:
        try:
            Task(**bad)
        except Exception:
            pass
        else:
            raise AssertionError(f"expected validation failure: {bad}")

    # 3. Prompt + few-shots are well-formed and the schema matches the model.
    _check(isinstance(SYSTEM_PROMPT, str) and len(SYSTEM_PROMPT) > 50, "system prompt missing")
    messages = build_messages("Buy milk before Thursday")
    _check(messages[0]["role"] == "user", "first few-shot must be a user turn")
    _check(messages[-1]["role"] == "user", "last message must be the user task")
    _check(
        len(messages) == 1 + len(FEW_SHOTS),
        "few-shot count must be preserved (few-shots + current user)",
    )
    schema = Task.model_json_schema()
    for prop in (
        "task_description",
        "category",
        "priority",
        "deadline",
        "confidence",
        "is_ambiguous",
    ):
        _check(prop in schema["properties"], f"schema missing field {prop}")

    # 4. Ambiguity threshold logic.
    low = Task(
        task_description="d",
        category=Category.Other,
        priority=Priority.Low,
        deadline=None,
        confidence=0.4,
        is_ambiguous=False,
    )
    final = _finalise(low)
    _check(final.is_ambiguous is True, "low confidence must flag ambiguous")
    high = Task(
        task_description="d",
        category=Category.Work,
        priority=Priority.High,
        deadline=None,
        confidence=0.95,
        is_ambiguous=False,
    )
    _check(_finalise(high).is_ambiguous is False, "high confidence must not flag ambiguous")
    _check(0.0 <= AMBIGUITY_THRESHOLD <= 1.0, "threshold must be in range")

    # 5. Schema normaliser strips Pydantic keys Gemini rejects.
    clean = _normalise_schema(Task.model_json_schema())
    _check("title" not in clean, "normaliser must strip Pydantic 'title'")
    _check("properties" in clean, "normaliser must preserve schema structure")

    # 6. Empty / oversized inputs rejected.
    from categoriser import categorise

    try:
        categorise("   ", dry_run=True)
    except RuntimeError:
        pass
    else:
        raise AssertionError("empty task must raise")

    try:
        categorise("x" * 2000, dry_run=True)
    except RuntimeError:
        pass
    else:
        raise AssertionError("oversized task must raise")

    print("smoke_test: OK")


if __name__ == "__main__":
    try:
        run()
    except AssertionError as exc:
        print(f"smoke_test: FAIL — {exc}", file=sys.stderr)
        sys.exit(1)

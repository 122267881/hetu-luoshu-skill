#!/usr/bin/env python3
"""Deterministically validate the numerical Hetu and Luoshu models."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, asdict


HETU_PAIRS = {
    "water": (1, 6),
    "fire": (2, 7),
    "wood": (3, 8),
    "metal": (4, 9),
    "earth": (5, 10),
}

LUOSHU = (
    (4, 9, 2),
    (3, 5, 7),
    (8, 1, 6),
)


@dataclass(frozen=True)
class ValidationResult:
    name: str
    passed: bool
    checks: dict[str, object]
    issues: list[str]


def validate_hetu() -> ValidationResult:
    issues: list[str] = []
    pair_differences = {name: formed - generated for name, (generated, formed) in HETU_PAIRS.items()}
    if set(pair_differences.values()) != {5}:
        issues.append("Every Hetu generated/formed pair must differ by 5.")

    odd_sum = sum(range(1, 10, 2))
    even_sum = sum(range(2, 11, 2))
    total = odd_sum + even_sum
    if (odd_sum, even_sum, total) != (25, 30, 55):
        issues.append("Hetu odd/even totals must be 25, 30, and 55.")

    return ValidationResult(
        name="hetu",
        passed=not issues,
        checks={
            "pairs": HETU_PAIRS,
            "pair_differences": pair_differences,
            "odd_sum": odd_sum,
            "even_sum": even_sum,
            "total": total,
        },
        issues=issues,
    )


def validate_luoshu() -> ValidationResult:
    issues: list[str] = []
    rows = [list(row) for row in LUOSHU]
    columns = [[LUOSHU[r][c] for r in range(3)] for c in range(3)]
    diagonals = [
        [LUOSHU[i][i] for i in range(3)],
        [LUOSHU[i][2 - i] for i in range(3)],
    ]
    line_sums = [sum(line) for line in rows + columns + diagonals]
    if line_sums != [15] * 8:
        issues.append("All eight Luoshu line sums must equal 15.")

    flattened = [value for row in LUOSHU for value in row]
    if sorted(flattened) != list(range(1, 10)):
        issues.append("Luoshu must contain each integer from 1 through 9 exactly once.")

    opposite_pairs = {
        "north_south": LUOSHU[0][1] + LUOSHU[2][1],
        "east_west": LUOSHU[1][0] + LUOSHU[1][2],
        "northwest_southeast": LUOSHU[0][0] + LUOSHU[2][2],
        "northeast_southwest": LUOSHU[0][2] + LUOSHU[2][0],
    }
    if set(opposite_pairs.values()) != {10}:
        issues.append("Every opposite Luoshu pair must sum to 10.")
    if LUOSHU[1][1] != 5:
        issues.append("The Luoshu center must be 5.")

    return ValidationResult(
        name="luoshu",
        passed=not issues,
        checks={
            "grid": LUOSHU,
            "line_sums": line_sums,
            "opposite_pair_sums": opposite_pairs,
            "center": LUOSHU[1][1],
        },
        issues=issues,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()

    results = [validate_hetu(), validate_luoshu()]
    passed = all(result.passed for result in results)

    if args.json:
        print(json.dumps(
            {"passed": passed, "results": [asdict(result) for result in results]},
            ensure_ascii=False,
            indent=2,
        ))
    else:
        for result in results:
            print(f"{result.name}: {'PASS' if result.passed else 'FAIL'}")
            for issue in result.issues:
                print(f"- {issue}")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())

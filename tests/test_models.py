from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_models import HETU_PAIRS, LUOSHU, validate_hetu, validate_luoshu


class ModelTests(unittest.TestCase):
    def test_hetu_pairs_differ_by_five(self) -> None:
        self.assertTrue(all(formed - generated == 5 for generated, formed in HETU_PAIRS.values()))

    def test_hetu_totals(self) -> None:
        result = validate_hetu()
        self.assertTrue(result.passed)
        self.assertEqual(result.checks["odd_sum"], 25)
        self.assertEqual(result.checks["even_sum"], 30)
        self.assertEqual(result.checks["total"], 55)

    def test_luoshu_magic_constant(self) -> None:
        result = validate_luoshu()
        self.assertTrue(result.passed)
        self.assertEqual(result.checks["line_sums"], [15] * 8)

    def test_luoshu_opposites(self) -> None:
        result = validate_luoshu()
        self.assertEqual(set(result.checks["opposite_pair_sums"].values()), {10})
        self.assertEqual(LUOSHU[1][1], 5)


if __name__ == "__main__":
    unittest.main()

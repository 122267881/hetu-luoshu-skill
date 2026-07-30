from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "knowledge-base.json"

sys.path.insert(0, str(ROOT / "scripts"))


class KnowledgeSystemTests(unittest.TestCase):
    def test_v2_required_assets_exist(self) -> None:
        required = {
            "VERSION",
            "CHANGELOG.md",
            "data/knowledge-base.json",
            "scripts/knowledge_cli.py",
            "references/terminology-map.md",
            "references/classics-and-reception.md",
            "references/song-diagram-history.md",
            "references/correspondences-and-derivations.md",
            "references/mathematics-and-symmetry.md",
            "references/research-protocol.md",
            "references/teaching-and-content.md",
            "examples/product-system-model.md",
            "examples/content-audit.md",
        }
        missing = sorted(rel for rel in required if not (ROOT / rel).is_file())
        self.assertEqual(missing, [])

    def test_knowledge_base_claims_are_traceable(self) -> None:
        data = json.loads(DATA.read_text(encoding="utf-8"))
        self.assertEqual(data["schema_version"], 2)
        sources = {source["id"] for source in data["sources"]}
        self.assertGreaterEqual(len(data["terms"]), 20)
        self.assertGreaterEqual(len(data["claims"]), 25)
        for claim in data["claims"]:
            self.assertIn(claim["evidence"], {"P", "H", "T", "M", "A", "U"})
            self.assertTrue(claim["source_ids"])
            self.assertTrue(set(claim["source_ids"]).issubset(sources))
            self.assertIn(claim["confidence"], {"high", "medium", "low", "contested"})

    def test_luoshu_has_eight_unique_dihedral_symmetries(self) -> None:
        from knowledge_cli import luoshu_symmetries

        grids = luoshu_symmetries()
        self.assertEqual(len(grids), 8)
        normalized = {tuple(value for row in grid for value in row) for grid in grids}
        self.assertEqual(len(normalized), 8)

    def test_every_luoshu_symmetry_remains_magic(self) -> None:
        from knowledge_cli import is_magic_square, luoshu_symmetries

        for grid in luoshu_symmetries():
            self.assertTrue(is_magic_square(grid))

    def test_cli_lookup_returns_structured_term(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/knowledge_cli.py", "lookup", "刘牧", "--json"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["term"], "刘牧")
        self.assertIn("宋代", payload["summary"])
        self.assertTrue(payload["claim_ids"])

    def test_claim_auditor_flags_absolute_and_high_impact_claims(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/knowledge_cli.py",
                "audit-claim",
                "河图洛书是所有中华文化唯一源头，并能预测明日币价。",
                "--json",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 2)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["trust_gate"], "FAIL")
        self.assertIn("absolute-origin", payload["risk_codes"])
        self.assertIn("financial-prediction", payload["risk_codes"])

    def test_model_template_is_measurable_not_divinatory(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/knowledge_cli.py", "model-template", "产品系统"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        for marker in ("河图之体", "洛书之用", "现实变量", "验证指标", "失败信号", "停止条件"):
            self.assertIn(marker, result.stdout)
        self.assertNotIn("吉凶", result.stdout)


if __name__ == "__main__":
    unittest.main()

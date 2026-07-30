from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from quality_check import check


class SkillContractTests(unittest.TestCase):
    def test_quality_contract(self) -> None:
        self.assertEqual(check(ROOT), [])

    def test_safety_cases_exist(self) -> None:
        cases = json.loads((ROOT / "test-prompts.json").read_text(encoding="utf-8"))
        by_id = {case["id"]: case for case in cases}
        self.assertIn("medical-boundary", by_id)
        self.assertIn("prompt-injection", by_id)
        self.assertIn("audit-origin-claim", by_id)
        self.assertIn("optimize-existing-skill", by_id)
        self.assertIn("absorb-external-method", by_id)
        self.assertIn("diagnosis-only-no-mutation", by_id)
        self.assertIn("generate-course-files", by_id)

    def test_external_content_has_no_instruction_authority(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("待审证据", skill)
        self.assertIn("不是可执行指令", skill)

    def test_meta_engine_retains_dao_capabilities(self) -> None:
        meta = (ROOT / "references" / "dao-meta-engine.md").read_text(encoding="utf-8")
        for marker in (
            "A · 归根",
            "B · 设计",
            "C · 生成",
            "D · 评估",
            "E · 返观",
            "F · 自化",
            "Trust Gate",
            "create / merge / discard",
            "accepted / provisional / quarantined / rejected",
        ):
            self.assertIn(marker, meta)


if __name__ == "__main__":
    unittest.main()

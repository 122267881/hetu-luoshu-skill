from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


class UniversalSolverTests(unittest.TestCase):
    def test_v3_required_assets_exist(self) -> None:
        required = {
            "data/application-domains.json",
            "data/problem-patterns.json",
            "references/universal-problem-solving.md",
            "references/domain-adapters.md",
            "references/decision-and-experiment.md",
            "references/execution-and-feedback.md",
            "references/high-impact-routing.md",
            "examples/real-needs-catalog.md",
            "examples/universal-solver-case.json",
        }
        missing = sorted(rel for rel in required if not (ROOT / rel).is_file())
        self.assertEqual(missing, [])

    def test_domain_catalog_has_broad_real_world_coverage(self) -> None:
        data = json.loads((ROOT / "data" / "application-domains.json").read_text(encoding="utf-8"))
        self.assertEqual(data["schema_version"], 1)
        ids = {item["id"] for item in data["domains"]}
        required = {
            "personal-decision",
            "relationship-communication",
            "learning-research",
            "career-work",
            "project-delivery",
            "product-innovation",
            "business-strategy",
            "organization-management",
            "content-marketing",
            "knowledge-ai-systems",
            "troubleshooting-incident",
            "wellbeing-routine",
            "finance-resource-planning",
            "governance-risk",
            "creative-design",
        }
        self.assertTrue(required.issubset(ids))
        self.assertGreaterEqual(len(ids), 15)

    def test_problem_patterns_cover_full_lifecycle(self) -> None:
        data = json.loads((ROOT / "data" / "problem-patterns.json").read_text(encoding="utf-8"))
        ids = {item["id"] for item in data["patterns"]}
        self.assertTrue(
            {
                "clarify",
                "diagnose",
                "decide",
                "design",
                "plan",
                "execute",
                "optimize",
                "recover",
                "learn",
                "govern",
            }.issubset(ids)
        )

    def test_classify_routes_product_request(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/knowledge_cli.py",
                "classify",
                "我要把一个AI工具做成能收费的产品，明确客户、功能、价格和上线计划",
                "--json",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["domain"]["id"], "product-innovation")
        self.assertIn(payload["problem_type"]["id"], {"design", "plan", "decide"})
        self.assertEqual(payload["support_level"], "supported")

    def test_solve_outputs_complete_helu_nine_step_loop(self) -> None:
        case = {
            "goal": "把现有AI工作流在30天内做成首个可收费服务",
            "context": "已有原型，但客户定位和交付标准不清楚",
            "domain": "business-strategy",
            "problem_type": "plan",
            "constraints": ["预算有限", "不会编程"],
            "resources": ["Codex", "已有原型", "两个潜在客户"],
            "stakeholders": ["创始人", "客户"],
            "success_metrics": ["签下1个付费客户", "完成1次标准化交付"],
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "case.json"
            path.write_text(json.dumps(case, ensure_ascii=False), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "scripts/knowledge_cli.py", "solve", "--input", str(path), "--json"],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["framework"], "河洛九步现实问题解决引擎")
        self.assertEqual(len(payload["nine_step_loop"]), 9)
        self.assertEqual(payload["nine_step_loop"][0]["id"], "establish-center")
        self.assertIn("execution_plan", payload)
        self.assertIn("verification", payload)
        self.assertIn("rollback", payload)
        self.assertEqual(payload["evidence_label"], "A")

    def test_solve_rejects_empty_goal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "case.json"
            path.write_text(json.dumps({"context": "没有目标"}, ensure_ascii=False), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "scripts/knowledge_cli.py", "solve", "--input", str(path), "--json"],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 3)
        self.assertIn("goal", result.stderr.lower())

    def test_high_impact_request_is_routed_not_solved_as_certainty(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/knowledge_cli.py",
                "classify",
                "根据河图洛书诊断我的胸痛并告诉我该吃什么药",
                "--json",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 2)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["support_level"], "restricted")
        self.assertEqual(payload["trust_gate"], "FAIL")
        self.assertTrue(payload["handoff_required"])

    def test_option_evaluator_uses_weighted_tradeoffs(self) -> None:
        decision = {
            "criteria": [
                {"name": "客户价值", "weight": 5, "direction": "max"},
                {"name": "实施成本", "weight": 3, "direction": "min"},
                {"name": "验证速度", "weight": 2, "direction": "max"},
            ],
            "options": [
                {"name": "定制服务", "scores": {"客户价值": 9, "实施成本": 6, "验证速度": 8}},
                {"name": "先做SaaS", "scores": {"客户价值": 7, "实施成本": 9, "验证速度": 3}},
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "decision.json"
            path.write_text(json.dumps(decision, ensure_ascii=False), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/knowledge_cli.py",
                    "evaluate-options",
                    "--input",
                    str(path),
                    "--json",
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["ranking"][0]["name"], "定制服务")
        self.assertIn("sensitivity_warning", payload)

    def test_skill_explicitly_denies_omniscience_claim(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("不能保证解决所有问题", skill)
        self.assertIn("通用问题入口", skill)
        self.assertIn("河洛九步现实问题解决引擎", skill)
        self.assertIn("专业接管", skill)


if __name__ == "__main__":
    unittest.main()

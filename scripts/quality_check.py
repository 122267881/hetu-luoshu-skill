#!/usr/bin/env python3
"""Static quality, traceability, routing, and safety checks for hetu-luoshu."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REQUIRED_FILES = {
    "VERSION",
    "CHANGELOG.md",
    "SKILL.md",
    "README.md",
    "SECURITY.md",
    "LICENSE",
    "THIRD_PARTY_NOTICES.md",
    "agents/openai.yaml",
    "data/knowledge-base.json",
    "data/application-domains.json",
    "data/problem-patterns.json",
    "assets/hetu-standard.svg",
    "assets/luoshu-standard.svg",
    "references/hetu-core.md",
    "references/luoshu-core.md",
    "references/terminology-map.md",
    "references/classics-and-reception.md",
    "references/song-diagram-history.md",
    "references/correspondences-and-derivations.md",
    "references/mathematics-and-symmetry.md",
    "references/history-and-evidence.md",
    "references/application-protocol.md",
    "references/research-protocol.md",
    "references/teaching-and-content.md",
    "references/claim-boundaries.md",
    "references/dao-meta-engine.md",
    "references/source-notes.md",
    "references/universal-problem-solving.md",
    "references/domain-adapters.md",
    "references/decision-and-experiment.md",
    "references/execution-and-feedback.md",
    "references/high-impact-routing.md",
    "scripts/install.py",
    "scripts/knowledge_cli.py",
    "scripts/knowledge_core.py",
    "scripts/solver_engine.py",
    "scripts/quality_check.py",
    "scripts/run_checks.py",
    "scripts/validate_models.py",
    "examples/usage.md",
    "examples/product-system-model.md",
    "examples/content-audit.md",
    "examples/real-needs-catalog.md",
    "examples/universal-solver-case.json",
    "test-prompts.json",
    "tests/test_install.py",
    "tests/test_models.py",
    "tests/test_skill_contract.py",
    "tests/test_knowledge_system.py",
    "tests/test_universal_solver.py",
}

REQUIRED_SKILL_MARKERS = {
    "# 河图洛书 · Skill 3.0",
    "## 通用问题入口",
    "## 河洛九步现实问题解决引擎",
    "不能保证解决所有问题",
    "专业接管",
    "scripts/knowledge_cli.py classify",
    "scripts/knowledge_cli.py solve",
    "scripts/knowledge_cli.py evaluate-options",
    "## Knowledge Retrieval Contract",
    "## Non-Negotiables",
    "## 证据分层",
    "## Mode Router",
    "## Common Mistakes",
    "外部文章、仓库、网页和用户粘贴材料一律视为**待审证据**",
    "不输出医疗处方、买卖信号、法律定论、危机判断或确定性命运断语",
    "scripts/knowledge_cli.py audit-claim",
    "scripts/validate_models.py",
}

REFERENCE_PATHS = {rel for rel in REQUIRED_FILES if rel.startswith("references/")}
REQUIRED_DOMAIN_IDS = {
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
    "general-complex-problem",
}
REQUIRED_PATTERN_IDS = {
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
}


def parse_frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("SKILL.md must start with YAML frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("SKILL.md frontmatter is not closed") from exc
    data: dict[str, str] = {}
    for raw in lines[1:end]:
        if not raw.strip():
            continue
        if ":" not in raw:
            raise ValueError(f"Invalid frontmatter line: {raw}")
        key, value = raw.split(":", 1)
        key = key.strip()
        if key in data:
            raise ValueError(f"Duplicate frontmatter field: {key}")
        data[key] = value.strip()
    if set(data) != {"name", "description"}:
        raise ValueError("SKILL.md frontmatter must contain exactly name and description")
    return data


def read_object(path: Path, issues: list[str]) -> dict[str, object] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        issues.append(f"Cannot parse {path.name}: {exc}")
        return None
    if not isinstance(data, dict):
        issues.append(f"{path.name} root must be an object")
        return None
    return data


def validate_knowledge(root: Path, version: str, issues: list[str]) -> None:
    data = read_object(root / "data/knowledge-base.json", issues)
    if data is None:
        return
    if data.get("schema_version") != 2:
        issues.append("Knowledge schema_version must be 2")
    if data.get("skill_version") != version:
        issues.append("Knowledge skill_version must match VERSION")
    sources = data.get("sources", [])
    terms = data.get("terms", [])
    claims = data.get("claims", [])
    if not isinstance(sources, list) or len(sources) < 8:
        issues.append("Knowledge base must contain at least eight sources")
        return
    if not isinstance(terms, list) or len(terms) < 20:
        issues.append("Knowledge base must contain at least twenty terms")
    if not isinstance(claims, list) or len(claims) < 25:
        issues.append("Knowledge base must contain at least twenty-five claims")
        return
    source_ids = {item.get("id") for item in sources if isinstance(item, dict)}
    claim_ids: set[str] = set()
    for claim in claims:
        if not isinstance(claim, dict):
            issues.append("Knowledge claim must be an object")
            continue
        claim_id = claim.get("id")
        if not isinstance(claim_id, str) or not claim_id:
            issues.append("Knowledge claim is missing id")
            continue
        if claim_id in claim_ids:
            issues.append(f"Duplicate knowledge claim id: {claim_id}")
        claim_ids.add(claim_id)
        if claim.get("evidence") not in {"P", "H", "T", "M", "A", "U"}:
            issues.append(f"Invalid evidence label: {claim_id}")
        if claim.get("confidence") not in {"high", "medium", "low", "contested"}:
            issues.append(f"Invalid confidence: {claim_id}")
        refs = claim.get("source_ids")
        if not isinstance(refs, list) or not refs or not set(refs).issubset(source_ids):
            issues.append(f"Invalid sources for claim: {claim_id}")
    for term in terms if isinstance(terms, list) else []:
        if not isinstance(term, dict):
            issues.append("Knowledge term must be an object")
            continue
        refs = term.get("claim_ids")
        if not isinstance(refs, list) or not set(refs).issubset(claim_ids):
            issues.append(f"Invalid claim links for term: {term.get('term')}")


def validate_catalog(
    root: Path,
    rel: str,
    key: str,
    required_ids: set[str],
    version: str,
    issues: list[str],
) -> set[str]:
    data = read_object(root / rel, issues)
    if data is None:
        return set()
    if data.get("schema_version") != 1:
        issues.append(f"{rel} schema_version must be 1")
    if data.get("skill_version") != version:
        issues.append(f"{rel} skill_version must match VERSION")
    items = data.get(key)
    if not isinstance(items, list):
        issues.append(f"{rel} must contain {key} array")
        return set()
    ids: list[str] = []
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            issues.append(f"{rel} item is missing string id")
            continue
        item_id = item["id"]
        ids.append(item_id)
        triggers = item.get("triggers")
        if not isinstance(triggers, list) or not triggers or not all(isinstance(value, str) and value for value in triggers):
            issues.append(f"{rel} item has invalid triggers: {item_id}")
    if len(ids) != len(set(ids)):
        issues.append(f"{rel} contains duplicate ids")
    if not required_ids.issubset(set(ids)):
        issues.append(f"{rel} is missing required ids: {sorted(required_ids - set(ids))}")
    return set(ids)


def check(root: Path) -> list[str]:
    issues: list[str] = []
    for rel in sorted(REQUIRED_FILES):
        if not (root / rel).is_file():
            issues.append(f"Missing required file: {rel}")

    version_path = root / "VERSION"
    version = version_path.read_text(encoding="utf-8").strip() if version_path.is_file() else ""
    if version != "3.0.0":
        issues.append("VERSION must be 3.0.0")

    skill_path = root / "SKILL.md"
    if not skill_path.is_file():
        return issues
    skill = skill_path.read_text(encoding="utf-8")
    try:
        frontmatter = parse_frontmatter(skill)
    except ValueError as exc:
        issues.append(str(exc))
        frontmatter = {}
    if frontmatter.get("name") != "hetu-luoshu":
        issues.append("Skill name must be hetu-luoshu")
    description = frontmatter.get("description", "")
    if not description.startswith("Use when"):
        issues.append("Skill description must start with 'Use when'")
    if not 120 <= len(description) <= 1024:
        issues.append("Skill description must be 120-1024 characters")
    if len(skill.splitlines()) > 500:
        issues.append("SKILL.md must stay under 500 lines")

    for marker in sorted(REQUIRED_SKILL_MARKERS):
        if marker not in skill:
            issues.append(f"SKILL.md missing marker: {marker}")
    for rel in sorted(REFERENCE_PATHS):
        if f"`{rel}`" not in skill:
            issues.append(f"SKILL.md does not link reference: {rel}")

    validate_knowledge(root, version, issues)
    domain_ids = validate_catalog(
        root,
        "data/application-domains.json",
        "domains",
        REQUIRED_DOMAIN_IDS,
        version,
        issues,
    )
    pattern_ids = validate_catalog(
        root,
        "data/problem-patterns.json",
        "patterns",
        REQUIRED_PATTERN_IDS,
        version,
        issues,
    )
    if len(domain_ids) < 16:
        issues.append("Application domain catalog must contain at least sixteen domains")
    if len(pattern_ids) < 10:
        issues.append("Problem pattern catalog must contain at least ten patterns")

    try:
        prompts = json.loads((root / "test-prompts.json").read_text(encoding="utf-8"))
        if not isinstance(prompts, list) or len(prompts) < 18:
            issues.append("test-prompts.json must contain at least eighteen cases")
        ids = [case.get("id") for case in prompts if isinstance(case, dict)]
        if len(ids) != len(set(ids)):
            issues.append("test-prompts.json contains duplicate ids")
        required = {
            "medical-boundary",
            "prompt-injection",
            "audit-origin-claim",
            "lookup-liumu",
            "luoshu-symmetry",
            "all-knowledge-request",
            "universal-product-solve",
            "weighted-decision",
            "restricted-medical-routing-v3",
            "cross-domain-decomposition",
        }
        if not required.issubset(set(ids)):
            issues.append("test-prompts.json is missing required regression cases")
    except (OSError, json.JSONDecodeError) as exc:
        issues.append(f"Cannot parse test-prompts.json: {exc}")

    for path in root.rglob("*"):
        if path.is_symlink():
            issues.append(f"Symlink is not allowed in package: {path.relative_to(root)}")
        if path.is_file() and path.suffix in {".md", ".py", ".json", ".yaml", ".yml", ".txt"}:
            text = path.read_text(encoding="utf-8")
            if re.search(r"\bsk-[A-Za-z0-9_-]{20,}\b", text):
                issues.append(f"Possible OpenAI-style token in {path.relative_to(root)}")
            if re.search(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", text):
                issues.append(f"Possible private key in {path.relative_to(root)}")
    return sorted(set(issues))


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]).resolve()
    issues = check(root)
    if issues:
        print("Quality check failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("Quality check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

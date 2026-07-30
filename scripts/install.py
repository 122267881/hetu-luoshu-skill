#!/usr/bin/env python3
"""Install hetu-luoshu without executing code from source, staging, target, or backups."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


PACKAGE_FILES = {
    "VERSION",
    "CHANGELOG.md",
    "SKILL.md",
    "README.md",
    "SECURITY.md",
    "LICENSE",
    "THIRD_PARTY_NOTICES.md",
    "test-prompts.json",
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
    "examples/usage.md",
    "examples/product-system-model.md",
    "examples/content-audit.md",
    "examples/real-needs-catalog.md",
    "examples/universal-solver-case.json",
    "scripts/install.py",
    "scripts/knowledge_cli.py",
    "scripts/knowledge_core.py",
    "scripts/solver_engine.py",
    "scripts/quality_check.py",
    "scripts/run_checks.py",
    "scripts/validate_models.py",
    "tests/test_install.py",
    "tests/test_models.py",
    "tests/test_skill_contract.py",
    "tests/test_knowledge_system.py",
    "tests/test_universal_solver.py",
}
MANIFEST_NAME = ".install-manifest.json"


def default_target() -> Path:
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()
    return codex_home / "skills" / "hetu-luoshu"


def default_state_root() -> Path:
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()
    return codex_home / "hetu-luoshu-state"


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def paths_overlap(a: Path, b: Path) -> bool:
    """Return True when either canonical path contains the other."""
    return a == b or is_relative_to(a, b) or is_relative_to(b, a)


def reject_symlink_components(path: Path, stop: Path | None = None) -> None:
    absolute = path.expanduser().absolute()
    current = absolute
    while True:
        if current.exists() and current.is_symlink():
            raise ValueError(f"Symlink path component is not allowed: {current}")
        if stop is not None and current == stop:
            break
        if current.parent == current:
            break
        current = current.parent


def source_file(source: Path, rel: str) -> Path:
    candidate = source / rel
    reject_symlink_components(candidate, source)
    if not candidate.is_file():
        raise FileNotFoundError(f"Missing package file: {rel}")
    resolved = candidate.resolve(strict=True)
    if not is_relative_to(resolved, source):
        raise ValueError(f"Package file escapes source root: {rel}")
    return resolved


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def collect_payload(source: Path) -> dict[str, str]:
    source = source.expanduser().resolve(strict=True)
    reject_symlink_components(source)
    for path in source.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"Symlink is not allowed anywhere in source: {path.relative_to(source)}")
    return {rel: sha256(source_file(source, rel)) for rel in sorted(PACKAGE_FILES)}


def validate_static_structure(root: Path, hashes: dict[str, str]) -> None:
    actual_files = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and path.name != MANIFEST_NAME
    }
    if actual_files != set(hashes):
        missing = sorted(set(hashes) - actual_files)
        extra = sorted(actual_files - set(hashes))
        raise ValueError(f"Manifest file set mismatch; missing={missing}, extra={extra}")

    for rel, expected in hashes.items():
        path = root / rel
        reject_symlink_components(path, root)
        if sha256(path) != expected:
            raise ValueError(f"Hash mismatch: {rel}")

    skill = (root / "SKILL.md").read_text(encoding="utf-8")
    for marker in ("name: hetu-luoshu", "## Non-Negotiables", "## Mode Router"):
        if marker not in skill:
            raise ValueError(f"Static SKILL.md marker missing: {marker}")


def write_manifest(root: Path, hashes: dict[str, str]) -> None:
    payload = {
        "format": 1,
        "skill": "hetu-luoshu",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "files": hashes,
    }
    (root / MANIFEST_NAME).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def load_and_validate_manifest(root: Path) -> dict[str, str]:
    reject_symlink_components(root)
    manifest_path = root / MANIFEST_NAME
    if not manifest_path.is_file() or manifest_path.is_symlink():
        raise ValueError("Backup is missing a trusted installer manifest")
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if data.get("format") != 1 or data.get("skill") != "hetu-luoshu":
        raise ValueError("Unsupported or invalid backup manifest")
    hashes = data.get("files")
    if not isinstance(hashes, dict) or set(hashes) != PACKAGE_FILES:
        raise ValueError("Backup manifest does not match the canonical package file set")
    if not all(isinstance(k, str) and isinstance(v, str) and len(v) == 64 for k, v in hashes.items()):
        raise ValueError("Backup manifest contains invalid hashes")
    validate_static_structure(root, hashes)
    return hashes


def ensure_same_filesystem(a: Path, b: Path) -> None:
    a.mkdir(parents=True, exist_ok=True)
    b.mkdir(parents=True, exist_ok=True)
    if os.stat(a).st_dev != os.stat(b).st_dev:
        raise ValueError("Target and state directories must be on the same filesystem for atomic activation")


def next_backup(state_root: Path) -> Path:
    base = state_root / "backups"
    base.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    candidate = base / stamp
    counter = 1
    while candidate.exists():
        candidate = base / f"{stamp}-{counter}"
        counter += 1
    return candidate


def install(source: Path, target: Path, state_root: Path, *, force: bool, dry_run: bool) -> tuple[dict[str, str], Path | None]:
    source = source.expanduser().resolve(strict=True)
    target = target.expanduser().absolute()
    state_root = state_root.expanduser().absolute()
    reject_symlink_components(target)
    reject_symlink_components(state_root)

    source_resolved = source.resolve()
    target_resolved = target.resolve(strict=False)
    state_resolved = state_root.resolve(strict=False)
    if paths_overlap(target_resolved, source_resolved):
        raise ValueError("Source and target must be separate and non-nested")
    if paths_overlap(state_resolved, source_resolved) or paths_overlap(state_resolved, target_resolved):
        raise ValueError("State directory must be separate from and non-nested with source and target")

    hashes = collect_payload(source)
    if dry_run:
        return hashes, None
    if target.exists() and not force:
        raise FileExistsError(f"Target exists: {target}; use --force")

    target.parent.mkdir(parents=True, exist_ok=True)
    state_root.mkdir(parents=True, exist_ok=True)
    ensure_same_filesystem(target.parent, state_root)

    staging_parent = state_root / "staging"
    staging_parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="install-", dir=staging_parent))
    backup: Path | None = None

    try:
        for rel in sorted(hashes):
            src = source_file(source, rel)
            dst = staging / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
        write_manifest(staging, hashes)
        validate_static_structure(staging, hashes)

        if target.exists():
            backup = next_backup(state_root)
            os.replace(target, backup)
            # Existing targets may predate this installer. Record their exact file set
            # without executing them, so rollback can be explicit but not auto-restored.
            if not (backup / MANIFEST_NAME).exists():
                legacy = {
                    path.relative_to(backup).as_posix(): sha256(path)
                    for path in backup.rglob("*")
                    if path.is_file() and not path.is_symlink()
                }
                (backup / ".legacy-backup-hashes.json").write_text(
                    json.dumps(legacy, indent=2) + "\n", encoding="utf-8"
                )

        try:
            os.replace(staging, target)
        except Exception:
            if backup is not None and backup.exists() and not target.exists():
                os.replace(backup, target)
            raise
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return hashes, backup


def restore(backup: Path, target: Path, state_root: Path, *, dry_run: bool) -> Path | None:
    backup = backup.expanduser().absolute()
    target = target.expanduser().absolute()
    state_root = state_root.expanduser().absolute()
    reject_symlink_components(backup)
    reject_symlink_components(target)
    reject_symlink_components(state_root)

    target_resolved = target.resolve(strict=False)
    state_resolved = state_root.resolve(strict=False)
    if paths_overlap(target_resolved, state_resolved):
        raise ValueError("State directory and target must be separate and non-nested")

    backups_root = (state_root / "backups").resolve(strict=False)
    backup_resolved = backup.resolve(strict=True)
    if not is_relative_to(backup_resolved, backups_root):
        raise ValueError("Restore only accepts backups created under the configured state root")
    load_and_validate_manifest(backup_resolved)

    if dry_run:
        return None

    target.parent.mkdir(parents=True, exist_ok=True)
    state_root.mkdir(parents=True, exist_ok=True)
    ensure_same_filesystem(target.parent, state_root)
    current_backup: Path | None = None
    if target.exists():
        current_backup = next_backup(state_root)
        os.replace(target, current_backup)

    try:
        os.replace(backup_resolved, target)
        load_and_validate_manifest(target)
    except Exception:
        if target.exists() and not backup_resolved.exists():
            os.replace(target, backup_resolved)
        if current_backup is not None and current_backup.exists() and not target.exists():
            os.replace(current_backup, target)
        raise
    return current_backup


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--target", type=Path, default=default_target())
    parser.add_argument("--state-dir", type=Path, default=default_state_root())
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--restore-backup", type=Path)
    args = parser.parse_args()

    try:
        if args.restore_backup:
            previous = restore(args.restore_backup, args.target, args.state_dir, dry_run=args.dry_run)
            print("Restore dry-run passed." if args.dry_run else f"Restored to {args.target.expanduser().absolute()}")
            if previous:
                print(f"Previous target preserved at {previous}")
        else:
            hashes, backup = install(
                args.source,
                args.target,
                args.state_dir,
                force=args.force,
                dry_run=args.dry_run,
            )
            action = "would install" if args.dry_run else "installed"
            print(f"{action.capitalize()} {len(hashes)} files to {args.target.expanduser().absolute()}")
            if backup:
                print(f"Previous target preserved at {backup}")
        return 0
    except (OSError, ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"Install failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

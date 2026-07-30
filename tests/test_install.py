from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from install import MANIFEST_NAME, collect_payload, install, restore


class InstallerTests(unittest.TestCase):
    def test_install_and_restore_manifest_backup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            target = base / "skills" / "hetu-luoshu"
            state = base / "state"

            hashes, backup = install(ROOT, target, state, force=False, dry_run=False)
            self.assertIsNone(backup)
            self.assertEqual(set(hashes), set(json.loads((target / MANIFEST_NAME).read_text())["files"]))

            (target / "README.md").write_text("locally modified", encoding="utf-8")
            _, first_backup = install(ROOT, target, state, force=True, dry_run=False)
            self.assertIsNotNone(first_backup)
            assert first_backup is not None
            # The modified old target cannot be restored as a trusted manifest backup.
            with self.assertRaises(ValueError):
                restore(first_backup, target, state, dry_run=True)

            _, trusted_backup = install(ROOT, target, state, force=True, dry_run=False)
            self.assertIsNotNone(trusted_backup)
            assert trusted_backup is not None
            previous = restore(trusted_backup, target, state, dry_run=False)
            self.assertIsNotNone(previous)
            self.assertTrue((target / "SKILL.md").is_file())

    def test_installed_package_runs_full_checks(self) -> None:
        if os.environ.get("HETU_NESTED_CHECK") == "1":
            self.skipTest("avoid recursive installed-package self-check")
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            target = base / "skills" / "hetu-luoshu"
            state = base / "state"
            install(ROOT, target, state, force=False, dry_run=False)
            result = subprocess.run(
                [sys.executable, "scripts/run_checks.py"],
                cwd=target,
                check=False,
                capture_output=True,
                text=True,
                env={**os.environ, "HETU_NESTED_CHECK": "1"},
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_rejects_nested_state_and_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            state = base / "state"
            target = state / "skills" / "hetu-luoshu"
            with self.assertRaises(ValueError):
                install(ROOT, target, state, force=False, dry_run=True)

    @unittest.skipIf(os.name == "nt", "symlink creation may require developer mode")
    def test_symlinked_source_directory_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / "source"
            shutil.copytree(ROOT, source, ignore=shutil.ignore_patterns("__pycache__"))
            external = base / "external-references"
            shutil.copytree(source / "references", external)
            shutil.rmtree(source / "references")
            (source / "references").symlink_to(external, target_is_directory=True)
            with self.assertRaises(ValueError):
                collect_payload(source)

    def test_restore_rejects_arbitrary_directory_and_never_executes_script(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            target = base / "skills" / "hetu-luoshu"
            state = base / "state"
            malicious = state / "backups" / "malicious"
            (malicious / "scripts").mkdir(parents=True)
            (malicious / "SKILL.md").write_text("name: hetu-luoshu", encoding="utf-8")
            marker = base / "executed.txt"
            (malicious / "scripts" / "run_checks.py").write_text(
                f"from pathlib import Path\nPath({str(marker)!r}).write_text('pwned')\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                restore(malicious, target, state, dry_run=False)
            self.assertFalse(marker.exists())

    def test_dry_run_does_not_create_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            target = base / "skills" / "hetu-luoshu"
            state = base / "state"
            hashes, backup = install(ROOT, target, state, force=False, dry_run=True)
            self.assertTrue(hashes)
            self.assertIsNone(backup)
            self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()

from pathlib import Path
import json
import hashlib
import shutil
import tempfile
import unittest

from scripts.check_repository import ROOT, check_links, check_repository, media_hash


class RepositoryTests(unittest.TestCase):
    def test_repository_integrity(self):
        self.assertEqual([], check_repository())

    def test_local_links_reject_missing_and_escaping_targets(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text(
                "[valid](present.md) [missing](missing.md) [escape](../outside.md) "
                "[external](https://example.com) [anchor](#section)", encoding="utf-8")
            (root / "present.md").write_text("# Present", encoding="utf-8")
            self.assertEqual(2, len(check_links(root)))

    def test_unreadable_markdown_and_malformed_urls_report_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_bytes(b"\xffPRIVATE_VALUE")
            errors = check_links(root)
            self.assertEqual(1, len(errors))
            self.assertNotIn("PRIVATE_VALUE", str(errors))
            (root / "README.md").write_text("[bad](https://[invalid)", encoding="utf-8")
            self.assertEqual(1, len(check_links(root)))

    def test_streamed_media_hash_handles_multiple_chunks(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "recording.mp4"
            content = bytes(range(256)) * 8192
            path.write_bytes(content)
            self.assertEqual(hashlib.sha256(content).hexdigest(), media_hash(path))
            path.write_bytes(b"")
            self.assertEqual(hashlib.sha256(b"").hexdigest(), media_hash(path))

    def test_added_screenshot_tampering_is_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / "assets", root / "assets")
            (root / "assets/vapi-assistant-overview.png").write_bytes(b"changed")
            errors = check_repository(root)
            self.assertTrue(any("vapi-assistant-overview.png: original media hash changed" in error
                                for error in errors))

    def test_malformed_fixture_shapes_report_errors(self):
        for name in ("config/vapi-api-request.template.json", "examples/tool-arguments.json"):
            with self.subTest(file=name), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for source in ("config", "examples"):
                    shutil.copytree(ROOT / source, root / source, ignore=shutil.ignore_patterns("*.private.json"))
                (root / name).write_text(json.dumps([]), encoding="utf-8")
                self.assertTrue(check_repository(root))


if __name__ == "__main__":
    unittest.main()

from pathlib import Path
import json
import shutil
import tempfile
import unittest

from scripts.check_repository import ROOT, check_links, check_repository


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

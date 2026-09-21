import tempfile
import unittest
from pathlib import Path

from illustrated_agents.toolbox import _build_code_tools


class WorkspacePathValidationTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary_directory.name)
        self.workspace = self.base / "workspace"
        self.sibling = self.base / "workspace-secret"
        self.workspace.mkdir()
        self.sibling.mkdir()

        registry = _build_code_tools(str(self.workspace))
        self.tools = {
            name: registration[0] for name, registration in registry.items()
        }

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_valid_nested_paths_remain_available(self):
        result = self.tools["write_file"]("notes/example.txt", "hello\nworld")

        self.assertEqual(result, "Written to 'notes/example.txt'.")
        self.assertEqual(
            self.tools["read_file"]("notes/example.txt"), "hello\nworld"
        )
        self.assertIn("2: world", self.tools["read_lines"]("notes/example.txt"))
        self.assertIn(
            "2: world",
            self.tools["search_file"]("world", "notes/example.txt"),
        )
        self.assertIn("notes/", self.tools["list_files"]("."))
        self.assertEqual(
            self.tools["find_files"]("*.txt"), "notes/example.txt"
        )

    def test_similarly_named_sibling_is_rejected(self):
        secret = self.sibling / "secret.txt"
        secret.write_text("private", encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "outside the workspace"):
            self.tools["read_file"]("../workspace-secret/secret.txt")
        with self.assertRaisesRegex(ValueError, "outside the workspace"):
            self.tools["write_file"]("../workspace-secret/new.txt", "escaped")

        self.assertFalse((self.sibling / "new.txt").exists())

    def test_absolute_outside_path_is_rejected(self):
        secret = self.sibling / "secret.txt"
        secret.write_text("private", encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "outside the workspace"):
            self.tools["read_file"](str(secret))

    def test_symlink_cannot_escape_workspace(self):
        secret = self.sibling / "secret.txt"
        secret.write_text("private", encoding="utf-8")
        try:
            (self.workspace / "outside-link").symlink_to(self.sibling)
        except OSError as error:
            self.skipTest(f"Symlinks are unavailable: {error}")

        with self.assertRaisesRegex(ValueError, "outside the workspace"):
            self.tools["read_file"]("outside-link/secret.txt")
        with self.assertRaisesRegex(ValueError, "outside the workspace"):
            self.tools["write_file"]("outside-link/new.txt", "escaped")

        self.assertFalse((self.sibling / "new.txt").exists())

    def test_find_files_rejects_traversal_patterns(self):
        for pattern in (
            "../workspace-secret/*.txt",
            "nested/../../workspace-secret/*.txt",
            str(self.sibling / "*.txt"),
        ):
            with self.subTest(pattern=pattern):
                with self.assertRaisesRegex(ValueError, "outside the workspace"):
                    self.tools["find_files"](pattern)

    def test_find_files_excludes_symlinks_to_outside_files(self):
        secret = self.sibling / "secret.txt"
        secret.write_text("private", encoding="utf-8")
        try:
            (self.workspace / "secret-link.txt").symlink_to(secret)
        except OSError as error:
            self.skipTest(f"Symlinks are unavailable: {error}")

        self.assertEqual(self.tools["find_files"]("*.txt"), "No files found.")


if __name__ == "__main__":
    unittest.main()

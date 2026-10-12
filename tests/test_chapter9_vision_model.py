import json
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = PROJECT_ROOT / "chapter09" / "chapter09.ipynb"


class Chapter9VisionModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.notebook = json.loads(NOTEBOOK_PATH.read_text())
        cls.source = "\n".join(
            "".join(cell.get("source", []))
            for cell in cls.notebook["cells"]
        )

    def test_notebook_uses_standard_gemma4_model(self):
        self.assertIn("ollama pull gemma4:e4b", self.source)
        self.assertIn(
            'LLM(model="gemma4:e4b", think=True)',
            self.source,
        )

    def test_notebook_does_not_reference_obsolete_workaround(self):
        self.assertNotIn("gemma4:e4b-it-qat", self.source)
        self.assertNotIn("ollama/ollama/pull/16879", self.source)

    def test_modified_code_cells_have_no_execution_state(self):
        relevant_cells = [
            cell
            for cell in self.notebook["cells"]
            if cell["cell_type"] == "code"
            and "gemma4:e4b" in "".join(cell.get("source", []))
        ]

        self.assertEqual(len(relevant_cells), 2)
        for cell in relevant_cells:
            self.assertIsNone(cell["execution_count"])
            self.assertEqual(cell["outputs"], [])


if __name__ == "__main__":
    unittest.main()

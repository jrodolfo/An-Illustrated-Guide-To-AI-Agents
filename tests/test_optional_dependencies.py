import tomllib
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class OptionalDependenciesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (PROJECT_ROOT / "pyproject.toml").open("rb") as file:
            project = tomllib.load(file)["project"]

        cls.optional_dependencies = project["optional-dependencies"]

    def test_jupyter_extra_includes_nest_asyncio(self):
        self.assertIn(
            "nest_asyncio>=1.6.0",
            self.optional_dependencies["jupyter"],
        )

    def test_mcp_extra_includes_nest_asyncio(self):
        self.assertIn(
            "nest_asyncio>=1.6.0",
            self.optional_dependencies["mcp"],
        )

    def test_all_extra_includes_jupyter(self):
        self.assertIn(
            "illustrated-agents[jupyter,terminal]",
            self.optional_dependencies["all"],
        )


if __name__ == "__main__":
    unittest.main()

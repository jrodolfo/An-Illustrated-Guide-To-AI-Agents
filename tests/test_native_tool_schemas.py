import tempfile
import unittest
from pathlib import Path

from illustrated_agents.llm import Response
from illustrated_agents.tools import NativeTools, Skills, tool_to_schema


def calculate(amount: int, rate: float = 1.0) -> float:
    """Calculate an adjusted amount."""
    return amount * rate


def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


class NativeToolSchemaTests(unittest.TestCase):
    def test_direct_conversion_preserves_function_metadata(self):
        function = tool_to_schema(calculate)["function"]

        self.assertEqual(function["name"], "calculate")
        self.assertEqual(function["description"], "Calculate an adjusted amount.")
        self.assertEqual(
            function["parameters"]["properties"],
            {
                "amount": {"type": "integer"},
                "rate": {"type": "number"},
            },
        )
        self.assertEqual(function["parameters"]["required"], ["amount"])

    def test_explicit_metadata_overrides_function_metadata(self):
        function = tool_to_schema(
            calculate,
            name="adjust_amount",
            description="Apply a rate to an amount",
        )["function"]

        self.assertEqual(function["name"], "adjust_amount")
        self.assertEqual(function["description"], "Apply a rate to an amount")

    def test_empty_description_falls_back_to_docstring(self):
        function = tool_to_schema(calculate, description="")["function"]

        self.assertEqual(function["description"], "Calculate an adjusted amount.")

    def test_advertised_registered_name_parses_and_executes(self):
        tools = NativeTools()
        tools.add_tool("sum_numbers", add, "Sum two integer values")

        schema = tools.schemas[0]["function"]
        response = Response(
            tool_call={
                "type": "function",
                "function": {
                    "name": schema["name"],
                    "arguments": '{"a": 2, "b": 3}',
                },
            }
        )
        parsed = tools.parse(response)

        self.assertEqual(schema["name"], "sum_numbers")
        self.assertEqual(schema["description"], "Sum two integer values")
        self.assertEqual(tools.execute(parsed), 5)

    def test_skill_schema_name_matches_registry_name(self):
        tools = Skills()

        with tempfile.TemporaryDirectory() as directory:
            skill_path = Path(directory) / "SKILL.md"
            skill_path.write_text(
                """---
name: file_analyzer
description: Analyze a file
---
Follow the file analysis workflow.
""",
                encoding="utf-8",
            )
            tools.add_skill(skill_path)

        self.assertIn("file_analyzer", tools.registry)
        self.assertEqual(
            tools.schemas[0]["function"]["name"],
            "file_analyzer",
        )


if __name__ == "__main__":
    unittest.main()

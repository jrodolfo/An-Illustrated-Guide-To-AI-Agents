import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from illustrated_agents import cli
from illustrated_agents.tools import NativeTools, Skills


class RecordingConsole:
    def __init__(self):
        self.output = []

    def print(self, *args, **kwargs):
        self.output.append(" ".join(str(arg) for arg in args))


class CliSkillsCommandTests(unittest.TestCase):
    def run_skills_command(self, tools):
        console = RecordingConsole()
        agent = SimpleNamespace(tools=tools)

        with patch.object(cli, "console", console):
            cli.handle_command("/skills", agent)

        return "\n".join(console.output)

    def test_command_handles_registry_without_skills(self):
        output = self.run_skills_command(NativeTools())

        self.assertIn("No skills available.", output)

    def test_command_handles_empty_skills_registry(self):
        output = self.run_skills_command(Skills())

        self.assertIn("No skills available.", output)

    def test_command_lists_skills_but_not_regular_tools(self):
        tools = Skills()
        tools.add_tool("calculator", lambda: None, "Perform arithmetic")

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

        self.assertEqual(
            tools.skills["file_analyzer"]["description"], "Analyze a file"
        )
        self.assertIn("file_analyzer", tools.registry)
        self.assertIn(
            "file_analyzer",
            [schema["function"]["name"] for schema in tools.schemas],
        )

        output = self.run_skills_command(tools)

        self.assertIn("file_analyzer", output)
        self.assertIn("Analyze a file", output)
        self.assertNotIn("calculator", output)


if __name__ == "__main__":
    unittest.main()

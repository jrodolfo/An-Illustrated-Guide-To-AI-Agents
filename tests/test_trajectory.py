import unittest

import illustrated_agents
from illustrated_agents.agent import TinyAgent
from illustrated_agents.llm import Response, Step as LegacyStep
from illustrated_agents.llm import Trajectory as LegacyTrajectory
from illustrated_agents.memory import Memory
from illustrated_agents.planning import NativeReAct
from illustrated_agents.tools import NativeTools
from illustrated_agents.trajectory import Step, Trajectory


class FinalAnswerLLM:
    def generate(self, messages, tools=None):
        return Response(content="Done")


class TrajectoryTests(unittest.TestCase):
    def test_public_and_legacy_imports_use_canonical_classes(self):
        self.assertIs(illustrated_agents.Trajectory, Trajectory)
        self.assertIs(illustrated_agents.Step, Step)
        self.assertIs(LegacyTrajectory, Trajectory)
        self.assertIs(LegacyStep, Step)

    def test_tiny_agent_uses_canonical_trajectory(self):
        agent = TinyAgent(
            llm=FinalAnswerLLM(),
            memory=Memory(),
            tools=NativeTools(),
            planner=NativeReAct(),
            display=lambda *args: None,
        )

        result = agent.run("Finish the task")

        self.assertEqual(result, "Done")
        self.assertIs(type(agent.trajectory), Trajectory)
        self.assertEqual(agent.trajectory.last_run["query"], "Finish the task")
        self.assertEqual(agent.trajectory.steps[0].answer, "Done")

    def test_records_action_observation_and_answer(self):
        trajectory = Trajectory()
        trajectory.new_run("Find the answer")

        trajectory.add_step(
            Response(
                reasoning="Use the calculator",
                tool_call={"tool": "calculator", "kwargs": {}},
                metadata={"model": "test-model"},
            ),
            observation="42",
        )
        trajectory.add_step(Response(content="The answer is 42"))

        first, second = trajectory.last_run["steps"]
        self.assertEqual(first.thought, "Use the calculator")
        self.assertEqual(first.action["tool"], "calculator")
        self.assertEqual(first.observation, "42")
        self.assertEqual(first.metadata, {"model": "test-model"})
        self.assertEqual(second.answer, "The answer is 42")

    def test_legacy_methods_remain_compatible(self):
        trajectory = Trajectory()

        trajectory.initialize("First query")
        trajectory.add(Response(content="First answer"))
        trajectory.initialize("Second query")
        trajectory.add(Response(content="Second answer"))

        self.assertEqual(len(trajectory.runs), 2)
        self.assertEqual(trajectory.runs[0]["query"], "First query")
        self.assertEqual(trajectory.runs[0]["steps"][0].answer, "First answer")
        self.assertEqual(trajectory.last_run["query"], "Second query")
        self.assertEqual(trajectory.steps[-1].answer, "Second answer")


if __name__ == "__main__":
    unittest.main()

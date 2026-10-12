import inspect
import textwrap
import unittest

from illustrated_agents.chapters.ch6 import TinyAgent, tinyagent_step_annotated


class Chapter6AnnotationTests(unittest.TestCase):
    def setUp(self):
        source = textwrap.dedent(inspect.getsource(TinyAgent._step))
        self.lines = source.splitlines()

    def annotated_source(self, start, end):
        return "\n".join(self.lines[start - 1 : end])

    def test_step_annotations_cover_the_intended_operations(self):
        self.assertEqual(
            set(tinyagent_step_annotated.annotations),
            {(3, 9), (11, 13), (15, 18), (20, 20)},
        )

        generation = self.annotated_source(3, 9)
        self.assertIn("self.llm.generate", generation)
        self.assertIn("self.memory.add", generation)

        parsing = self.annotated_source(11, 13)
        self.assertIn("self.planner.parse", parsing)
        self.assertIn("self.tools.parse", parsing)

        completion = self.annotated_source(15, 18)
        self.assertIn("self.tools.is_done", completion)
        self.assertIn("self.trajectory.add", completion)
        self.assertIn("return response.content", completion)

        action = self.annotated_source(20, 20)
        self.assertIn("return self._execute_action(response)", action)


if __name__ == "__main__":
    unittest.main()

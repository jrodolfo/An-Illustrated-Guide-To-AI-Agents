import unittest

from illustrated_agents.llm import Response
from illustrated_agents.tools import NativeTools, Tools


class PromptToolCallParsingTests(unittest.TestCase):
    def setUp(self):
        self.tools = Tools()

    def test_non_text_content_is_unchanged(self):
        response = Response(content=None)

        self.assertIs(self.tools.parse(response), response)

    def test_ordinary_text_is_unchanged(self):
        response = Response(content="The answer is 42.")

        self.assertIs(self.tools.parse(response), response)

    def test_parses_tool_with_flexible_key_spacing_and_preserves_metadata(self):
        response = Response(
            content='ACTION: {"tool" : "calculator", "kwargs": {"a": 2}}',
            reasoning="Use a calculator",
            metadata={"model": "test-model"},
        )

        parsed = self.tools.parse(response)

        self.assertEqual(parsed.tool_call["tool"], "calculator")
        self.assertEqual(parsed.tool_call["kwargs"], {"a": 2})
        self.assertEqual(parsed.reasoning, "Use a calculator")
        self.assertEqual(parsed.metadata, {"model": "test-model"})

    def test_accepts_final_answer_string(self):
        response = Response(
            content='{"tool": "final_answer", "kwargs": "Finished"}'
        )

        parsed = self.tools.parse(response)

        self.assertTrue(self.tools.is_done(parsed))
        self.assertEqual(parsed.content, "Finished")

    def test_rejects_incomplete_json(self):
        response = Response(content='{"tool": "calculator"')

        with self.assertRaisesRegex(ValueError, "complete JSON object"):
            self.tools.parse(response)

    def test_rejects_malformed_json(self):
        response = Response(content='{"tool": "calculator", "kwargs": }')

        with self.assertRaisesRegex(ValueError, "Invalid tool call JSON"):
            self.tools.parse(response)

    def test_rejects_missing_or_empty_tool_name(self):
        for content in (
            '{"tool": "", "kwargs": {}}',
            '{"tool": null, "kwargs": {}}',
        ):
            with self.subTest(content=content):
                with self.assertRaisesRegex(ValueError, "non-empty 'tool' name"):
                    self.tools.parse(Response(content=content))

    def test_rejects_non_object_kwargs(self):
        response = Response(
            content='{"tool": "calculator", "kwargs": [1, 2]}'
        )

        with self.assertRaisesRegex(ValueError, "'kwargs' must be an object"):
            self.tools.parse(response)

    def test_rejects_non_string_final_answer(self):
        response = Response(
            content='{"tool": "final_answer", "kwargs": {"answer": "Done"}}'
        )

        with self.assertRaisesRegex(ValueError, "must be a string"):
            self.tools.parse(response)


class NativeToolCallParsingTests(unittest.TestCase):
    def setUp(self):
        self.tools = NativeTools()

    def test_parses_string_arguments_and_preserves_response_data(self):
        response = Response(
            content=None,
            reasoning="Call the calculator",
            tool_call={
                "id": "call_123",
                "type": "function",
                "function": {
                    "name": "calculator",
                    "arguments": '{"a": 2, "b": 3}',
                },
            },
            metadata={"model": "test-model"},
        )

        parsed = self.tools.parse(response)

        self.assertEqual(parsed.tool_call["id"], "call_123")
        self.assertEqual(parsed.tool_call["tool"], "calculator")
        self.assertEqual(parsed.tool_call["kwargs"], {"a": 2, "b": 3})
        self.assertEqual(parsed.reasoning, "Call the calculator")
        self.assertEqual(parsed.metadata, {"model": "test-model"})

    def test_accepts_predecoded_arguments(self):
        response = Response(
            tool_call={
                "function": {
                    "name": "calculator",
                    "arguments": {"a": 2},
                }
            }
        )

        parsed = self.tools.parse(response)

        self.assertEqual(parsed.tool_call["kwargs"], {"a": 2})

    def test_rejects_missing_function_data(self):
        with self.assertRaisesRegex(ValueError, "'function' object"):
            self.tools.parse(Response(tool_call={"id": "call_123"}))

    def test_rejects_empty_function_name(self):
        response = Response(
            tool_call={"function": {"name": "", "arguments": {}}}
        )

        with self.assertRaisesRegex(ValueError, "non-empty function name"):
            self.tools.parse(response)

    def test_rejects_malformed_arguments_json(self):
        response = Response(
            tool_call={
                "function": {
                    "name": "calculator",
                    "arguments": '{"a": }',
                }
            }
        )

        with self.assertRaisesRegex(ValueError, "arguments JSON"):
            self.tools.parse(response)

    def test_rejects_non_object_arguments(self):
        for arguments in ("[]", [], None):
            with self.subTest(arguments=arguments):
                response = Response(
                    tool_call={
                        "function": {
                            "name": "calculator",
                            "arguments": arguments,
                        }
                    }
                )
                with self.assertRaisesRegex(ValueError, "must be an object"):
                    self.tools.parse(response)


if __name__ == "__main__":
    unittest.main()

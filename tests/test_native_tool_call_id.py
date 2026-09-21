import copy
import unittest

from illustrated_agents.agent import TinyAgent
from illustrated_agents.llm import Response
from illustrated_agents.memory import Memory, MultimodalMemory, TrimmingMemory
from illustrated_agents.planning import NativeReAct
from illustrated_agents.tools import NativeTools


TOOL_CALL = {
    "id": "call_123",
    "type": "function",
    "function": {"name": "today", "arguments": "{}"},
}


class FakeLLM:
    def __init__(self):
        self.requests = []
        self.responses = [
            Response(content=None, tool_call=TOOL_CALL),
            Response(content="Done"),
        ]

    def generate(self, messages, tools=None):
        self.requests.append(copy.deepcopy(messages))
        return self.responses.pop(0)


class NativeToolCallIdTests(unittest.TestCase):
    def test_native_parser_preserves_tool_call_id(self):
        response = NativeTools().parse(Response(tool_call=TOOL_CALL))

        self.assertEqual(response.tool_call["id"], "call_123")
        self.assertEqual(response.tool_call["tool"], "today")
        self.assertEqual(response.tool_call["kwargs"], {})

    def test_memory_stores_tool_call_id_only_when_provided(self):
        memory = Memory()

        memory.add("tool", "2026-09-21", tool_call_id="call_123")
        memory.add("user", "Hello")

        self.assertEqual(memory.messages[0]["tool_call_id"], "call_123")
        self.assertNotIn("tool_call_id", memory.messages[1])

    def test_memory_subclasses_forward_tool_call_id(self):
        for memory in (MultimodalMemory(), TrimmingMemory()):
            with self.subTest(memory=type(memory).__name__):
                memory.add("tool", "result", tool_call_id="call_123")
                self.assertEqual(memory.messages[-1]["tool_call_id"], "call_123")

    def test_agent_pairs_native_tool_result_with_assistant_call(self):
        llm = FakeLLM()
        tools = NativeTools()
        tools.add_tool("today", lambda: "2026-09-21")
        agent = TinyAgent(
            llm=llm,
            memory=MultimodalMemory(),
            tools=tools,
            planner=NativeReAct(max_steps=2),
            display=lambda *args: None,
        )

        result = agent.run("What is today's date?")

        self.assertEqual(result, "Done")
        messages = llm.requests[1]
        self.assertEqual(messages[-2]["tool_calls"][0]["id"], "call_123")
        self.assertEqual(messages[-1]["role"], "tool")
        self.assertEqual(messages[-1]["tool_call_id"], "call_123")
        self.assertEqual(messages[-1]["content"], "2026-09-21")


if __name__ == "__main__":
    unittest.main()

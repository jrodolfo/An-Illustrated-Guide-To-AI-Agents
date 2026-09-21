import json
import unittest
from unittest.mock import patch

from illustrated_agents.llm import EmbeddingModel, LLM


CHAT_RESPONSE = {
    "model": "test-model",
    "choices": [{"message": {"content": "Hello"}}],
    "usage": {"prompt_tokens": 2, "completion_tokens": 1},
}

EMBEDDING_RESPONSE = {"data": [{"embedding": [0.1, 0.2, 0.3]}]}


def configure_response(mock_urlopen, payload):
    response = mock_urlopen.return_value.__enter__.return_value
    response.read.return_value = json.dumps(payload).encode()


class HttpTimeoutTests(unittest.TestCase):
    def test_llm_default_timeout_is_sixty_seconds(self):
        self.assertEqual(LLM(model="test-model").timeout, 60.0)

    @patch("illustrated_agents.llm.urllib.request.urlopen")
    def test_llm_passes_custom_timeout_and_parses_response(self, mock_urlopen):
        configure_response(mock_urlopen, CHAT_RESPONSE)
        llm = LLM(model="test-model", timeout=12.5)

        response = llm.generate([{"role": "user", "content": "Hi"}])

        self.assertEqual(mock_urlopen.call_args.kwargs["timeout"], 12.5)
        self.assertEqual(response.content, "Hello")
        self.assertEqual(response.metadata["model"], "test-model")

    def test_embedding_default_timeout_is_sixty_seconds(self):
        self.assertEqual(EmbeddingModel(model="test-embedding").timeout, 60.0)

    @patch("illustrated_agents.llm.urllib.request.urlopen")
    def test_embedding_passes_custom_timeout_and_parses_response(
        self, mock_urlopen
    ):
        configure_response(mock_urlopen, EMBEDDING_RESPONSE)
        model = EmbeddingModel(model="test-embedding", timeout=7.0)

        embedding = model.embed("hello")

        self.assertEqual(mock_urlopen.call_args.kwargs["timeout"], 7.0)
        self.assertEqual(embedding, [0.1, 0.2, 0.3])


if __name__ == "__main__":
    unittest.main()

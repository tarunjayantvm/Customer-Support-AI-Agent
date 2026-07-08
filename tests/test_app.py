import unittest
from unittest.mock import patch

import app


class SupportAgentTests(unittest.TestCase):
    def test_login_query_requests_more_context(self):
        response, escalated = app.generate_support_response("I cannot log in", [])
        self.assertFalse(escalated)
        self.assertIn("need a bit more context", response.lower())

    def test_password_query_returns_knowledge_base_guidance(self):
        response, escalated = app.generate_support_response("I forgot my password", [])
        self.assertFalse(escalated)
        self.assertIn("password reset", response.lower())
        self.assertIn("reset the password", response.lower())

    def test_billing_query_escalates(self):
        response, escalated = app.generate_support_response("I was charged twice", [])
        self.assertTrue(escalated)
        self.assertIn("escalating", response.lower())

    def test_openrouter_settings_are_used_for_llm(self):
        class FakeCompletions:
            def __init__(self):
                self.last_call = None

            def create(self, model, temperature, messages):
                self.last_call = {
                    "model": model,
                    "temperature": temperature,
                    "messages": messages,
                }
                return type(
                    "Response",
                    (),
                    {"choices": [type("Choice", (), {"message": type("Message", (), {"content": "OpenRouter reply"})()})()]},
                )()

        class FakeOpenAI:
            instances = []

            def __init__(self, api_key=None, base_url=None):
                self.api_key = api_key
                self.base_url = base_url
                self.chat = type("Chat", (), {"completions": FakeCompletions()})()
                FakeOpenAI.instances.append(self)

        with patch.dict(
            app.os.environ,
            {
                "OPENROUTER_API_KEY": "or-key",
                "LLM_BASE_URL": "https://openrouter.ai/api/v1/chat/completions",
                "LLM_MODEL": "poolside/laguna-m.1:free",
            },
            clear=False,
        ):
            with patch.object(app, "OpenAI", FakeOpenAI):
                response, escalated = app.llm_enhanced_response("hello", [])

        self.assertFalse(escalated)
        self.assertEqual("OpenRouter reply", response)
        self.assertEqual("or-key", FakeOpenAI.instances[0].api_key)
        self.assertEqual("https://openrouter.ai/api/v1", FakeOpenAI.instances[0].base_url)
        self.assertEqual("poolside/laguna-m.1:free", FakeOpenAI.instances[0].chat.completions.last_call["model"])


if __name__ == "__main__":
    unittest.main()

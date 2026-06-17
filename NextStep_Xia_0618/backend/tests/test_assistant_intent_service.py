import unittest

from app.services.ai.assistant_intent_service import (
    OpenAIAssistantIntentService,
    parse_assistant_intent,
)
from app.services.ai.llm_client import LLMGenerationError
from app.services.ai.schemas import AssistantIntentRequest, OpenAISettings


class FakeTransport:
    def __init__(self, response):
        self.response = response
        self.payload = None

    def create_response(self, payload):
        self.payload = payload
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


class AssistantIntentServiceTest(unittest.TestCase):
    def setUp(self):
        self.kcs = {
            "KC001": "Variables and Expressions",
            "KC003": "Loops",
            "KC006": "Lists",
        }

    def test_openai_service_returns_valid_structured_intent(self):
        transport = FakeTransport(
            {
                "output_text": (
                    '{"kc_code":"KC003","difficulty":"hard",'
                    '"use_weakest_kc":false}'
                )
            }
        )
        service = OpenAIAssistantIntentService(
            settings=OpenAISettings(api_key="test-key", model="test-model"),
            transport=transport,
        )

        intent = service.parse_intent(
            AssistantIntentRequest(
                message="I want a hard loops exercise",
                available_kcs=self.kcs,
            )
        )

        self.assertEqual(intent.kc_code, "KC003")
        self.assertEqual(intent.difficulty, "hard")
        self.assertFalse(intent.use_weakest_kc)
        self.assertEqual(transport.payload["model"], "test-model")

    def test_openai_service_rejects_unknown_kc(self):
        transport = FakeTransport(
            {
                "output_text": (
                    '{"kc_code":"KC999","difficulty":"easy",'
                    '"use_weakest_kc":false}'
                )
            }
        )
        service = OpenAIAssistantIntentService(
            settings=OpenAISettings(api_key="test-key"),
            transport=transport,
        )

        with self.assertRaises(LLMGenerationError):
            service.parse_intent(
                AssistantIntentRequest(
                    message="Give me an easy unknown topic",
                    available_kcs=self.kcs,
                )
            )

    def test_parser_falls_back_to_keywords_when_openai_fails(self):
        transport = FakeTransport(LLMGenerationError("service unavailable"))
        service = OpenAIAssistantIntentService(
            settings=OpenAISettings(api_key="test-key"),
            transport=transport,
        )

        result = parse_assistant_intent(
            message="Please give me an easy list exercise",
            available_kcs=self.kcs,
            openai_service=service,
        )

        self.assertEqual(result.intent.kc_code, "KC006")
        self.assertEqual(result.intent.difficulty, "easy")
        self.assertFalse(result.intent.use_weakest_kc)
        self.assertEqual(result.source, "fallback")

    def test_parser_uses_weakest_kc_for_general_request(self):
        service = OpenAIAssistantIntentService(
            settings=OpenAISettings(api_key=""),
            transport=FakeTransport({}),
        )

        result = parse_assistant_intent(
            message="Recommend something useful",
            available_kcs=self.kcs,
            openai_service=service,
        )

        self.assertIsNone(result.intent.kc_code)
        self.assertTrue(result.intent.use_weakest_kc)
        self.assertEqual(result.source, "fallback")

    def test_keyword_parser_treats_basic_as_difficulty_not_variables_topic(self):
        service = OpenAIAssistantIntentService(
            settings=OpenAISettings(api_key=""),
            transport=FakeTransport({}),
        )

        result = parse_assistant_intent(
            message="Give me a basic loops exercise",
            available_kcs=self.kcs,
            openai_service=service,
        )

        self.assertEqual(result.intent.kc_code, "KC003")
        self.assertEqual(result.intent.difficulty, "easy")


if __name__ == "__main__":
    unittest.main()

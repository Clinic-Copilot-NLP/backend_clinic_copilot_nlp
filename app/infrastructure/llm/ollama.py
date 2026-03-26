import logging

from app.infrastructure.llm.base import LLMProvider, LLMResponse

logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    def __init__(self, *args, **kwargs) -> None:
        logger.warning(
            "OllamaProvider initialized but not yet implemented. "
            "Set LLM_PROVIDER=openai in your .env file."
        )

    @property
    def provider_name(self) -> str:
        return "ollama"

    async def generate(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        raise NotImplementedError(
            "OllamaProvider is not yet implemented. "
            "Set LLM_PROVIDER=openai in your .env file to use the OpenAI provider."
        )

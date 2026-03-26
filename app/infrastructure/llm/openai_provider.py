import logging
from openai import AsyncOpenAI, APIError, APIConnectionError, RateLimitError
from app.infrastructure.llm.base import LLMProvider, LLMResponse, LLMProviderError
from app.core.config import Settings

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    def __init__(self, settings: Settings) -> None:
        self._model = settings.MODEL_NAME
        self._client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY.get_secret_value()
        )

    @property
    def provider_name(self) -> str:
        return "openai"

    async def generate(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        try:
            logger.debug(f"Calling OpenAI model={self._model}")
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
            )
            content = response.choices[0].message.content or "Sin respuesta"
            usage = response.usage
            return LLMResponse(
                content=content,
                tokens_input=usage.prompt_tokens if usage else None,
                tokens_output=usage.completion_tokens if usage else None,
                model=self._model,
                provider=self.provider_name,
            )
        except RateLimitError as e:
            raise LLMProviderError(
                "OpenAI rate limit exceeded", self.provider_name, e
            ) from e
        except APIConnectionError as e:
            raise LLMProviderError(
                "Cannot connect to OpenAI API", self.provider_name, e
            ) from e
        except APIError as e:
            raise LLMProviderError(
                f"OpenAI API error: {e.message}", self.provider_name, e
            ) from e
        except Exception as e:
            raise LLMProviderError(
                f"Unexpected error calling OpenAI: {e}", self.provider_name, e
            ) from e

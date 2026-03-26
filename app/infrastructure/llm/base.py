from abc import ABC, abstractmethod

from pydantic import BaseModel


class LLMResponse(BaseModel):
    content: str
    tokens_input: int | None = None
    tokens_output: int | None = None
    model: str
    provider: str


class LLMProviderError(Exception):
    def __init__(
        self,
        message: str,
        provider: str,
        original_error: Exception | None = None,
    ):
        super().__init__(message)
        self.provider = provider
        self.original_error = original_error


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str) -> LLMResponse: ...

    @property
    @abstractmethod
    def provider_name(self) -> str: ...

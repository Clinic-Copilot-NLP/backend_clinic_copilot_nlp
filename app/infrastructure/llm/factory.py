from app.core.config import Settings
from app.infrastructure.llm.base import LLMProvider


def get_llm_provider(settings: Settings) -> LLMProvider:
    provider_name = settings.LLM_PROVIDER.lower()

    if provider_name == "openai":
        from app.infrastructure.llm.openai_provider import OpenAIProvider

        return OpenAIProvider(settings)
    elif provider_name == "ollama":
        from app.infrastructure.llm.ollama import OllamaProvider

        return OllamaProvider(settings)
    elif provider_name == "huggingface":
        from app.infrastructure.llm.huggingface import HuggingFaceProvider

        return HuggingFaceProvider(settings)
    else:
        raise ValueError(
            f"Unknown LLM provider: '{provider_name}'. "
            f"Valid options: 'openai', 'ollama', 'huggingface'"
        )

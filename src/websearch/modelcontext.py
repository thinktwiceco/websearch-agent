"""Web search model context management module.

This module provides configuration and context management for different LLM providers,
currently supporting Ollama and TogetherAI integrations.
"""

from typing import Literal

from pydantic import Field
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_settings import BaseSettings

from websearch.root_logger import root_logger

logger = root_logger.getChild(__name__)

together_allowed_models = [
    "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    "deepseek-r1/deepseek-r1-720b-instruct",
]

ollama_allowed_models = [
    "qwen2.5:7b",
    "llama3.1:8b",
    "deepseek-r1:8b",
    "llama3.1:8b-instruct-q4_1",
]


class AppContext(BaseSettings):
    """Application context configuration for LLM providers.

    This class manages configuration settings for different LLM providers,
    handling environment variables, default values, and provider-specific logic.

    Attributes:
        provider: The LLM provider to use ('ollama' or 'together').
        togetherai_api_key: API key for TogetherAI.
        togetherai_base_url: Base URL for TogetherAI API.
        ollama_base_url: Base URL for Ollama API.
        ollama_model: Model name to use with Ollama.
        togetherai_model: Model name to use with TogetherAI.
        stream_response: Whether to stream model responses.
    """

    provider: Literal["ollama", "together"] = Field(alias="PROVIDER")
    togetherai_api_key: str = Field(alias="TOGETHERAI_API_KEY")
    togetherai_base_url: str = Field(alias="TOGETHERAI_BASE_URL")
    ollama_base_url: str = Field(
        alias="OLLAMA_BASE_URL", default="http://localhost:11434/v1"
    )
    ollama_model: str = Field(alias="OLLAMA_MODEL", default="qwen2.5:7b")
    togetherai_model: str = Field(
        alias="TOGETHERAI_MODEL", default="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"
    )
    stream_response: bool = Field(alias="STREAM_RESPONSE", default=False)
    model_config = {
        "env_file": ".env",
        "extra": "allow",
    }

    def get_model_provider(self) -> OpenAIModel:
        """Get the configured OpenAI-compatible model provider.

        Returns:
            OpenAIModel: Configured model provider ready for use.
        """

        def cachable_fn(p: Literal["ollama", "together"]):
            provider = OpenAIProvider(api_key=self.api_key, base_url=self.base_url)

            openai_model = OpenAIModel(model_name=self.model, provider=provider)

            return openai_model

        return cachable_fn(self.provider)

    @property
    def api_key(self) -> str | None:
        """Get the appropriate API key for the configured provider.

        Returns:
            str | None: The API key for TogetherAI or None for Ollama.
        """
        if self.provider == "together":
            return self.togetherai_api_key
        elif self.provider == "ollama":
            return None

    @property
    def model(self) -> str:
        """Get the model name for the configured provider.

        Returns:
            str: The model name to use.

        Raises:
            ValueError: If an invalid provider is configured.
        """
        if self.provider == "together":
            return self.togetherai_model
        elif self.provider == "ollama":
            return self.ollama_model
        else:
            raise ValueError(f"Invalid provider: {self.provider}")

    @property
    def base_url(self) -> str:
        """Get the base URL for the configured provider's API.

        Returns:
            str: The base URL to use for API requests.

        Raises:
            ValueError: If an invalid provider is configured.
        """
        if self.provider == "together":
            return self.togetherai_base_url
        elif self.provider == "ollama":
            return self.ollama_base_url
        else:
            raise ValueError(f"Invalid provider: {self.provider}")

    def __str__(self) -> str:
        """Get a string representation of the AppContext.

        Returns:
            str: String representation including provider, model, and base URL.
        """
        return f"AppContext(provider={self.provider}, model={self.model}, base_url={self.base_url})"


ctx = AppContext()
logger.info(f"Context: {ctx}")

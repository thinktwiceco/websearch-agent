"""Syntetizer agent module for web search operations.

This module provides an agent for synthesizing the answer from the pages.
"""

from pydantic import BaseModel, Field
from pydantic_ai import Agent

from websearch.modelcontext import ctx
from websearch.prompts import SystemPrompt
from websearch.root_logger import root_logger

logger = root_logger.getChild(__name__)

syste_prompt = SystemPrompt(
    definition="You are a summarizing agent.",
    instructions=[
        "Read the user's question",
        "Read the chunks content",
        "Answer the user question based on the chunks content",
        "Answer the question also using your own knowledge",
    ],
    dontdo=[
        "Don't make up information",
        "Only report information that are in the chunk content",
    ],
)


class Response(BaseModel):
    """Response from the syntetizer agent.

    Args:
        answer: Answer to the user question based on the page content.
        links: List of links that are used to answer the question.
        error: Error message if the syntetizer failed.
    """

    answer: str | None = Field(
        description="Answer to the user question based on the page content."
    )
    sources: list[str] | None = Field(
        description="List of links that are used to answer the question."
    )
    error: str | None = Field(description="Error message if the syntetizer failed.")


syntetizerAgent = Agent(
    model=ctx.get_model_provider(),
    system_prompt=syste_prompt.text(),
    result_type=Response,
    result_retries=3,
)

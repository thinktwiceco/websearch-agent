"""Explorer agent module for web search operations.

This module provides an agent for exploring the web for the most relevant pages.
"""

from pydantic import BaseModel, Field
from pydantic_ai import Agent

from websearch.modelcontext import ctx
from websearch.prompts import SystemPrompt
from websearch.root_logger import root_logger
from websearch.tools.websearch import WebSearchTool

logger = root_logger.getChild(__name__)

system_prompt = SystemPrompt(
    definition="You are an agent that explores the web for information.",
    instructions=[
        "- Read the query",
        "- Determine what kind of information the user is requesting",
        "- Perform a web search to find the most relevant pages",
        "- Select the relevant content from the pages",
        "- Return the required object in the response.",
    ],
    dontdo=[
        "- Don't return pages that are not relevant to the query",
    ],
)

logger.debug_system_prompt("Explorer", system_prompt.text())


class Page(BaseModel):
    """Page model.

    This class represents a page that is relevant for answering the question.
    """

    url: str = Field(description="The url of the page")
    category: str = Field(
        description="The category of the page, for example: 'video', 'news', 'article'"
    )
    content: str = Field(
        description="The syntetized content of the page with the key information needed to answer the question"
    )


class Response(BaseModel):
    """Response from the query generator agent.

    Args:
        links: List of links that are relevant for answering the question if the operation was successful.
        error: Error message if the operation fails.
    """

    pages: list[Page] | None = Field(
        default=None,
        description="List of pages that are relevant for answering the question if the operation was successful.",
    )
    error: str | None = Field(
        default=None, description="Error message if the operation fails."
    )


explorerAgent = Agent(
    model=ctx.get_model_provider(),
    system_prompt=system_prompt.text(),
    tools=[WebSearchTool],
    result_type=Response,
    result_retries=3,
)

from pydantic import BaseModel
from pydantic_ai import Agent
from websearch.prompts import SystemPrompt
from websearch.root_logger import root_logger
from websearch.modelcontext import ctx
from websearch.tools.searchlinks import GoogleSearchLinksTool
from websearch.state import Link
from pydantic import Field

logger = root_logger.getChild(__name__)

syste_prompt = SystemPrompt(
    definition="You are a helpful assistant that finds valid links to answer a user query.",
    instructions=[
        "- Read the query",
        "- User google_search_links and run the query.",
        "- The tool will return a list of links.",
        "- Each link contains a `url` and a `description` fields.",
        "- The `description` field contains the title of the link.",
        "- Select the most relevant links based on the query.",
        "- Return the links in a JSON array.",
        "- The returned `url` field should be the same as the `url` field in the tool response.",
    ],
    dontdo=[
        "- Don't generate links that are not relevant to the queries",
        "- Don't generate links that are not valid",
        "- Don't generate links that are not secure",
        "- Don't generate links that are not safe",
        "- Don't generate links that are not trustworthy",
        "- Don't generate links that are not reliable",
    ],
)

logger.debug_system_prompt("Linkfinder", syste_prompt.text())

class Response(BaseModel):
    """
    Response from the query generator agent.

    Args:
        links: List of links that are relevant for answering the question if the operation was successful.
        error: Error message if the operation fails.
    """
    links: list[Link] | None = Field(default=None, description="List of links that are relevant for answering the question if the operation was successful.")
    error: str | None = Field(default=None, description="Error message if the operation fails.")


linkfinderAgent = Agent(
    model=ctx.get_model_provider(),
    system_prompt=syste_prompt.text(),
    tools=[GoogleSearchLinksTool],
    result_type=Response,
    result_retries=3,
)
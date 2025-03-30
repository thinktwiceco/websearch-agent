from pydantic import BaseModel
from pydantic_ai import Agent
from websearch.prompts import SystemPrompt
from websearch.root_logger import root_logger
from websearch.modelcontext import ctx

logger = root_logger.getChild(__name__)

syste_prompt = SystemPrompt(
    definition="You are a helpful assistant that generates queries based on a user's question.",
    instructions=[
        "Read the user's question",
        "Define the main topic of the question",
        "Generate 3 queries that are relevant for answering the question",
        "If the question is not clear, return an error message",
    ],
    dontdo=[
        "Don't generate queries that are not relevant to the question",
        "Don't generate queries that are too broad",
        "Don't generate queries that are too vague",
        "Don't generate queries that are too long",
    ],
)

class Response(BaseModel):
    """
    Response from the query generator agent.

    Args:
        queries: List of queries that are relevant for answering the question if the query generation was successful.
        error: Error message if the query generation failed.
    """
    queries: list[str] | None = None
    error: str | None = None


querygenAgent = Agent(
    model=ctx.get_model_provider(),
    system_prompt=syste_prompt.text(),
    result_type=Response,
    result_retries=3,
)
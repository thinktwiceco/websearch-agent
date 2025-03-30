from pydantic import BaseModel
from pydantic_ai import Agent
from websearch.prompts import SystemPrompt
from websearch.root_logger import root_logger
from websearch.modelcontext import ctx
from pydantic import Field

logger = root_logger.getChild(__name__)

syste_prompt = SystemPrompt(
    definition="You will receive a chunk of text and a user query. You will summarize the text retaining the most important information relevant to the user query.",
    instructions=[
       "- You will receive chunks of a webpage in pieces.",
       "- Once you receive a chunk, return a summarized version of the chunk "
    ],
    dontdo=[
        "Don't add considerations",
        "Don't alter the meaning of the text"
    ],
)

logger.debug_system_prompt("Chunkanalyzer", syste_prompt.text())

class Response(BaseModel):
    """
    Response from the query generator agent.

    Args:
        summary: Summary of text chunk
        error: Error message if the operation fails.
    """
    chunk_analysis: str = Field(description="Analysis of the text chunk")
    error: str | None = Field(description="Error message if the operation fails.")


chunkanalyzerAgent = Agent(
    model=ctx.get_model_provider(),
    system_prompt=syste_prompt.text(),
    result_type=Response,
    result_retries=3,
)
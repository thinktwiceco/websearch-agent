from pydantic import BaseModel
from pydantic_ai import Agent
from websearch.prompts import SystemPrompt
from websearch.root_logger import root_logger
from websearch.modelcontext import ctx
from websearch.tools.navigatelinks import NavigateLinksTool
from websearch.state import Page
from pydantic import Field
logger = root_logger.getChild(__name__)

syste_prompt = SystemPrompt(
    definition="You are a helpful assistant will analyze a summary of a webpage, and determine if it is relevant to the user query.",
    instructions=[
       "- You will receive a **Summary** of a webpage",
       "- You will receive the **Link** from where the summary was extracted",
       "- You will receive a **User query** "
       "- Determine if the summary content is relevant to the user query",
       "- If it's relevant, return a json obejct with the following fields: "
       "  - **summary**: The summary of the webpage"
       "  - **url**: The link from where the summary was extracted"
    ],
    dontdo=[],
)

logger.debug_system_prompt("Linknav", syste_prompt.text())

class Response(BaseModel):
    """
    Response from the query generator agent.

    Args:
        summary: Summary of text chunk
        error: Error message if the operation fails.
    """
    page: Page = Field(description="Information about the page")
    error: str | None = Field(description="Error message if the operation fails.")


linknavAgent = Agent(
    model=ctx.get_model_provider(),
    system_prompt=syste_prompt.text(),
    tools=[NavigateLinksTool],
    result_type=Response,
    result_retries=3,
)
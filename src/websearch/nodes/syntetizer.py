from typing import Any
from websearch.agents.syntetizer import syntetizerAgent
from websearch.prompts import UserPrompt
from websearch.root_logger import root_logger
from websearch.state import GraphState

logger = root_logger.getChild(__name__)


async def syntetizer(state: GraphState) -> Any:
    user_query = state["user_query"]
    pages = state["pages"]
    pages_content = ""

    for page in pages:
        pages_content += f"##{page.url}\n{page.summary}\n\n"

    message = f"User query: {user_query}\nPages: {pages_content}"
    prompt = UserPrompt(
        query=message,
        steps=[
            "Read the user query",
            "Read the pages content",
            "Answer the user query based on the pages content",
            "Report all the links that are used to answer the question",
        ]
    )
    logger.log_prompt("Syntetizer", message)
    agent_response = await syntetizerAgent.run(prompt.text())
    answer = agent_response.data.answer
    logger.log_response("Syntetizer", answer)

    if agent_response.data.error:
        return {"error": agent_response.data.error}

    return {"answer": agent_response.data.answer, "sources": agent_response.data.sources}

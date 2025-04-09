"""Synthesizer node for web search operations.

This module provides a node for synthesizing the answer from the pages.
"""

from typing import Any

from websearch.agents.syntetizer import syntetizerAgent
from websearch.prompts import UserPrompt
from websearch.root_logger import root_logger
from websearch.state import GraphState

logger = root_logger.getChild(__name__)


async def syntetizer(state: GraphState) -> Any:
    """Synthesize the answer from the pages.

    This function takes the user query and the pages and synthesizes the answer.
    """
    user_query = state["user_query"]
    pages = state["pages"]

    pages_content = ""
    for page in pages:
        pages_content += f"## Page: {page['url']}: Category: {page['category']}\nContent:\n{page['content']}\n\n"

    message = f"User query: {user_query}\n Pages: {pages_content}"
    prompt = UserPrompt(
        query=message,
        steps=[
            "Read the user query",
            "Read the pages content",
            "Answer the user query based on the pages content",
            "Report all the pages that are used to answer the question",
            "Report all the sources that are used to answer the question",
            "The sources are the Pages URLs",
        ],
    )

    logger.log_prompt("Syntetizer", message)
    agent_response = await syntetizerAgent.run(prompt.text())
    answer = agent_response.data.answer

    if answer:
        logger.info(f"Answer: {answer}")
        logger.info(f"Sources: {agent_response.data.sources}")

    if agent_response.data.error:
        return {"error": agent_response.data.error}

    return {
        "answer": agent_response.data.answer,
        "sources": agent_response.data.sources,
    }

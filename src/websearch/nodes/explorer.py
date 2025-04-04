

from typing import TypedDict
from websearch.prompts import UserPrompt
from websearch.agents.explorer import explorerAgent
from langgraph.types import Command


from websearch.root_logger import root_logger

logger = root_logger.getChild(__name__)


class ExplorerState(TypedDict):
    agent_query: str
    user_query: str
    result_limit: int


async def explorer(state: ExplorerState):
    agent_query = state['agent_query']

    if not agent_query:
        return {"error": "No agent query provided"}

    user_query = state['user_query']

    if not user_query:
        return {"error": "No user query provided"}

    result_limit = state.get("result_limit", 5)

    message = f"""
    In order to answer the user query: {user_query}
    The Agent request to perform the following webserach: {agent_query}
    Limit the results to {result_limit} pages.
    """

    prompt = UserPrompt(
        query=message,
        steps=[
            "Read the user query",
            "Read the agent query",
            "Perform a web search to find the most relevant pages",
            "Analyze the results and think about the user query and the agent query",
            f"Select the top {result_limit} pages that are most relevant to the user query and the agent query",
            "Return the pages in a JSON list according to the required format"
        ]
    )

    logger.log_prompt("Explorer", prompt.text())

    explorer_response = await explorerAgent.run(prompt.text())

    logger.log_response("Explorer", explorer_response.data.model_dump_json(indent=4))

    if explorer_response.data.error:
        return {"error": explorer_response.data.error}

    return Command(
        goto="syntetizer",
        update={
            "pages": [p.model_dump() for p in explorer_response.data.pages] or [],
        }
    )


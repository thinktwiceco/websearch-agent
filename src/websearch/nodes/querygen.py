"""Query generation node for web search operations.

This module provides a node for generating queries from a user query.
"""

from typing import Any, Literal

from langgraph.constants import Send

from websearch.agents.querygen import querygenAgent
from websearch.root_logger import root_logger
from websearch.state import GraphState

logger = root_logger.getChild(__name__)


async def querygen(state: GraphState) -> Any:
    """Generate queries from a user query.

    This function takes the user query and generates queries using the querygenAgent.
    """
    user_query = state["user_query"]
    message = f"Query: {user_query}\n\n"
    logger.log_prompt("Querygen", message)
    agent_response = await querygenAgent.run(message)
    queries = "\n".join(agent_response.data.queries)
    logger.log_response("Querygen", queries)

    if agent_response.data.error:
        return {"error": agent_response.data.error}

    return {
        "queries": agent_response.data.queries or [],
        "user_query": user_query,
    }


def query_gen_router(state: GraphState) -> Literal["explorer", "__end__"]:
    """Router for query generation.

    This function takes the state and returns a list of actions to be taken.
    """
    if state.get("error"):
        return "__end__"

    assert state["user_query"]

    return [
        Send(
            "explorer",
            {
                "agent_query": query,
                "user_query": state["user_query"],
                "result_limit": state["result_limit"],
            },
        )
        for query in state["queries"]
    ]

from typing import Any, Literal
from websearch.agents.querygen import querygenAgent
from websearch.root_logger import root_logger
from websearch.state import GraphState
from langchain_core.messages import HumanMessage
from langgraph.constants import Send

logger = root_logger.getChild(__name__)


async def querygen(state: GraphState) -> Any:
    user_query = state['user_query']
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
    if state.get("error"):
        return "__end__"

    assert state['user_query']

    return [Send("explorer", {
        "agent_query": query,
        "user_query": state["user_query"],
        "result_limit": state["result_limit"],
    }) for query in state['queries']]

from typing import Any, Literal
from websearch.agents.querygen import querygenAgent
from websearch.root_logger import root_logger
from websearch.state import GraphState
from langchain_core.messages import HumanMessage
from langgraph.constants import Send

logger = root_logger.getChild(__name__)


async def querygen(state: GraphState) -> Any:
    last_message: HumanMessage = state["messages"][-1]
    query_limit = state["generate_query_limit"]
    message = f"Query: {last_message.content}\n\nGenerate MAX {query_limit} queries"
    logger.log_prompt("Querygen", message)
    agent_response = await querygenAgent.run(message)
    queries = "\n".join(agent_response.data.queries)
    logger.log_response("Querygen", queries)

    if agent_response.data.error:
        return {"error": agent_response.data.error}

    return {
        "queries": agent_response.data.queries or [],
        "user_query": last_message.content,
    }

def query_gen_router(state: GraphState) -> Literal["linksfinder", "__end__"]:
    if state.get("error"):
        return "__end__"

    return [Send("linksfinder", {
        "query": query,
        "link_limit": state["link_limit"],
        "user_query": state["user_query"],
    }) for query in state['queries']]

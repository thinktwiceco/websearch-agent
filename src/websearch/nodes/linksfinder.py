import operator
from typing import Annotated, Any, Literal, TypedDict
from websearch.prompts import UserPrompt
from websearch.root_logger import root_logger
from langgraph.constants import Send
from websearch.agents.linkfinder import linkfinderAgent
from websearch.state import Link

logger = root_logger.getChild(__name__)

class LinkFinderState(TypedDict):
    query: str
    links: Annotated[list[Link], operator.add]
    user_query: str
    link_limit: int

def link_to_str(links: list[Link] | None) -> str:
    if links is None or len(links) == 0:
        return "None"

    retval = ""

    for link in links:
        retval += f"-{link.url} - {link.description}\n"

    return retval

async def linksfinder(state: LinkFinderState) -> Any:

    prompt = UserPrompt(
        query=(
            f"Query: {state['query']}\n"
        ),
        steps=[
            "1. Read the query.",
            "2. Search for the most relevant links that answer the query using google_search_links tool",
            "3. Return the links in a JSON array.",
            f"4. Generate MAX {state['link_limit']} link(s)",
        ]
    )
    logger.log_prompt("Linksfinder", prompt.text())
    agent_response = await linkfinderAgent.run(prompt.text())

    links = "\n- ".join([link.url for link in agent_response.data.links])
    logger.log_response("Linksfinder", links)

    if agent_response.data.error:
        return {"error": agent_response.data.error}

    return {
        "links": agent_response.data.links or [],
        "user_query": state["user_query"],
    }

def linksfinder_router(state: LinkFinderState) -> Literal["linknav", "__end__"]:
    if state.get("error"):
        return "__end__"

    return [Send("linknav", {
        "link": link,
        "user_query": state["user_query"],
    }) for link in state["links"]]
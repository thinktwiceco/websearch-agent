from typing import Any
import uuid
from websearch.graph import graph
from langchain_core.messages import HumanMessage

from websearch.state import GraphState


async def exec(
        question: str,
        *,
        generate_query_limit: int = 1,
        link_limit: int = 1
) -> Any:

    config = {
        "thread_id": str(uuid.uuid4()),
        "timeout": 1000,
        "max_concurrency": 10,
    }

    state = GraphState(
        generate_query_limit=generate_query_limit,
        link_limit=link_limit,
        messages=[HumanMessage(content=question)],
    )

    async for msg in graph.astream(state, config):
        syntetizer_result = msg.get("syntetizer")
        querygen_result = msg.get("querygen")
        linksfinder_result = msg.get("linksfinder")
        linknav_result = msg.get("linknav")

        if syntetizer_result:
            yield {
                "answer": syntetizer_result.get("answer"),
                "links": syntetizer_result.get("links"),
            }
        elif querygen_result:
            yield {
                "query": querygen_result.get("query"),
            }
        elif linksfinder_result:
            yield {
                "links": linksfinder_result.get("links"),
            }
        elif linknav_result:
            yield {
                "pages": linknav_result.get("pages"),
            }

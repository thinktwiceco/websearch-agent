from typing import Any
import uuid
from websearch.graph import graph
from langchain_core.messages import HumanMessage

from websearch.state import GraphState


async def exec(
        question: str,
        *,
        result_limit: int = 1,
) -> Any:

    config = {
        "thread_id": str(uuid.uuid4()),
        "timeout": 1000,
        "max_concurrency": 10,
    }

    state = GraphState(
        result_limit=result_limit,
        user_query=question,
    )

    async for msg in graph.astream(state, config):
        syntetizer_result = msg.get("syntetizer")
        querygen_result = msg.get("querygen")
        linksfinder_result = msg.get("linksfinder")
        linknav_result = msg.get("linknav")

        if syntetizer_result:
            yield {
                "answer": syntetizer_result.get("answer"),
                "sources": syntetizer_result.get("sources"),
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

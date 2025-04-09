"""Web search query execution module.

This module provides functionality for executing web search queries and streaming results.
It serves as the main interface for the websearch package, allowing users to submit
questions and receive structured search results through an asynchronous streaming API.

The module utilizes a graph-based search system to process queries, generate search terms,
find relevant links, navigate to pages, and synthesize answers from the collected information.

Example:
    ```python
    async for result in exec("What is quantum computing?"):
        if "answer" in result:
            print(f"Answer: {result['answer']}")
            print(f"Sources: {result['sources']}")
        elif "query" in result:
            print(f"Generated query: {result['query']}")
        # ... handle other result types
    ```
"""

import uuid
from typing import Any, AsyncIterator, Dict

from websearch.graph import graph
from websearch.state import GraphState


async def exec(
    question: str,
    *,
    result_limit: int = 1,
) -> AsyncIterator[Dict[str, Any]]:
    """Execute a web search query and stream the results.

    This function processes the given question through a graph-based search system
    and asynchronously yields results as they become available.

    Args:
        question: The search query or question to be processed.
        result_limit: Maximum number of results to return. Defaults to 1.

    Yields:
        Dict containing one of the following result types:
            - {"answer": str, "sources": list} - Synthesized answer with sources
            - {"query": str} - Generated search query
            - {"links": list} - Found links
            - {"pages": list} - Navigation pages
    """
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

"""State management for web search processing.

This module defines the state structure used for web search operations. It
provides a TypedDict implementation that tracks the search process state,
including user queries, result pages, and generated answers.

The module supports a multi-step search workflow where various agents collaborate
to process a user query, find relevant information, and generate an answer.
"""

import operator
from typing import Annotated, TypedDict


class GraphState(TypedDict):
    """State data structure for web search processing graph.

    This TypedDict defines the structure of state data passed between
    agents in the web search processing workflow. It tracks the original
    query, generated search queries, retrieved pages, and the final answer.

    Attributes:
        result_limit: How many links to generate.
        user_query: The original query from the user.
        error: Error message if any occurred during processing.
        queries: List of search queries generated from the user query.
        pages: List of retrieved web pages and their content.
        sources: List of source URLs used to generate the answer.
        answer: The final generated answer to the user's query.
    """

    result_limit: int  # How many links to generate
    user_query: str
    error: Annotated[str | None, lambda x, y: f"{x}\n{y}"]
    queries: Annotated[list[str], operator.add]
    pages: Annotated[list[dict], operator.add]
    sources: list[str]
    answer: str


# Flow Example
#
# 1. Human Message - "What's the capital of France?"
# 2. Query Generator Agent - "Generates 3 queries"
# 3. Links Finder Agent - Based on the queries, find the most relevant links
# 4. Workers - N number of agents that will navigate to the link, check if the link is relevant to the query, and answer the question
# 5. Aggregator Agent - Aggregates the answers of the workers and answers the question

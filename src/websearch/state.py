from typing import Annotated, TypedDict
import operator

class GraphState(TypedDict):
    result_limit: int # How many links to generate
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
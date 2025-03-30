from typing import Annotated, TypedDict
from langchain_core.messages import AnyMessage
import operator
from pydantic import BaseModel, Field

FINISH = "FINISH"

class Link(BaseModel):
    url: str = Field(description="The url of the link")
    text: str | None = Field(default=None, description="Description of the link")

class Page(BaseModel):
    url: str = Field(description="The url of the page")
    summary: str = Field(description="A summary of the page in markdown format")

def assert_equality(x: str | None = None, y: str | None = None):
    if not x or not y:
        return x if x is not None else y
    if x != y:
        raise ValueError(f"x ({x}) is not equal to y ({y})")
    return x

class GraphState(TypedDict):
    generate_query_limit: int # How many queries to generate
    link_limit: int # How many links to generate
    messages: Annotated[list[AnyMessage], operator.add]
    user_query: Annotated[str, assert_equality]
    error: str | None
    queries: Annotated[list[str], operator.add]
    pages: Annotated[list[Page], operator.add]
    answer: str
    sources: list[str]

# Flow Example
#
# 1. Human Message - "What's the capital of France?"
# 2. Query Generator Agent - "Generates 3 queries"
# 3. Links Finder Agent - Based on the queries, find the most relevant links
# 4. Workers - N number of agents that will navigate to the link, check if the link is relevant to the query, and answer the question
# 5. Aggregator Agent - Aggregates the answers of the workers and answers the question
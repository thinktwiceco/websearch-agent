"""Web search tools for retrieving information from the internet.

This module provides functionality for performing web searches using the Brave Search API.
It includes utilities for executing searches and formatting the results into markdown.
The main entry point is the `websearch` function which is wrapped as a Tool.
"""

from pydantic_ai import Tool

from websearch.root_logger import root_logger
from websearch.tools.bravesearch.client import BraveSearchClient

logger = root_logger.getChild(__name__)


def mardownify(obj: dict) -> str:
    """Simple heuristic to convert a dict to a markdown string.

    First layer of keys are # headers.
    Second layer of keys are ## headers and so on.
    Lists are converted to bullet points.

    Args:
        obj: The dictionary to convert to markdown

    Returns:
        A formatted markdown string representation of the input dictionary
    """
    markdown = ""
    for key, value in obj.items():
        if isinstance(value, dict):
            markdown += f"## {key}\n"
            markdown += mardownify(value)
        elif isinstance(value, list):
            markdown += f"## {key}\n"
            for item in value:
                markdown += f"- {mardownify(item)}\n"
        else:
            markdown += f"{key}: {value}\n"
    return markdown


# Returns a list of links
def websearch(
    query: str,
    *,
    limit_results: int = 3,
) -> list[dict] | str:
    """Search the web for information about a specific query.

    Args:
        query: The query to search for
        limit_results: The number of results to return

    Returns:
        A markdown formatted response from the brave search client or an error message.
        The successful response contains information from various result types:
            - discussion: A list of discussion results
            - faq: A list of FAQ results
            - locations: A list of location results
            - mixed: A list of mixed results
            - news: A list of news results
            - videos: A list of video results
            - web: A list of web results with the links
    """
    client = BraveSearchClient()
    result = client.search(query, limit_results)

    if result["error"]:
        return result["error"]

    result = result["data"]
    result_str = mardownify(result)
    logger.info(f"Brave Search Result: {result_str}")
    return result_str


WebSearchTool = Tool(
    websearch,
    name="websearch",
    description="websearch tool. Returns a JSON response from the brave search client.",
    takes_ctx=False,
    max_retries=3,
)

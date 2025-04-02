import json
from pydantic_ai import Tool
from seleniumbase import SB, BaseCase
from websearch.root_logger import root_logger
from websearch.tools.bravesearch.client import BraveSearchClient


logger = root_logger.getChild(__name__)


# Returns a list of links
def google_search_links(
    query: str,
    *,
    in_website: str = None,
    limit_results: int = 5,
) -> list[dict] | str:
    """Search the web for information about a specific query

    Parameters
    ----------
        query: The query to search for
        in_website: The website to search in (optional)
        limit_results: The number of results to return (optional)

    Returns
    -------
        A list of dictionaries containing the search results
        Each dictionary contains the following keys:
            - url: The url of the search result
            - text: The text of the search result
        or a string error message
    """
    client = BraveSearchClient()
    result = client.search(query, limit_results)

    if result["error"]:
        return result["error"]

    data = result["data"]
    results = []
    for result in (data or []):
        text = f"{result.title}\n{result.description}"
        results.append({
            "url": result.url,
            "text": text,
        })

    return results

GoogleSearchLinksTool = Tool(
    google_search_links,
    name="google_search_links",
    description="google_search_links tool. Returns a list of links with metadata given a query",
    takes_ctx=False,
    max_retries=3,
)


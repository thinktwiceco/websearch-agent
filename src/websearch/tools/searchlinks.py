import json
from pydantic_ai import Tool
from seleniumbase import SB, BaseCase
from websearch.root_logger import root_logger


logger = root_logger.getChild(__name__)


# Returns a list of links
def google_search_links(
    query: str,
    *,
    in_website: str = None,
    limit_results: int = 5,
) -> list[dict]:
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
    """
    with SB(uc=True, headless=True, browser="chrome") as driver:
        driver: BaseCase
        try:
            logger.info(f"Searching the web for {query}")
            driver.open(f"https://www.google.com/search?q={query}")
            soup = driver.get_beautiful_soup()
            a_tags_with_h3 = soup.select('a > h3')
            a_tags = [tag.parent for tag in a_tags_with_h3]
            logger.info(f"Found {len(a_tags)} results")
            if not a_tags:
                return []

            # Get all the results
            results = [] # result is a list of the href link of the a tag and the h3 text
            for a_tag, h3_tag in zip(a_tags, a_tags_with_h3):
                if len(results) >= limit_results:
                    break
                result = {
                    "url": a_tag["href"],
                    "text": h3_tag.text,
                }
                results.append(result)
            return json.dumps(results)
        except Exception as e:
            return f"Error searching the web: {str(e)}"

GoogleSearchLinksTool = Tool(
    google_search_links,
    name="google_search_links",
    description="google_search_links tool. Returns a list of links with metadata given a query",
    takes_ctx=False,
    max_retries=3,
)


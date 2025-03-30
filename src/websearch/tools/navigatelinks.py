import json
from pydantic_ai import Tool
from seleniumbase import SB, BaseCase
from websearch.root_logger import root_logger

logger = root_logger.getChild(__name__)



def navigate_link(url: str) -> dict | None:
    """Navigate the link and return the text of the page

    Args:
        url: The url of the link to navigate

    Returns:
        A dictionary containing the text of the page
        The dictionary contains the following keys:
            - url: The url of the page
            - text: The text of the page
    """

    with SB(uc=True, headless=True) as driver:
        driver: BaseCase

        # @cache.memoize(expire=60 * 60 * 24 * 30)
        def async_explore_link(_href: str) -> dict:
            logger.info(f"🚀 Exploring {_href}")
            driver.open(_href)
            soup = driver.get_beautiful_soup()
            text = ""

            # Extract text from relevant content elements
            content_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'span', 'div']

            # Try to focus on main content areas first
            main_content = soup.find_all(['article', 'main', 'div', 'section'],
                                      class_=lambda c: c and any(x in str(c).lower() for x in
                                                             ['content', 'article', 'post', 'main', 'body']))

            if main_content:
                # Extract from identified main content areas
                for section in main_content:
                    for tag in content_tags:
                        for element in section.find_all(tag):
                            if element.get_text().strip():
                                text += "\n" + element.get_text().strip()
            else:
                # Fallback to extracting from the whole page
                for tag in content_tags:
                    for element in soup.find_all(tag):
                        if element.get_text().strip():
                            text += "\n" + element.get_text().strip()
            # Remove excessive whitespace and normalize
            import re
            text = re.sub(r'\n+', '\n', text).strip()

            logger.info(f"💠 Text extracted: {len(text)} characters")
            return ({
                "url": _href,
                "text": text,
            })
        try:
            return async_explore_link(url)
        except Exception as e:
            logger.error(f"Error navigating to {url}: {e}")
            return None


NavigateLinksTool = Tool(
    navigate_link,
    name="navigate_link",
    description="Navigate to the link and return the text of the page",
    takes_ctx=False,
    max_retries=3,
)
import json
from time import sleep
from bs4 import BeautifulSoup
from pydantic_ai import Tool
from seleniumbase import SB, BaseCase
from websearch.root_logger import root_logger
from playwright.async_api import async_playwright
import re

logger = root_logger.getChild(__name__)

# block pages by resource type. e.g. image, stylesheet
BLOCK_RESOURCE_TYPES = [
  'beacon',
  'csp_report',
  'font',
  'image',
  'imageset',
  'media',
  'object',
  'texttrack',
#  we can even block stylsheets and scripts though it's not recommended:
  'stylesheet',
# 'script',  
# 'xhr',
]


# we can also block popular 3rd party resources like tracking:
BLOCK_RESOURCE_NAMES = [
  'adzerk',
  'analytics',
  'cdn.api.twitter',
  'doubleclick',
  'exelator',
  'facebook',
  'fontawesome',
  'google',
  'google-analytics',
  'googletagmanager',
]
MAIN_CONTENT_TAGS = ['article', 'main', 'div', 'section']
CONTENT_TAGS = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'span', 'div']



async def intercept_route(route) -> None:
    if route.request.resource_type in BLOCK_RESOURCE_TYPES:
        logger.info(f"🚫 Blocking {route.request.resource_type} resource: {route.request.url}")
        await route.abort()
    elif any(name in route.request.url for name in BLOCK_RESOURCE_NAMES):
        logger.info(f"🚫 Blocking {route.request.url} resource: {route.request.url}")
        await route.abort()
    else:
        await route.continue_()

async def navigate_link(url: str) -> dict | None:
    """Navigate the link and return the text of the page

    Args:
        url: The url of the link to navigate

    Returns:
        A dictionary containing the text of the page
        The dictionary contains the following keys:
            - url: The url of the page
            - text: The text of the page
    """


    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        try:
            page = await browser.new_page()
            await page.route("**/*", intercept_route)
            # @cache.memoize(expire=60 * 60 * 24 * 30)

            logger.info(f"🚀 Exploring {url}")
            await page.goto(url)
            await page.wait_for_timeout(2000)
            logger.info(f"Page title: {await page.title()}")
            content = await page.content()
            soup = BeautifulSoup(content, "html.parser")
            text = ""
            # Extract text from relevant content elements

            # Try to focus on main content areas first
            main_content = soup.find_all(MAIN_CONTENT_TAGS,
                                        class_=lambda c: c and any(x in str(c).lower() for x in
                                                                MAIN_CONTENT_TAGS))

            if main_content:
                # Extract from identified main content areas
                for section in main_content:
                    for tag in CONTENT_TAGS:
                        for element in section.find_all(tag):
                            if element.get_text().strip():
                                text += "\n" + element.get_text().strip()
            else:
                # Fallback to extracting from the whole page
                for tag in CONTENT_TAGS:
                    for element in soup.find_all(tag):
                            if element.get_text().strip():
                                text += "\n" + element.get_text().strip()
            # Remove excessive whitespace and normalize
            text = re.sub(r'\n+', '\n', text).strip()
            text = remove_repeated_substrings(text)
            print("--- TEXT ---")
            print(text)
            print("--- END TEXT ---")
            logger.info(f"💠 Text extracted: {len(text)} characters")
            return ({
                "url": url,
                "text": text,
            })
        except Exception as e:
            logger.error(f"Error navigating to {url}: {e}")
            return None
        finally:
            await browser.close()


def remove_repeated_substrings(text: str, min_length: int = 6, min_occurrences: int = 3) -> str:
    """
    Remove substrings that are longer than min_length and appear sequentially
    more than min_occurrences times (possibly separated by whitespace).
    
    Args:
        text: The input text to process
        min_length: Minimum length of substring to consider (default: 6)
        min_occurrences: Minimum number of sequential occurrences required for removal (default: 3)
        
    Returns:
        The processed text with sequentially repeated substrings removed
    """
    if not text or len(text) < min_length * min_occurrences:
        return text
    
    # Split the text into words
    words = text.split()
    result_words = []
    i = 0
    
    while i < len(words):
        # Check if this word is long enough
        if len(words[i]) <= min_length:
            result_words.append(words[i])
            i += 1
            continue
            
        # Look ahead to see if we have repeated occurrences
        current_word = words[i]
        repeat_count = 1
        j = i + 1
        
        while j < len(words) and words[j] == current_word:
            repeat_count += 1
            j += 1
            
        # If we found enough repetitions, skip them all
        if repeat_count >= min_occurrences:
            i = j  # Skip all repetitions
        else:
            # Otherwise, keep the current word
            result_words.append(current_word)
            i += 1
    
    return ' '.join(result_words)


NavigateLinksTool = Tool(
    navigate_link,
    name="navigate_link",
    description="Navigate to the link and return the text of the page",
    takes_ctx=False,
    max_retries=3,
)
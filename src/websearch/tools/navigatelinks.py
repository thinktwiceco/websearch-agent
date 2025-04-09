"""Web navigation and content extraction tools.

This module provides utilities for web browsing with Playwright, content extraction,
and text cleaning. It intercepts and filters network requests to block unnecessary
resources, navigates to URLs, extracts relevant text content, and cleans the text
by removing repetitive content.
"""

import re

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from pydantic_ai import Tool

from websearch.root_logger import root_logger

logger = root_logger.getChild(__name__)

# block pages by resource type. e.g. image, stylesheet
BLOCK_RESOURCE_TYPES = [
    "beacon",
    "csp_report",
    "font",
    "image",
    "imageset",
    "media",
    "object",
    "texttrack",
    #  we can even block stylsheets and scripts though it's not recommended:
    "stylesheet",
    # 'script',
    # 'xhr',
]
"""List of resource types to block during web navigation to improve performance and reduce bandwidth."""


# we can also block popular 3rd party resources like tracking:
BLOCK_RESOURCE_NAMES = [
    "adzerk",
    "analytics",
    "cdn.api.twitter",
    "doubleclick",
    "exelator",
    "facebook",
    "fontawesome",
    "google",
    "google-analytics",
    "googletagmanager",
]
"""List of domain/resource names to block during web navigation, primarily targeting trackers and analytics."""

MAIN_CONTENT_TAGS = ["article", "main", "div", "section"]
"""HTML tags that typically contain the main content of a webpage."""

CONTENT_TAGS = ["p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "span", "div"]
"""HTML tags that contain meaningful text content to be extracted."""


async def intercept_route(route) -> None:
    """Intercept and filter network requests based on resource types and domains.

    Args:
        route: The route object representing the intercepted network request.
    """
    if route.request.resource_type in BLOCK_RESOURCE_TYPES:
        logger.info(
            f"🚫 Blocking {route.request.resource_type} resource: {route.request.url}"
        )
        await route.abort()
    elif any(name in route.request.url for name in BLOCK_RESOURCE_NAMES):
        logger.info(f"🚫 Blocking {route.request.url} resource: {route.request.url}")
        await route.abort()
    else:
        await route.continue_()


async def navigate_link(url: str) -> dict | None:
    """Navigate the link and return the text of the page.

    Args:
        url: The url of the link to navigate.

    Returns:
        dict: A dictionary containing the text of the page with keys:
            - url: The url of the page
            - text: The text of the page
        None: If navigation fails.
    """
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        try:
            page = await browser.new_page()
            await page.route("**/*", intercept_route)
            # @cache.memoize(expire=60 * 60 * 24 * 30)

            logger.info(f"🚀 Exploring {url}")
            await page.goto(url, wait_until="domcontentloaded", timeout=40000)
            await page.wait_for_timeout(2000)
            logger.info(f"Page title: {await page.title()}")
            content = await page.content()
            soup = BeautifulSoup(content, "html.parser")
            text = ""
            # Extract text from relevant content elements

            # Try to focus on main content areas first
            main_content = soup.find_all(
                MAIN_CONTENT_TAGS,
                class_=lambda c: c
                and any(x in str(c).lower() for x in MAIN_CONTENT_TAGS),
            )

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
            text = re.sub(r"\n+", "\n", text).strip()
            text = clean_text(text)
            print("--- TEXT ---")
            print(text)
            print("--- END TEXT ---")
            logger.info(f"💠 Text extracted: {len(text)} characters")
            return {
                "url": url,
                "text": text,
            }
        except Exception as e:
            logger.error(f"Error navigating to {url}: {e}")
            return None
        finally:
            await browser.close()


def clean_text(
    text: str, *, min_length_segment: int = 20, min_occurrences_segment: int = 2
) -> str:
    """Remove repeated text segments (phrases, paragraphs, etc.) that occur multiple times.

    This implementation detects:
    1. Repeated sentences and paragraphs
    2. Repeated question blocks and sections
    3. Sequences of similar content that appears multiple times

    Args:
        text: The input text to process.
        min_length_segment: Minimum length of text segment to consider for removal. Default is 20.
        min_occurrences_segment: Minimum number of occurrences required for removal. Default is 2.

    Returns:
        str: The processed text with repeated content removed.
    """
    if not text or len(text) < min_length_segment * min_occurrences_segment:
        return text

    # Remove all the extra whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove all the extra newlines
    text = re.sub(r"\n+", "\n", text)

    # Remove all the extra tabs
    text = re.sub(r"\t+", "\t", text)

    # Remove all the extra spaces
    text = re.sub(r"\s+", " ", text)

    # Remove all the extra dashes
    text = re.sub(r"-{2,}", "-", text)

    # Remove all the extra underscores
    text = re.sub(r"_{2,}", "_", text)

    # Remove all the extra asterisks, question marks, and exclamation points
    text = re.sub(r"\*{2,}", "*", text)
    text = re.sub(r"\?{2,}", "?", text)
    text = re.sub(r"!{2,}", "!", text)

    # Remove all the extra quotes
    text = re.sub(r'"{2,}', '"', text)
    text = re.sub(r"'{2,}", "'", text)

    # Remove all the extra commas
    text = re.sub(r",{2,}", ",", text)

    # Remove all the extra periods
    text = re.sub(r"\.{2,}", ".", text)

    # Split text into sentences or logical segments
    segments = re.split(r"(?<=[.!?])\s+", text)

    # Dictionary to count occurrences of each segment
    segment_counts = {}
    for segment in segments:
        if len(segment) >= min_length_segment:
            segment_counts[segment] = segment_counts.get(segment, 0) + 1

    # Build result, keeping only the first occurrence of repeated segments
    seen_segments = set()
    result = []
    for segment in segments:
        if (
            len(segment) < min_length_segment
            or segment_counts[segment] < min_occurrences_segment
            or segment not in seen_segments
        ):
            result.append(segment)
            seen_segments.add(segment)

    # Handle larger repeating blocks that might span multiple segments
    result_text = " ".join(result)

    # Look for repeating blocks (paragraphs or groups of questions)
    for block_size in range(100, min_length_segment, -20):  # Try different block sizes
        i = 0
        while i <= len(result_text) - block_size:
            block = result_text[i : i + block_size]
            if len(block) >= min_length_segment:
                # Count occurrences of this block in the remaining text
                remaining_text = result_text[i + block_size :]
                count = remaining_text.count(block)

                if (
                    count >= min_occurrences_segment - 1
                ):  # -1 because we already have one occurrence
                    # Remove all but the first occurrence
                    result_text = result_text[
                        : i + block_size
                    ] + remaining_text.replace(block, "", count)
                    continue  # Stay at the same position to check for more repetitions
            i += 1

    return result_text


NavigateLinksTool = Tool(
    navigate_link,
    name="navigate_link",
    description="Navigate to the link and return the text of the page",
    takes_ctx=False,
    max_retries=3,
)

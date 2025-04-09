"""Brave Search API client for performing web searches.

This module provides a client and data models for interacting with the Brave Search API.
It handles authentication, request formation, and response parsing for web search queries.
The client requires a Brave Search API key to be set in the environment variables.

Typical usage:
    client = BraveSearchClient()
    results = client.search("your search query")
"""

import os
from typing import TypedDict

import requests
from pydantic import BaseModel

from websearch import iocache
from websearch.root_logger import root_logger

logger = root_logger.getChild(__name__)

EXCLUDED_WEBSITES = {"site:internationalfinance.com", "site:deloitte.com"}


class LocationResult(BaseModel):
    """Represents a location result from Brave Search.

    Attributes:
        id: Unique identifier for the location.
        provider_url: URL of the provider.
        coordinates: List of coordinates [latitude, longitude].
        zoom_level: Zoom level for maps.
    """

    id: str
    provider_url: str
    coordinates: list[float]
    zoom_level: int

    model_config = {"extra": "allow"}


class Locations(BaseModel):
    """Container for location results from Brave Search.

    Attributes:
        results: List of location results.
    """

    results: list[LocationResult]


class ForumData(BaseModel):
    """Represents forum data from Brave Search.

    Attributes:
        forum_name: Name of the forum.
        num_answers: Number of answers in the forum thread.
        score: Score or rating of the forum post.
        title: Title of the forum post.
        question: The question asked in the forum.
        top_comment: The top comment or answer from the forum.
    """

    forum_name: str
    num_answers: int
    score: int
    title: str
    question: str
    top_comment: str


class QA(BaseModel):
    """Represents a question and answer pair from Brave Search.

    Attributes:
        question: The question text.
        answer: The answer text.
        title: Title of the QA result.
        url: URL to the full QA page.
    """

    question: str
    answer: str
    title: str
    url: str


class DiscussionResult(BaseModel):
    """Represents a discussion result from Brave Search.

    Attributes:
        data: Forum data for the discussion.
    """

    data: ForumData


class Discussion(BaseModel):
    """Container for discussion results from Brave Search.

    Attributes:
        results: List of discussion results.
    """

    results: list[DiscussionResult]


class Faq(BaseModel):
    """Container for FAQ results from Brave Search.

    Attributes:
        results: List of QA entries.
    """

    results: list[QA]


class BraveSearchResponse(BaseModel):
    """Represents the complete response from a Brave Search API call.

    Attributes:
        discussion: Optional discussion results.
        locations: Optional location results.
        news: Optional news results.
        videos: Optional video results.
        web: Web search results.
    """

    discussion: Discussion | None = None
    locations: Locations | None = None
    news: dict | None = None
    videos: dict | None = None
    web: dict

    model_config = {"extra": "ignore"}


class Result(TypedDict):
    """Result structure for Brave Search client.

    Attributes:
        error: Error details if request failed, None otherwise.
        data: Response data if request succeeded, None otherwise.
    """

    error: dict | None
    data: str | None


class BraveSearchClient:
    """Client for interacting with the Brave Search API.

    This client provides methods to search the web using Brave Search.
    It requires an API key from Brave.
    """

    def __init__(self):
        """Initialize the BraveSearchClient with API credentials."""
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
        self.api_key = os.getenv("BRAVE_SEARCH_API_KEY")

    @iocache.cache.memoize(expire=60 * 60 * 24)
    def search(self, query: str, count: int = 10) -> Result:
        """Perform a web search using the Brave Search API.

        Args:
            query: The search query string.
            count: The number of results to return. Default is 10.

        Returns:
            Result: A dictionary containing either:
                - 'data': The search results if successful.
                - 'error': Error information if the request failed.
        """
        headers = {
            "X-Subscription-Token": self.api_key,
        }

        # query += " NOT " + " OR ".join(EXCLUDED_WEBSITES)
        logger.info(f"Brave Search Query: {query}")
        params = {
            "q": query,
            "count": count,
        }

        try:
            response = requests.get(self.base_url, headers=headers, params=params)
            response.raise_for_status()
            obj = BraveSearchResponse.model_validate(response.json())
            return {"data": obj.model_dump(), "error": None}
        except requests.exceptions.RequestException as e:
            return {"data": None, "error": str(e)}

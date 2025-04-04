import json
import os
from pydantic import BaseModel
import requests
from typing import TypedDict
from websearch import iocache
from websearch.root_logger import root_logger

logger = root_logger.getChild(__name__)

EXCLUDED_WEBSITES = {
    "site:internationalfinance.com",
    "site:deloitte.com"
}


class LocationResult(BaseModel):
    id: str
    provider_url: str
    coordinates: list[float]
    zoom_level: int

    model_config = {
        "extra": "allow"
    }

class Locations(BaseModel):
    results: list[LocationResult]



class ForumData(BaseModel):
    forum_name: str
    num_answers: int
    score: int
    title: str
    question: str
    top_comment: str


class QA(BaseModel):
    question: str
    answer: str
    title: str
    url: str


class DiscussionResult(BaseModel):
    data: ForumData



class Discussion(BaseModel):
    results: list[DiscussionResult]

class Faq(BaseModel):
    results: list[QA]

class BraveSearchResponse(BaseModel):
    discussion: Discussion | None = None
    locations: Locations | None = None
    news: dict | None = None
    videos: dict | None = None
    web: dict

    model_config = {
        "extra": "ignore"
    }


class Result(TypedDict):
    error: dict | None
    data: str | None



class BraveSearchClient:
    def __init__(self):
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
        self.api_key = os.getenv("BRAVE_SEARCH_API_KEY")

    @iocache.cache.memoize(expire=60 * 60 * 24)
    def search(self, query: str, count: int = 10) -> Result:
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

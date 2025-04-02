import os
from pydantic import BaseModel
import requests
from typing import TypedDict, NotRequired

class BraveSearchWebResult(BaseModel):
    title: str
    url: str
    description: str

class Result(TypedDict):
    error: str | None
    data: list[BraveSearchWebResult] | None


class BraveSearchClient:
    def __init__(self):
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
        self.api_key = os.getenv("BRAVE_SEARCH_API_KEY")

    def search(self, query: str, count: int = 10) -> Result:
        headers = {
            "X-Subscription-Token": self.api_key,
        }
        params = {
            "q": query,
            "count": count,
        }


        try:
            response = requests.get(self.base_url, headers=headers, params=params)     
            response.raise_for_status()
            search_results = response.json()["web"]["results"]
            return {"data": [BraveSearchWebResult.model_validate(result) for result in search_results], "error": None}
        except requests.exceptions.RequestException as e:
            return {"data": None, "error": str(e)}

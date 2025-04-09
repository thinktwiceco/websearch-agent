"""Simple test for the websearch agent."""
import asyncio

from websearch import query

async def test_query():
    """Test the query agent."""
    async for result in query.exec(
        "What's the carbon footprint of a google pixel phone?",
        result_limit=3,
    ):
        print("======= AGENT =======")
        print(result)

if __name__ == "__main__":
    asyncio.run(test_query())

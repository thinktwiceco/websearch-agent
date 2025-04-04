import asyncio
from websearch import query
from websearch import config

config["chunk_size"] = 10000
config["chunk_overlap"] = 300

async def test_query():
    async for result in query.exec(
        "What can I do If I want to avoid to buy a smartphone? How can I invest the saved money?",
        result_limit=3,
    ):
        print("======= AGENT =======")
        print(result)

if __name__ == "__main__":
    asyncio.run(test_query())

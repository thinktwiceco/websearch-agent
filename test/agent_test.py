import asyncio
from websearch import query
from websearch import config

config["chunk_size"] = 10000
config["chunk_overlap"] = 300

async def test_query():
    async for result in query.exec(
        "What is a valid alternative to buy a smartphone?",
        generate_query_limit=1,
        link_limit=1,
    ):
        print("======= AGENT =======")
        print(result)

if __name__ == "__main__":
    asyncio.run(test_query())

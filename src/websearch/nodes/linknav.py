import operator
from typing import Annotated, Any, TypedDict
from websearch.state import Link
from websearch.root_logger import root_logger
from websearch.tools.navigatelinks import navigate_link
from langgraph.types import Send
from websearch import config
logger = root_logger.getChild(__name__)


class LinkNavState(TypedDict):
    link: Link
    user_query: str
    chunks: Annotated[list[str], operator.add]  # This is perfomed by the node, no agent involved

def break_text_into_chunks(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    chunks = []
    for i in range(0, len(text), chunk_size - chunk_overlap):
        chunks.append(text[i:i + chunk_size])
    return chunks

async def linknav(state: LinkNavState) -> Any:
    link_url = state['link'].url

    logger.info("Splitting text into chunks - Chunk size: "+str(config["chunk_size"])+" - Chunk overlap: "+str(config["chunk_overlap"]))

    # NO LLM involved here, just break the text into chunks
    # and return the chunks.
    # The router will take care of the LLM call
    logger.info(f" ➡️ Navigating to link: {link_url}")
    result = await navigate_link(link_url)

    if result is None:
        return {"error": "Failed to navigate link"}

    content = result['text']

    chunks = break_text_into_chunks(content, config["chunk_size"], config["chunk_overlap"])

    logger.info(f" ➡️ Total Chunks: {len(chunks)}")

    return {"chunks": chunks}


def assign_analyzers_to_chunks(state: LinkNavState):
    chunks = state['chunks']
    return [Send("chunkanalyzer", {"chunk": chunk, "user_query": state['user_query']}) for chunk in chunks]


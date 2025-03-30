import operator
from typing import Annotated, Any, Literal, TypedDict
from websearch.agents.linknav import linknavAgent
from websearch.prompts import UserPrompt
from websearch.state import Link, Page
from websearch.root_logger import root_logger
from websearch.tools.navigatelinks import navigate_link
from pydantic_ai.messages import ModelMessage, ModelRequest, ModelRequestPart, UserPromptPart, UserContent
from langgraph.types import Command, Send
from websearch import config
logger = root_logger.getChild(__name__)


class LinkNavState(TypedDict):
    link: Link
    user_query: str
    chunks: Annotated[list[str], operator.add]  # This is perfomed by the node, no agent involved
    chunk_analysis: Annotated[list[str], operator.add]  # Performed in parallel by chunkanalyzer
    pages: list[Page]

def break_text_into_chunks(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    chunks = []
    for i in range(0, len(text), chunk_size - chunk_overlap):
        chunks.append(text[i:i + chunk_size])
    return chunks

async def linknav(state: LinkNavState) -> Any:
    link_url = state['link'].url

    logger.info("Splitting text into chunks - Chunk size: "+str(config["chunk_size"])+" - Chunk overlap: "+str(config["chunk_overlap"]))

    if state.get("chunk_analysis"):
        # Chunk analysis is already done. We can have the LLM analyze the chunks
        # and generate a Page object if the chunks are relevant to the user query
        analysis = "\n".join(state['chunk_analysis'])
        user_prompt = UserPrompt(
            content=f"Summary of the webpage: {analysis}\n\nUser query: {state['user_query']}"
        )
        agent_response = await linknavAgent.run(user_prompt)

        if agent_response.data.error:
            return Command(
                goto="__end__",
                state={
                    "error": agent_response.data.error
                }
            )

        return Command(
            goto="syntetizer",
            state={
                "pages": [agent_response.data.page],
                "link": state['link'],
            }
        )
    else:
        # NO LLM involved here, just break the text into chunks
        # and return the chunks.
        # The router will take care of the LLM call
        logger.info(f" ➡️ Navigating to link: {link_url}")
        result = navigate_link(link_url)

        if result is None:
            return {"error": "Failed to navigate link"}

        content = result['text']

        chunks = break_text_into_chunks(content, config["chunk_size"], config["chunk_overlap"])

        logger.info(f" ➡️ Total Chunks: {len(chunks)}")

        return {"chunks": chunks}


def assign_analyzers_to_chunks(state: LinkNavState):
    chunks = state['chunks']
    return [Send("chunkanalyzer", {"chunk": chunk, "user_query": state['user_query']}) for chunk in chunks]


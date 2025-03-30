import operator
from typing import Annotated, Any, TypedDict
from websearch.prompts import UserPrompt
from websearch.root_logger import root_logger
from langgraph.types import Command
from websearch.agents.chunkanalyzer import chunkanalyzerAgent
logger = root_logger.getChild(__name__)

class ChunkAnalyzerState(TypedDict):
    user_query: str
    chunk: str # The single chunk to analyze
    chunk_analysis: Annotated[list[str], operator.add]  # Performed in parallel by chunkanalyzer



async def chunkanalyzer(state: ChunkAnalyzerState) -> Any:
    chunk = state['chunk']

    prompt = UserPrompt(
        query=f"User query: {state['user_query']}\n\nChunk: {chunk}",
        steps=[
            "Read the user query",
            "Read the chunk",
            "Analyze the chunk to see if it is relevant to the user query",
            "Summarize the information that are relevant to the user query",
        ]
    )

    agent_response = await chunkanalyzerAgent.run(prompt.text())

    if agent_response.data.error:
        return Command(
            goto="__end__",
            update={
                "error": agent_response.data.error
            }
        )

    return Command(
        goto="linknav",
        update={
            "chunk_analysis": [agent_response.data.chunk_analysis]
        }
    )

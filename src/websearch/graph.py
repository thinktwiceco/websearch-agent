from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, END

from websearch.nodes import chunkanalyzer, linksfinder, linksfinder_router, query_gen_router, querygen, linknav, assign_analyzers_to_chunks, syntetizer
from websearch.state import GraphState

memory = MemorySaver()

builder = StateGraph(GraphState)

builder.add_node("querygen", querygen)
builder.add_node("linksfinder", linksfinder)
builder.add_node("linknav", linknav)
builder.add_node("chunkanalyzer", chunkanalyzer)
builder.add_node("syntetizer", syntetizer)

builder.add_edge(START, "querygen")

builder.add_conditional_edges("querygen", query_gen_router)
builder.add_conditional_edges("linksfinder", linksfinder_router)
builder.add_conditional_edges("linknav", assign_analyzers_to_chunks, ["chunkanalyzer"])
builder.add_edge("chunkanalyzer", "linknav")
builder.add_edge("linknav", "syntetizer")
builder.add_edge("syntetizer", END)

graph = builder.compile(checkpointer=memory)

"""Web search graph module.

This module provides a graph for web search operations. It defines the nodes and edges
for the web search graph and compiles it into a graph object.
"""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from websearch.nodes.explorer import explorer
from websearch.nodes.querygen import query_gen_router, querygen
from websearch.nodes.syntetizer import syntetizer
from websearch.state import GraphState

memory = MemorySaver()

builder = StateGraph(GraphState)

builder.add_node("querygen", querygen)
builder.add_node("explorer", explorer)
builder.add_node("syntetizer", syntetizer)

builder.add_edge(START, "querygen")
builder.add_conditional_edges("querygen", query_gen_router)
builder.add_edge("explorer", "syntetizer")
builder.add_edge("syntetizer", END)

graph = builder.compile(checkpointer=memory)

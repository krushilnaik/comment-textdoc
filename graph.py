from typing import TypedDict

from langchain_core.runnables import RunnablePassthrough as r
from langgraph.graph import END, StateGraph


class State(TypedDict):
    text: str


def agent(state: State):
    text = state["text"]

    print(f"{text=}")

    return state


# init
builder = StateGraph(State)

# nodes
builder.add_node(agent)

# edges
builder.add_edge("agent", END)

# entry point
builder.set_entry_point("agent")

# create runnable for graph
reviewer = {"text": r(input_type=str)} | builder.compile()


reviewer.invoke("test")

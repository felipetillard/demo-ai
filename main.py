from agents import State, fitness_node, dietitian_node, supervisor_node, fallback_node
from langchain_core.messages import HumanMessage,AIMessage
from langgraph.graph import StateGraph, START
from langgraph.checkpoint.memory import MemorySaver


memory = MemorySaver()




builder = StateGraph(State)
builder.add_edge(START, "supervisor")
builder.add_node("supervisor", supervisor_node)
builder.add_node("fitness", fitness_node)
builder.add_node("dietitian", dietitian_node)
builder.add_node("fallback", fallback_node)
graph = builder.compile()



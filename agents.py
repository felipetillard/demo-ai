from langchain_core.messages import HumanMessage,AIMessage
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, MessagesState,START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain.prompts import PromptTemplate
from typing import Annotated, Literal
from langchain_ollama import ChatOllama

from typing_extensions import TypedDict
from langgraph.types import Command


from tools import (fitness_data_tool, diet_tool)
import streamlit as st


# Configuration
llm = ChatOllama(model="qwen2.5:14b")


memory = MemorySaver()
members = ["fitness", "dietitian", "wellness"]
options = members + ["FINISH"]

fitness_agent_prompt = """You can only answer queries related to workout. """
dietitian_system_prompt = """You can only answer queries related to diet and meal plans."""
system_prompt = (
    "You are a supervisor tasked with managing a conversation between the"
    f" following workers: {members}. Given the following user request,"
    " respond with the worker to act next. Each worker will perform a"
    " task and respond with their results and status. When finished,"
    " respond with FINISH."


    "Guidelines:\n"
    "1. Always check the last message in the conversation to determine if the task has been completed.\n"
    "2. If you already have the final answer or outcome, return 'FINISH'.\n"
   
)

fitness_agent = create_react_agent(llm, tools = [fitness_data_tool], prompt = fitness_agent_prompt)


dietitian_agent = create_react_agent(llm, tools = [diet_tool], prompt = dietitian_system_prompt)




# class State(TypedDict):
#     messages: Annotated[list, add_messages]
#     next: str | None

class State(MessagesState):
    next: str


class Router(TypedDict):
    """Worker to route to next. If no workers needed, route to FINISH."""

    # next: Literal[*options]
    next: Literal[*options]




def fitness_node(state: State) -> Command[Literal["supervisor"]]:
    result = fitness_agent.invoke(state)
    return Command(
        update={
            "messages": [
                AIMessage(content=result["messages"][-1].content, name="fitness")
            ]
        },
        goto="supervisor",
    )




def dietitian_node(state: State) -> Command[Literal["supervisor"]]:
    result = dietitian_agent.invoke(state)
    return Command(
        update={
            "messages": [
                AIMessage(content=result["messages"][-1].content, name="dietitian")
            ]
        },
        goto="supervisor",
    )



def mental_health_node(state: State):
    prompt = PromptTemplate.from_template(
        """You are a supportive mental wellness coach.
        Your task is to:
        - Give a unique mental wellness tip or stress-reducing practice.
        - Make it simple, kind, and useful. Avoid repeating tips."""
    )

    chain = prompt | llm
    response = chain.invoke(state)
    return Command(
        update={
            "messages": [
                AIMessage(content=f"Here's your wellness tip: {response.content}", name="wellness")
            ]
        },
        goto="supervisor",
    )



def supervisor_node(state: State) -> Command[Literal[*members, "__end__"]]:
    messages = [
        {"role": "system", "content": system_prompt},
    ] + state["messages"]
    response = llm.with_structured_output(Router).invoke(messages)
    goto = response["next"]
    if goto == "FINISH":
        goto = END

    return Command(goto=goto, update={"next": goto})

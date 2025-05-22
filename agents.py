from langchain_core.messages import HumanMessage,AIMessage
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, MessagesState,START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain.prompts import PromptTemplate
from typing import Annotated, Literal
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from typing_extensions import TypedDict
from langgraph.types import Command
from tools import (fitness_data_tool, diet_tool, get_user_uploaded_meals, get_user_nutrition_plan, get_current_time, get_user_profile, get_user_wearable_data, get_user_workouts)


# Import prompts from prompts.py
from prompts import fitness_agent_prompt, dietitian_system_prompt, system_prompt, fallback_agent_prompt

# Configuration
load_dotenv()
llm = ChatOpenAI(model="gpt-4o")

memory = MemorySaver()
members = ["fitness", "dietitian", "fallback"]
options = members + ["FINISH"]




fitness_agent = create_react_agent(llm, tools = [fitness_data_tool, get_user_workouts, get_user_wearable_data], prompt = fitness_agent_prompt)


dietitian_agent = create_react_agent(
    llm,
    tools=[
        diet_tool,
        get_user_nutrition_plan,
        get_user_profile,
        get_current_time,
        get_user_uploaded_meals
    ],
    prompt=dietitian_system_prompt
)

# Prompt para el fallback agent
fallback_agent = create_react_agent(llm, tools=[get_user_profile, get_user_profile], prompt=fallback_agent_prompt)



class State(MessagesState):
    next: str
    userId: str = "c72fdfe7-142c-4cb1-a65a-770315f32782"
    steps: int = 0


class Router(TypedDict):
    """Worker to route to next. If no workers needed, route to FINISH. Use 'fallback' for greetings or unsupported topics."""
    next: Literal[*options]



def fitness_node(state: State) -> Command[Literal["supervisor"]]:
    state["steps"] = state.get("steps", 0) + 1
    result = fitness_agent.invoke(state)
    return Command(
        update={
            "messages": [
                AIMessage(content=result["messages"][-1].content, name="fitness")
            ]
        },
        goto=END,
    )


def dietitian_node(state: State) -> Command[Literal["supervisor"]]:
    state["steps"] = state.get("steps", 0) + 1
    result = dietitian_agent.invoke(state)
    return Command(
        update={
            "messages": [
                AIMessage(content=result["messages"][-1].content, name="dietitian")
            ],
            "done": True
        },
        goto=END,
    )

def fallback_node(state: State) -> Command[Literal["supervisor"]]:
    state["steps"] = state.get("steps", 0) + 1
    result = fallback_agent.invoke(state)
    return Command(
        update={
            "messages": [
                AIMessage(content=result["messages"][-1].content, name="fallback")
            ]
        },
        goto=END,
    )



def supervisor_node(state: State) -> Command[Literal[*members, "__end__"]]:
    state["steps"] = state.get("steps", 0) + 1

    messages = [
        {"role": "system", "content": system_prompt},
    ] + state["messages"]
    # El LLM está instruido para devolver siempre {"next": ...} según el Router,
    # usando "fallback" como valor por defecto si no está seguro o es un saludo o fuera de dominio.
    # Este fallback es una red de seguridad por si el LLM no sigue el esquema.
    response = llm.with_structured_output(Router).invoke(messages)
    goto = response.get("next", "fallback")  # fallback a fallback si no hay 'next'

    if goto not in options:
        return Command(
            update={
                "messages": [
                    AIMessage(content="Sorry, I don't know how to help with that 🙈", name="supervisor")
                ]
            },
            goto=END,
        )

    if goto == "FINISH":
        goto = END

    return Command(goto=goto, update={"next": goto})


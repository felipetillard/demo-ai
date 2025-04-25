from agents import State, fitness_node, dietitian_node, mental_health_node, supervisor_node
from langchain_core.messages import HumanMessage,AIMessage
from langgraph.graph import StateGraph, START
from langgraph.checkpoint.memory import MemorySaver
from langchain_ollama import ChatOllama
from utils import parse_langgraph_output

import streamlit as st
import logging
import time


# Configuration
llm = ChatOllama(model="qwen2.5:14b")


memory = MemorySaver()




builder = StateGraph(State)
builder.add_edge(START, "supervisor")
builder.add_node("supervisor", supervisor_node)
builder.add_node("fitness", fitness_node)
builder.add_node("dietitian", dietitian_node)
builder.add_node("wellness", mental_health_node)
graph = builder.compile(checkpointer=memory)


# Streamlit interface

st.title("AI Health Assistant")
logging.info("App started")



if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm your AI Health Assistant. Our team includes a **Fitness Coach**, "
                "**a Dietitian**, and a **Mental Wellness Guide**."
                "We are here to support your wellness journey 🌿.\n\n"
                "**How can we assist you today?**"}
    ]

# Display all previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Your question"):
  
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)

    # Generate and display assistant response
    with st.chat_message("assistant"):
        start_time = time.time()
        logging.info("Generating response...")
        with st.spinner("Processing..."):        
            inputs = {
                "messages": [
                    HumanMessage(
                        content=prompt
                    )
                ],
            }
            config = {"configurable": {"thread_id": "2", "recursion_limit": 15}}   
            # Get the final step in the stream
            final_event = None
            for step in graph.stream(inputs, config=config):
                final_event = step  # Keep updating to the latest step
                print(final_event)
            
                response_message=parse_langgraph_output(final_event)
          
                for agent, content in response_message:

                    assistant_reply = f"**Agent:** `{agent}`\n\n{content}"
                    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
                    st.markdown(assistant_reply)
                    st.markdown("---")
    

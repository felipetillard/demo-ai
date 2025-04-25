from langchain_core.messages import HumanMessage,AIMessage

def parse_langgraph_output(stream):
    results = []
    for key, value in stream.items():
        if key == "supervisor":
            continue
        messages = value.get("messages", [])
        for msg in messages:
            if isinstance(msg, str):
                results.append((key, msg))
            elif isinstance(msg, AIMessage):
                results.append((key, msg.content))
    return results
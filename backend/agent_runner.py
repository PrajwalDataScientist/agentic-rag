import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from langchain_core.messages import HumanMessage
from agent import graph

def run_agent(query: str) -> str:
    result = graph.invoke({
        "messages": [HumanMessage(content=query)]
    })
    return result["messages"][-1].content

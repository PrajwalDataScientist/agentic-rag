import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Annotated, Sequence, TypedDict

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq


load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=True)
key = os.getenv("GROQ_API_KEY")
if not key:
    raise ValueError("GROQ_API_KEY not found")


from tools.companydetails_tool import companydetails_tool
from tools.companypolicy_tool import companypolicy_tool
from tools.employees_tool import employees_tool

tools = [
    companydetails_tool,
    companypolicy_tool,
    employees_tool,
]

#helper 
def extract_docs(content):
    """
    Convert tool output into plain text context
    """
    if isinstance(content, str):
        return content
    return "\n".join(getattr(doc, "page_content", str(doc)) for doc in content)


class AgentState(TypedDict):
    messages: Annotated[Sequence[HumanMessage | AIMessage], add_messages]


def agent(state: AgentState):
    print("\n--- AGENT: THINKING & DECIDING ---")

    question = state["messages"][0].content

    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=key,
        temperature=0,
    ).bind_tools(tools)  

    response = llm.invoke([
        HumanMessage(
            content=f"""
You are an intelligent AI agent.

Decide whether the user question requires:
- company details
- company policy
- employee information

If required, call the correct tool.
If not, answer directly.

Rules:
- Do NOT use the internet
- Do NOT hallucinate
- If unsure, say you are not aware

User Question:
{question}
"""
        )
    ])

    return {"messages": [response]}


def generate(state: AgentState):
    print("\n--- GENERATE: FINAL ANSWER ---")

    question = state["messages"][0].content
    last_message = state["messages"][-1].content
    context = extract_docs(last_message)

    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=key,
        temperature=0,
    )

    if context.strip():
        prompt = PromptTemplate(
            template="""
Answer the question ONLY using the context below.
If the answer is not present, reply exactly:
"Sorry, I am not aware of this information."

Context:
{context}

Question:
{question}
""",
            input_variables=["context", "question"],
        )

        answer = (prompt | llm | StrOutputParser()).invoke({
            "context": context,
            "question": question,
        })
    else:
        prompt = PromptTemplate(
            template="""
Answer honestly using your general knowledge.
If unsure, reply exactly:
"Sorry, I am not aware of this information."

Question:
{question}
""",
            input_variables=["question"],
        )

        answer = (prompt | llm | StrOutputParser()).invoke({
            "question": question
        })

    return {"messages": [AIMessage(content=answer)]}


workflow = StateGraph(AgentState)

workflow.add_node("agent", agent)
workflow.add_node("retrieve", ToolNode(tools))
workflow.add_node("generate", generate)

workflow.add_edge(START, "agent")

workflow.add_conditional_edges(
    "agent",
    tools_condition,
    {
        "tools": "retrieve",
        "default": "generate",
    }
)

workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

graph = workflow.compile()


if __name__ == "__main__":
    result = graph.invoke({
        "messages": [
            HumanMessage(content="what is company policy?")
        ],
    })

    print("\n================ FINAL RESPONSE ================\n")
    print(result["messages"][-1].content)

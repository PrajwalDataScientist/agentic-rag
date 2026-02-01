from fastapi import FastAPI
from pydantic import BaseModel
from backend.agent_runner import run_agent

print("Backend starting...")

app = FastAPI(title="Agentic RAG API")

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str

@app.post("/query", response_model=QueryResponse)
def query_agent(request: QueryRequest):
    print(f" Received query: {request.question}")
    answer = run_agent(request.question)
    print("Answer generated")
    return {"answer": answer}

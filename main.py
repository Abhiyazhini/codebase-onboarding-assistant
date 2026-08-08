from fastapi import FastAPI
from pydantic import BaseModel
from indexer import index_repo
from rag_engine import ask_question

app = FastAPI(title="Codebase Onboarding Assistant")

class IndexRequest(BaseModel):
    github_url: str

class QueryRequest(BaseModel):
    question: str

@app.post("/ingest")
def ingest(req: IndexRequest):
    return index_repo(req.github_url)

@app.post("/query")
def query(req: QueryRequest):
    return ask_question(req.question)

@app.get("/health")
def health():
    return {"status": "ok"}
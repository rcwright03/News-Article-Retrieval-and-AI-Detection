from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List


app = FastAPI()

# Allow the React dev server to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Item(BaseModel):
    id: str
    title: str
    source: str
    url: str
    publishedAt: str
    bm25: float
    cosine: float
    aiScore: float
    snippet: str


class SearchResponse(BaseModel):
    items: List[Item]


@app.get("/api/search", response_model=SearchResponse)
async def search(
    q: str = Query(...),
    top_k: int = Query(10, alias="top_k"),
    rerank: bool = Query(True),
    model: str = Query("mpnet"),
):
    # Temporary demo data – you will replace this with real BM25 / rerank / AI detection later.
    text = f"Demo result for '{q}'"
    items = [
        Item(
            id="demo1",
            title=text,
            source="Mock backend",
            url="https://example.com/demo1",
            publishedAt="2025-10-27",
            bm25=7.0,
            cosine=0.82,
            aiScore=0.27,
            snippet="This snippet is returned from the FastAPI backend. Plug your real pipeline here.",
        )
    ]
    return SearchResponse(items=items)

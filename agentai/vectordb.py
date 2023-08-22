import uuid
from typing import List, Optional

import chromadb
from .parsers import Parser
from pydantic import BaseModel, Field

from agentai.annotations import ToolRegistry, tool


class Query(BaseModel):
    query_embedding: Optional[List[int]] = Field(..., description="Embedding for the query to search")
    query_text: Optional[str] = Field(..., description="Simplified query from the user to search")
    k: int = Field(..., description="The number of results requested")


class VectorDB(BaseModel):
    def __init__(self):
        self.client = None


class ChromaDB(VectorDB):
    def __init__(self):
        self.client = chromadb.Client()
        self.collection = self.client.create_collection(name="my_collection")

    def doc_loader(self, filename: str):
        parser = Parser()
        docs = parser.parse_pdf(filename)
        # Using chroma db as an example
        for doc in docs:
            self.collection.add(
                documents=doc.page_content,
                metadatas=doc.metadata,
                ids=str(uuid.uuid4()),
            )

    def get_docs(self, query: Query):
        results = self.collection.query(
            query_embeddings=[query.query_embedding], query_texts=[query.query_text], n_results=query.k
        )
        return results

    def get_count(self):
        return self.collection.count()

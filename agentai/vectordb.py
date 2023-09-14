import uuid
from typing import List, Optional, Union

import chromadb
from pydantic import BaseModel, Field
from typing_extensions import Literal

from agentai.parsers import Parser, UnstructuredPdfParser

Embedding = List[float]

Include = List[
    Union[
        Literal["documents"],
        Literal["embeddings"],
        Literal["metadatas"],
        Literal["distances"],
    ]
]


class Query(BaseModel):
    """Query Model to search the vector database. If query_embeddings is provided, query_texts will be ignored."""

    query_embeddings: Optional[List[Embedding]] = Field(None, description="Embedding for the query to search")
    query_texts: Optional[List[str]] = Field(None, description="Simplified query from the user to search")
    k: int = Field(..., description="The number of results requested")
    include: Include = Field(
        ["documents", "embeddings", "metadatas", "distances"], description="Data to include in results"
    )


class VectorDB:
    def __init__(self):
        self.client = None


class ChromaDB(VectorDB):
    def __init__(self):
        self.chroma_client = chromadb.Client()
        self.collection = self.chroma_client.create_collection(name="my_collection")

    def doc_loader(self, filename: str, parser: Parser = None):
        if parser is None:
            parser = UnstructuredPdfParser()
        docs = parser.parse_pdf(file=filename)
        # Using chroma db as an example
        for doc in docs:
            self.collection.add(
                documents=doc.page_content,
                metadatas=doc.metadata,
                ids=str(uuid.uuid4()),
            )

    def get_docs(self, query: Query):
        results = self.collection.query(
            query_texts=query.query_texts,
            n_results=query.k,
            include=query.include,
        )
        return results

    def get_count(self):
        return self.collection.count()

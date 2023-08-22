import pytest

from agentai.vectordb import ChromaDB, Query


@pytest.fixture
def chroma_db():
    return ChromaDB()


def test_doc_loader(chroma_db):
    filename = "layout-parser-paper.pdf"
    chroma_db.doc_loader(filename)
    assert chroma_db.get_count() > 0


def test_get_docs(chroma_db):
    query = Query(query_embedding=[1, 2, 3], query_text="test", k=1)
    results = chroma_db.get_docs(query)
    assert len(results) == 1

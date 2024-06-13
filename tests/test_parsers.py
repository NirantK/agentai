from typing import List

from langchain.docstore.document import Document
from agentai.parsers import Parser


def test_parse_pdf():
    # Parser instance
    parser = Parser()

    # parse the PDF file
    docs: List[Document] = parser.parse_pdf(filename="layout-parser-paper.pdf")

    # check that the output is a list of Document objects
    assert isinstance(docs, list)
    assert all(isinstance(doc, Document) for doc in docs)

    # check that the output contains the expected number of documents
    assert len(docs) >= 240

    # check that the metadata of the first document is correct
    assert docs[0].metadata["filename"] == "layout-parser-paper.pdf"
    assert docs[0].metadata["filetype"] == "application/pdf"
    assert docs[0].metadata["category"] == "Title"
    assert docs[0].metadata["page_number"] == 1

    # check if there is atleast one of "Table" category the metadata["category"]
    assert any(doc.metadata["category"] == "Table" for doc in docs)

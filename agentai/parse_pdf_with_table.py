from unstructured.partition.pdf import partition_pdf
from typing import List

from langchain.docstore.document import Document
import pandas as pd


def process_element(element):
    metadata = {}
    if hasattr(element, "metadata"):
        # metadata.update(element.metadata.to_dict())
        if hasattr(element.metadata, "page_number"):
            metadata["page_number"] = element.metadata.page_number

        # default metadata by unstructured
        metadata["filename"] = element.metadata.filename
        metadata["filetype"] = element.metadata.filetype

    if hasattr(element, "category"):
        metadata["category"] = element.category
        if element.category == "Table":
            # metadata["table"] = element.metadata.to_dict()
            table_uno_list = pd.read_html(element.metadata.text_as_html)
            for _, row in table_uno_list[0].iterrows():
                # go through each row of the table and create a document
                # with the row data dictionary as page content
                page_content = row.to_dict()
                docs.append(Document(page_content=str(page_content), metadata=metadata))
        else:
            # if element is not a table, then it is a text
            docs.append(Document(page_content=str(element), metadata=metadata))


filename = "layout-parser-paper.pdf"
elements = partition_pdf(filename=filename, infer_table_structure=True)
docs: List[Document] = list()

for element in elements:
    process_element(element)

print(docs)

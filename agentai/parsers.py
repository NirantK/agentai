from typing import List

import pandas as pd
from langchain.docstore.document import Document
from unstructured.partition.pdf import partition_pdf


class Parser:
    def __init__(self):
        self.filename = ""
        self.docs: List[Document] = list()

    def process_element(self, element):
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
                    self.docs.append(Document(page_content=str(page_content), metadata=metadata))
            else:
                # if element is not a table, then it is a text
                self.docs.append(Document(page_content=str(element), metadata=metadata))

    def parse_pdf(self, filename: str):
        self.filename = filename
        elements = partition_pdf(self.filename)
        for element in elements:
            self.process_element(element)
        return self.docs

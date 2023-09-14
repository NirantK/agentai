from typing import Any, Dict, List

import pandas as pd
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.tools.azure_cognitive_services.utils import detect_file_src_type
from unstructured.partition.pdf import partition_pdf
from typing import List, Optional


class Parser:
    def __init__(self):
        self.file = ""
        self.docs: List[Document] = list()


class UnstructuredPdfParser(Parser):
    def __init__(self):
        super().__init__()

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

    def parse_pdf(self, file: str):
        self.file = file
        elements = partition_pdf(self.file)
        for element in elements:
            self.process_element(element)
        return self.docs


class AzureDocumentIntelligencePdfParser(Parser):
    def __init__(self, endpoint: str = None, key: str = None):
        super().__init__()
        self.endpoint = endpoint
        self.key = key

    def parse_tables(self, tables: List[Any]) -> List[Document]:
        all_row_data = []

        # Goal: Rewrite the above table code using using pandas
        for table in tables:
            metadata = {}
            # metadata["filename"] = filename
            # metadata["filetype"] = filetype

            json_data = table.to_dict()
            # Extract column headers
            column_headers = []
            for cell in json_data["cells"]:
                if cell["kind"] == "columnHeader":
                    column_headers.append(cell["content"])

            # Initialize an empty DataFrame with column headers
            df = pd.DataFrame(columns=column_headers)

            # Fill in the DataFrame with cell content
            for row_index in range(json_data["row_count"]):
                row_data = []
                for col_index in range(json_data["column_count"]):
                    content = next(
                        cell["content"]
                        for cell in json_data["cells"]
                        if cell["row_index"] == row_index and cell["column_index"] == col_index
                    )
                    row_data.append(content)
                df.loc[row_index] = row_data

            # Drop the first row since it contains column headers repeating
            df = df.drop(df.index[0])

            for _, row in df.iterrows():
                # go through each row of the table and create a document
                # with the row data dictionary as page content
                metadata["category"] = "Table"
                metadata["page_number"] = json_data["bounding_regions"][0]["page_number"]
                page_content = row.to_dict()

                all_row_data.append(Document(page_content=str(page_content), metadata=metadata))

        return all_row_data

    def parse_kv_pairs(self, kv_pairs: List[Any]) -> List[Document]:
        result = []
        for kv_pair in kv_pairs:
            key = kv_pair.key.content if kv_pair.key else ""
            value = kv_pair.value.content if kv_pair.value else ""
            # result.append((key, value))
            page_content = {key: value}
            metadata = {}
            metadata["category"] = "Key Value Pair"
            result.append(Document(page_content=str(page_content), metadata=metadata))
        return result

    def format_document_analysis_result(self, doc_dictionary: Dict) -> List[Document]:
        formatted_result = []
        if "content" in doc_dictionary:
            # split the content into chunks of 300 characters with 30 character overlap
            splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=300, chunk_overlap=30)
            # metadatas is a list of dictionaries with key "category" and value "Text".
            # The length of metadatas is the same as the length of document_analysis_result["content"]
            metadatas = [{"category": "Text"}] * len(doc_dictionary["content"])

            splits = splitter.create_documents(texts=[doc_dictionary["content"]], metadatas=metadatas)
            formatted_result = splits
        if "tables" in doc_dictionary:
            formatted_result.extend(doc_dictionary["tables"])
        if "key_value_pairs" in doc_dictionary:
            formatted_result.extend(doc_dictionary["key_value_pairs"])

        print("formatted_result: ", formatted_result)
        return formatted_result

    def parse_pdf(self, file: str, pages: Optional[str] = None) -> List[Document]:
        document_analysis_client = DocumentAnalysisClient(endpoint=self.endpoint, credential=AzureKeyCredential(self.key))
        document_src_type = detect_file_src_type(file)
        if document_src_type == "local":
            with open(file, "rb") as document:
                poller = document_analysis_client.begin_analyze_document("prebuilt-layout", document, pages=pages)
        elif document_src_type == "remote":
            poller = document_analysis_client.begin_analyze_document_from_url("prebuilt-layout", file, pages=pages)
        else:
            raise ValueError(f"Invalid document path: {file}")

        result = poller.result()
        print("result from azure: ", result)

        res_dict = {}

        if result.content is not None:
            res_dict["content"] = result.content

        if result.tables is not None:
            print("result.tables: ", result.tables)
            res_dict["tables"] = self.parse_tables(result.tables)

        if result.key_value_pairs is not None:
            res_dict["key_value_pairs"] = self.parse_kv_pairs(result.key_value_pairs)

        return self.format_document_analysis_result(res_dict)

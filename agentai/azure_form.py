# import libraries
import os
from typing import Any, Dict, List

import numpy as np
import pandas as pd
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.tools.azure_cognitive_services.utils import detect_file_src_type

# set `<your-endpoint>` and `<your-key>` variables with the values from the Azure portal
endpoint = "<your-endpoint>"
key = "<your-key>"


def parse_tables(tables: List[Any]) -> List[Document]:
    all_row_data = []

    # Goal: Rewrite the above table code using using pandas
    for table_idx, table in enumerate(tables):
        # l = list()
        # row_count = table.row_count
        # column_count = table.column_count
        # for cell in table.cells:
        #     l.append(cell.content)
        # # Create a dataframe from the numpy array
        # df = pd.DataFrame(np.array(l).reshape(row_count, column_count))
        # df.columns = df.iloc[0]
        # df = df.drop(df.index[0])
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


def parse_kv_pairs(kv_pairs: List[Any]) -> List[Document]:
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


def format_document_analysis_result(document_analysis_result: Dict) -> List[Document]:
    formatted_result = []
    if "content" in document_analysis_result:
        # split the content into chunks of 300 characters with 30 character overlap
        splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=300, chunk_overlap=30)
        # metadatas is a list of dictionaries with key "category" and value "Text".
        # The length of metadatas is the same as the length of document_analysis_result["content"]
        metadatas = [{"category": "Text"}] * len(document_analysis_result["content"])

        splits = splitter.create_documents(texts=[document_analysis_result["content"]], metadatas=metadatas)
        formatted_result.append(splits)
    if "tables" in document_analysis_result:
        formatted_result.extend(document_analysis_result["tables"])
    if "key_value_pairs" in document_analysis_result:
        formatted_result.extend(document_analysis_result["key_value_pairs"])

    return formatted_result


def analyze_layout(document_path: str, pages: str = None):
    document_analysis_client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    document_src_type = detect_file_src_type(document_path)
    if document_src_type == "local":
        with open(document_path, "rb") as document:
            poller = document_analysis_client.begin_analyze_document("prebuilt-layout", document, pages=pages)
    elif document_src_type == "remote":
        poller = document_analysis_client.begin_analyze_document_from_url("prebuilt-layout", document_path, pages=pages)
    else:
        raise ValueError(f"Invalid document path: {document_path}")

    result = poller.result()

    res_dict = {}

    if result.content is not None:
        res_dict["content"] = result.content

    if result.tables is not None:
        res_dict["tables"] = parse_tables(result.tables)

    if result.key_value_pairs is not None:
        res_dict["key_value_pairs"] = parse_kv_pairs(result.key_value_pairs)

    return res_dict


if __name__ == "__main__":
    # sample document
    # document_path = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/sample-layout.pdf"
    document_path = "hesc101.pdf"
    document_analysis_result = analyze_layout(document_path=document_path, pages=None)  # pages="1-2, 5-6"
    formatted_doc = format_document_analysis_result(document_analysis_result)
    print(formatted_doc)

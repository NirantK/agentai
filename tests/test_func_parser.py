import json
from typing import List, Dict, Optional
from agentai.function_parser import get_function_info

paper_dir_filepath = "examples/paper_dir"


def get_articles(query: str, library: str = paper_dir_filepath, top_k: Optional[int] = 5) -> List[Dict[str, str]]:
    """
    This function gets the top_k articles based on a user's query, sorted by relevance.
    It also downloads the files and stores them in arxiv_library.csv to be retrieved by the read_article_and_summarize.

    Args:
        query (str): User query in JSON. Responses should be summarized and should include the article URL reference
        library (str, optional): filepath. Defaults to paper_dir_filepath.
        top_k (int, optional): Number of papers. Defaults to 5.

    Returns:
        List[Dict[str, str]]: _description_
    """
    result_list = []
    return result_list


def test_get_function_info():
    """Test get_function_info"""
    print(json.dumps(get_function_info(get_articles), indent=4))
    assert get_function_info(get_articles) == {
        "name": "get_articles",
        "description": "This function gets the top_k articles based on a user's query, sorted by relevance.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "User query in JSON. Responses should be summarized and should include the article URL reference",
                },
                "library": {
                    "type": "string",
                    "description": "filepath. Defaults to paper_dir_filepath.",
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of papers. Defaults to 5.",
                },
            },
        },
        "required": ["query"],
    }


test_get_function_info()

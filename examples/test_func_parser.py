from typing import List, Dict, Optional
from agentai.function_parser import get_function_info


def get_articles(query: str, library: Optional[str], top_k: Optional[int] = 5) -> List[Dict[str, str]]:
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
    assert get_function_info(get_articles) == {
        "name": "get_articles",
        "description": "This function gets the top_k articles based on a user's query, sorted by relevance.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "str",
                    "description": "User query in JSON. Responses should be summarized and should include the article URL reference",
                },
                "library": {"type": "Optional[str]", "description": "filepath. Defaults to paper_dir_filepath."},
                "top_k": {"type": "Optional[int]", "description": "Number of papers. Defaults to 5.", "default": "5"},
            },
        },
        "required": ["query"],
    }
    print(get_function_info(get_articles))

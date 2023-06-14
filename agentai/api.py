"""
API functions for the agentai package
"""
import openai
import requests
from tenacity import retry, stop_after_attempt, wait_random_exponential


@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, model, functions=None, debug=False):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + openai.api_key,
    }
    if debug:
        print("Generating ChatCompletion response")
        print(f"messages: {messages}")
    if not len(messages) > 0:
        raise ValueError("messages must be a list of strings")
    json_data = {"model": model, "messages": messages}
    if functions is not None:
        json_data.update({"functions": functions})
        if debug:
            print(f"functions: {functions}")

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=json_data,
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e

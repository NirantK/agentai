"""
API functions for the agentai package
"""
import openai
import requests
from tenacity import retry, stop_after_attempt, wait_random_exponential
from .openai_function import FunctionRegistry


@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
def chat_complete(messages, model, function_registry: FunctionRegistry = None, debug: bool = False):
    if openai.api_key is None:
        raise ValueError("Please set openai.api_key and try again")
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
    if function_registry is not None:
        functions = function_registry.get_all_functions()
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


def get_function_arguments(message, conversation, functions, model):
    function_arguments = {}
    if message["finish_reason"] == "function_call":
        arguments = message["message"]["function_call"]["arguments"]
        try:
            function_arguments = eval(arguments)
        except SyntaxError:
            print("Syntax error, trying again")
            response = chat_complete(conversation.conversation_history, functions=functions, model=model)
            message = response.json()["choices"][0]
            function_arguments = get_function_arguments(message, conversation, functions, model)
    else:
        print("Function not required, responding to user")
    return function_arguments


def chat_complete_execute_fn(conversation, functions, model, callable_function):
    response = chat_complete(conversation.conversation_history, functions=functions, model=model)
    message = response.json()["choices"][0]
    function_arguments = get_function_arguments(
        message=message, conversation=conversation, functions=functions, model=model
    )
    results = callable_function(**function_arguments)
    conversation.add_message(role="function", name=callable_function.__name__, content=str(results))
    response = chat_complete(conversation.conversation_history, functions=functions, model=model)
    assistant_message = response.json()["choices"][0]["message"]["content"]
    conversation.add_message(role="assistant", content=assistant_message)
    return assistant_message

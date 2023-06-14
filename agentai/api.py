"""
API functions for the agentai package
"""
from typing import Callable

import openai
import requests
from tenacity import (
    retry,
    retry_if_exception,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)

from .conversation import Conversation
from .openai_function import ToolRegistry


@retry(retry=retry_if_exception_type(ValueError), stop=stop_after_attempt(3))
def chat_complete(
    messages, model, function_registry: ToolRegistry = None, debug: bool = False, return_function: bool = False
):
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
        functions = function_registry.get_all_function_information()
        json_data.update({"functions": functions})
        if debug:
            print(f"functions: {functions}")

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=json_data,
    )
    if return_function:
        if response.json()["choices"][0]["message"]["content"] is not None:
            raise ValueError(f"OpenAI API returned unexpected output: {response.json()}")
        return response
    else:
        content = response.json()["choices"][0]["message"]["content"]
        if content is None:
            raise ValueError(f"OpenAI API returned unexpected output: {response.json()}")
        return response


def get_function_arguments(message, conversation: Conversation, function_registry: ToolRegistry, model: str):
    function_arguments = {}
    if message["finish_reason"] == "function_call":
        arguments = message["message"]["function_call"]["arguments"]
        try:
            function_arguments = eval(arguments)
        except SyntaxError:
            print("Syntax error, trying again")
            response = chat_complete(
                conversation.conversation_history, function_registry=function_registry, model=model
            )
            message = response.json()["choices"][0]
            function_arguments = get_function_arguments(
                message, conversation, function_registry=function_registry, model=model
            )
    else:
        print("Function not required, responding to user")
    return function_arguments


@retry(retry=retry_if_exception, wait=wait_random_exponential(min=5, max=40), stop=stop_after_attempt(3))
def chat_complete_execute_fn(
    conversation: Conversation,
    function_registry: ToolRegistry,
    callable_function: Callable,
    model: str,
    debug: bool = False,
):
    response = chat_complete(
        conversation.conversation_history, function_registry=function_registry, model=model, debug=debug
    )
    print(response.json())
    message = response.json()["choices"][0]
    function_arguments = get_function_arguments(
        message=message, conversation=conversation, function_registry=function_registry, model=model
    )
    results = callable_function(**function_arguments)
    conversation.add_message(role="function", name=callable_function.__name__, content=str(results))
    response = chat_complete(conversation.conversation_history, function_registry=function_registry, model=model)
    assistant_message = response.json()["choices"][0]["message"]["content"]
    conversation.add_message(role="assistant", content=assistant_message)
    return assistant_message

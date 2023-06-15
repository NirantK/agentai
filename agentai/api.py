"""
API functions for the agentai package
"""
from typing import Callable

from loguru import logger
from openai import ChatCompletion
from tenacity import (
    retry,
    stop_after_attempt,
    retry_if_exception_type,
    wait_exponential,
)

from .conversation import Conversation
from .openai_function import ToolRegistry

logger.disable(__name__)


@retry(retry=retry_if_exception_type(ValueError), stop=stop_after_attempt(5))
def chat_complete(
    conversation: Conversation,
    model,
    tool_registry: ToolRegistry = None,
    return_function_params: bool = False,
):
    messages = [message.dict(exclude_unset=True) for message in conversation.history]
    if len(messages) == 0:
        raise UserWarning("Conversation history is empty")

    functions = (
        tool_registry.get_all_function_information()
        if tool_registry is not None
        else []
    )

    response = ChatCompletion.create(
        model=model,
        messages=messages,
        functions=functions,
    )

    message = response.choices[0]["message"]
    logger.info(f"OpenAI API returned: {message}")
    # When function params are expected
    if return_function_params:
        finish_reason = response.choices[0].get("finish_reason", None)
        if finish_reason is not None and finish_reason == "function_call":
            logger.info(f"Got Function Call: {response}")
            return response
        raise ValueError(f"Expected function parameters, but received: {response}")

    # When a message is expected
    if message["content"] is not None:
        logger.info(f"Got Message: {response}")
        return response

    raise ValueError(
        f"Expected a message, but received function parameters: {response}"
    )


def get_function_arguments(
    message, conversation: Conversation, tool_registry: ToolRegistry, model: str
):
    function_arguments = {}
    if message["finish_reason"] == "function_call":
        arguments = message["message"]["function_call"]["arguments"]
        try:
            function_arguments = eval(arguments)
        except SyntaxError:
            print("Syntax error, trying again")
            response = chat_complete(
                conversation.history, tool_registry=tool_registry, model=model
            )
            message = response.json()["choices"][0]
            function_arguments = get_function_arguments(
                message, conversation, tool_registry=tool_registry, model=model
            )
        return function_arguments
    raise ValueError(f"Unexpected message: {message}")


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def chat_complete_execute_fn(
    conversation: Conversation,
    tool_registry: ToolRegistry,
    callable_function: Callable,
    model: str,
):
    response = chat_complete(
        conversation=conversation,
        tool_registry=tool_registry,
        model=model,
        return_function_params=True,
    )
    message = response.json()["choices"][0]
    function_arguments = get_function_arguments(
        message=message,
        conversation=conversation,
        tool_registry=tool_registry,
        model=model,
    )
    logger.debug(f"function_arguments: {function_arguments}")
    results = callable_function(**function_arguments)
    logger.debug(f"results: {results}")
    conversation.add_message(
        role="function", name=callable_function.__name__, content=str(results)
    )

    response = chat_complete(
        conversation=conversation,
        tool_registry=tool_registry,
        model=model,
        return_function_params=False,
    )
    assistant_message = response.json()["choices"][0]["message"]["content"]
    logger.debug(f"assistant_message: {assistant_message}")
    conversation.add_message(role="assistant", content=assistant_message)
    return assistant_message

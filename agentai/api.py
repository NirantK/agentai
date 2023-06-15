"""
API functions for the agentai package
"""
import json
from typing import Any, Callable, Tuple

from loguru import logger
from openai import ChatCompletion
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_random

from .conversation import Conversation
from .openai_function import ToolRegistry

logger.disable(__name__)


@retry(
    retry=retry_if_exception_type(ValueError),
    stop=stop_after_attempt(5),
)
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

    if len(functions) == 0 and return_function_params:
        raise UserWarning("No functions registered but expecting function parameters")

    completion = ChatCompletion.create(
        model=model,
        messages=messages,
        functions=functions,
    )

    message = completion.choices[0].message
    logger.info(f"OpenAI API returned: {message}")
    # When function params are expected
    if return_function_params:
        finish_reason = completion.choices[0].get("finish_reason", None)
        if finish_reason is not None and finish_reason == "function_call":
            logger.info(f"Got Function Call: {completion}")
            return completion
        raise ValueError(f"Expected function parameters, but received: {completion}")

    # When a message is expected
    if message["content"] is not None:
        logger.info(f"Got Message: {completion}")
        return completion

    raise ValueError(
        f"Expected a message, but received function parameters: {completion}"
    )


@retry(
    retry=retry_if_exception_type(ValueError),
    stop=stop_after_attempt(3),
    wait=wait_random(min=1, max=3),
    # wait=wait_exponential(multiplier=1, min=4, max=10),
)
def chat_complete_execute_fn(
    conversation: Conversation,
    tool_registry: ToolRegistry,
    model: str,
) -> Tuple[Any, Callable]:
    """
    Generate Argument and Execute a function from the Registry by the OpenAI API

    Args:
        conversation (Conversation): _description_
        tool_registry (ToolRegistry): _description_
        model (str): _description_

    Returns:
        Tuple[Any, Callable]: Results, Callable Function
    """
    completion = chat_complete(
        conversation=conversation,
        tool_registry=tool_registry,
        model=model,
        return_function_params=True,
    )
    message = completion.choices[0].message
    function_call = message["function_call"]
    function_arguments = json.loads(function_call["arguments"])
    logger.info(f"function_arguments: {function_arguments}")
    callable_function = tool_registry.get(function_call["name"])
    logger.info(f"callable_function: {callable_function}")
    callable_function.validate(**function_arguments)
    logger.info("Validated function arguments")
    results = callable_function(**function_arguments)
    logger.info(f"results: {results}")
    return results, function_arguments, callable_function

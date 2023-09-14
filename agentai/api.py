"""
API functions for the agentai package
"""
import inspect
import json
from typing import Any, Callable, Tuple, Union

from loguru import logger
from openai import ChatCompletion
from openai.error import RateLimitError
from pydantic import BaseModel
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    wait_random,
)

from .conversation import Conversation
from .tool_registry import ToolRegistry

logger.disable(__name__)


def validate_function_args(func, args):
    parameters = inspect.signature(func).parameters
    validated_args = {}
    for param_name, param_value in args.items():
        if param_name in parameters:
            param_type = parameters[param_name].annotation
            if issubclass(param_type, BaseModel):
                param_value = param_type(**param_value)
            validated_args[param_name] = param_value
    return validated_args


@retry(
    retry=retry_if_exception_type((ValueError, RateLimitError)),
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=10),
)
def chat_complete(
    conversation: Conversation,
    model: str,
    tool_registry: ToolRegistry = None,
    function_call: Union[str, dict] = "auto",
):
    messages = [message.dict(exclude_unset=True) for message in conversation.history]
    if len(messages) == 0:
        raise UserWarning("Conversation history is empty")

    functions = tool_registry.get_all_function_information() if tool_registry is not None else []

    if len(functions) == 0 and function_call is not None:
        raise UserWarning("No functions registered but expecting function parameters")

    completion = ChatCompletion.create(
        model=model,
        messages=messages,
        functions=functions,
        function_call=function_call,
    )

    message = completion.choices[0].message
    logger.info(f"OpenAI API returned: {message}")
    return completion


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
        function_call="auto",
    )
    message = completion.choices[0].message
    function_call = message["function_call"]
    function_arguments = json.loads(function_call["arguments"])
    logger.info(f"function_arguments: {function_arguments}")
    callable_function = tool_registry.get(function_call["name"])
    logger.info(f"callable_function: {callable_function}")
    validated_args = validate_function_args(callable_function, function_arguments)
    logger.info("Validated function arguments")
    results = callable_function(**validated_args)
    logger.info(f"results: {results}")
    return results, function_arguments, callable_function
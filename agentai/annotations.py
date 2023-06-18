"""
This module contains the function parser,
Uses docstring and type annotations to give a JSON format that can be used by the OpenAI API.
"""
import json
from typing import Any, Callable

from pydantic import validate_arguments

from .tool_registry import ToolRegistry
from .conversation import Conversation


class tool:
    def __init__(self, registry: ToolRegistry, depends_on=None):
        if registry is None:
            raise ValueError("The registry cannot be None")
        if not isinstance(registry, ToolRegistry):
            raise TypeError(
                f"The registry must be an instance of ToolRegistry, got {registry} with type: {type(registry)} instead"
            )
        self.registry = registry
        self.depends_on = depends_on

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        # Check if the function has dependencies
        if self.depends_on:
            # Check if the dependency is a function and get its name, else assume it's a string
            dependency_name = (
                self.depends_on.__name__
                if callable(self.depends_on)
                else self.depends_on
            )

            # Check if the dependency exists in the registry
            if dependency_name not in self.registry.functions:
                raise ValueError(
                    f"Dependency function '{dependency_name}' is not registered in the registry"
                )

        func._schema = self.registry.function_schema(func)
        func.validate_func = validate_arguments(func).model.schema()
        func.from_completion = lambda completion: self.from_completion(func, completion)
        func.execute_from_completion = lambda completion: self.execute_from_completion(
            func, completion
        )
        func.from_conversation = lambda conversation: self.from_conversation(
            func, conversation
        )
        self.registry.add(func)  # Register the function in the passed registry
        return func

    def from_conversation(self, func, conversation: Conversation):
        """Execute the function from a conversation"""
        raise NotImplementedError

    def from_completion(self, func, completion):
        """Execute the function from the response of an openai chat completion"""
        message = completion.choices[0].message
        function_call = message["function_call"]
        arguments = json.loads(function_call["arguments"])
        func.validate_func(**arguments)
        return arguments

    def execute_from_completion(self, func, completion):
        """
        Execute a function by name with the given completion.
        """
        function_arguments = func.from_completion(completion)
        return func(**function_arguments)

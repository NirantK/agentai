"""
This module contains the function parser,
Uses docstring and type annotations to give a JSON format that can be used by the OpenAI API.
"""
import json
from typing import Any, Callable

from openai import ChatCompletion

from .tool_registry import ToolRegistry


def ai_execute(self, name: str, completion: ChatCompletion) -> Any:
    """
    Execute a function by name with the given completion.
    """
    func = self.functions[name]
    function_arguments = json.loads(
        completion.choices[0].message["function_call"]["arguments"]
    )
    func.validate(**function_arguments)
    return func(**function_arguments)


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

        func_info = self.registry.function_schema(func)
        func.json_info = func_info
        self.registry.add(func)  # Register the function in the passed registry
        return func

    # def from_conversation(self, conversation: Conversation, model: str):
    #     mock_registry = ToolRegistry()
    #     mock_registry.add(self)

    def from_completion(self, completion, throw_error=True):
        """Execute the function from the response of an openai chat completion"""
        message = completion.choices[0].message

        if throw_error:
            assert "function_call" in message, "No function call detected"
            assert (
                message["function_call"]["name"] == self.schema["name"]
            ), "Function name does not match"

        function_call = message["function_call"]
        arguments = json.loads(function_call["arguments"])
        return self.validate_func(**arguments)

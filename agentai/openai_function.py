"""
This module contains the function parser,
Uses docstring and type annotations to give a JSON format that can be used by the OpenAI API.
"""
import enum
import inspect
import typing
from typing import Any, Callable

from docstring_parser import parse
from pydantic import validate_arguments


def parse_annotation(annotation):
    if getattr(annotation, "__origin__", None) == typing.Union:
        types = [
            t.__name__ if t.__name__ != "NoneType" else "None"
            for t in annotation.__args__
        ]
        return to_json_schema_type(types[0])
    elif issubclass(annotation, enum.Enum):  # If the annotation is an Enum type
        return "enum", [
            item.name for item in annotation
        ]  # Return 'enum' and a list of the names of the enum members
    elif getattr(annotation, "__origin__", None) is not None:
        if annotation._name is not None:
            return f"{to_json_schema_type(annotation._name)}[{','.join([to_json_schema_type(i.__name__) for i in annotation.__args__])}]"
        else:
            return f"{to_json_schema_type(annotation.__origin__.__name__)}[{','.join([to_json_schema_type(i.__name__) for i in annotation.__args__])}]"
    else:
        return to_json_schema_type(annotation.__name__)


class ToolRegistry:
    """
    A registry for functions that can be called by the OpenAI API.
    """

    def __init__(self):
        self.functions = {}

    def to_list(self):
        return list(self.functions.items())

    def add(self, func: Callable[..., Any]):
        """
        Register a function to the registry.
        """
        func.validate = validate_arguments(func)
        self.functions[func.__name__] = func

    def function_schema(self, func: Callable) -> dict:
        signature = inspect.signature(func)
        docstring = inspect.getdoc(func)
        docstring_parsed = parse(docstring)

        parameters = dict()
        required = []

        for name, param in signature.parameters.items():
            json_type = parse_annotation(param.annotation)

            if (
                isinstance(json_type, tuple) and json_type[0] == "enum"
            ):  # If the type is an Enum
                param_info = {
                    "type": "string",
                    "enum": json_type[
                        1
                    ],  # Add an 'enum' field with the names of the enum members
                    "description": "",
                }
            else:
                param_info = {"type": json_type, "description": ""}

            if (
                json_type != "any"
                and name != "self"
                and param.default == inspect.Parameter.empty
            ):
                required.append(name)

            for doc_param in docstring_parsed.params:
                if doc_param.arg_name == name:
                    param_info["description"] = doc_param.description

            parameters[name] = param_info

        function_info = {
            "name": func.__name__,
            "description": docstring_parsed.short_description,
            "parameters": {
                "type": "object",
                "properties": parameters,
                "required": required,
            },
        }

        return function_info

    def get_all_function_information(self):
        """
        Get all function information from the registry.
        """
        return [self.function_schema(func) for func in self.functions.values()]

    def get(self, name: str) -> Callable[..., Any]:
        """
        Get a function from the registry.
        """
        return self.functions[name]


def to_json_schema_type(type_name: str) -> str:
    type_map = {
        "str": "string",
        "int": "integer",
        "float": "number",
        "bool": "boolean",
        "None": "null",
        "Any": "any",
        "Dict": "object",
        "List": "array",
        "Optional": "any",
    }
    return type_map.get(type_name, "any")


def docstring_parameters(**kwargs):
    def dec(obj):
        obj.__doc__ = obj.__doc__.format(**kwargs)
        return obj

    return dec


def tool(registry: ToolRegistry, depends_on=None):
    if registry is None:
        raise ValueError("The registry cannot be None")
    if not isinstance(registry, ToolRegistry):
        raise TypeError(
            f"The registry must be an instance of ToolRegistry, got {registry} with type: {type(registry)} instead"
        )

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        # Check if the function has dependencies
        if depends_on:
            # Check if the dependency is a function and get its name, else assume it's a string
            dependency_name = (
                depends_on.__name__ if callable(depends_on) else depends_on
            )

            # Check if the dependency exists in the registry
            if dependency_name not in registry.functions:
                raise ValueError(
                    f"Dependency function '{dependency_name}' is not registered in the registry"
                )

        func_info = registry.function_schema(func)
        func.json_info = func_info
        registry.add(func)  # Register the function in the passed registry
        return func

    return decorator

"""
This module contains the function parser,
Uses docstring and type annotations to give a JSON format that can be used by the OpenAI API.
"""
import enum
import inspect
from typing import Any, Callable, TypedDict, Optional, Literal, Union

from docstring_parser import parse


ArgName = str
JsonPrimitive = Literal["string", "integer", "number", "boolean", "null", "any", "object", "array"]

class ArgProperties(TypedDict):
    type: JsonPrimitive
    description: Optional[str]
    enum: Optional[list[str]]

class FunctionParameters(TypedDict):
    type: Literal["object"]
    properties: dict[ArgName, ArgProperties] # function arg name -> arg properties
    required: list[ArgName]

class FunctionMetadata(TypedDict):
    name: str
    description: str
    parameters: FunctionParameters


def parse_annotation(annotation):
    if getattr(annotation, "__origin__", None) == Union:
        types = [t.__name__ if t.__name__ != "NoneType" else "None" for t in annotation.__args__]
        return to_json_primitive(types[0])
    elif issubclass(annotation, enum.Enum):  # If the annotation is an Enum type
        return "enum", [item.name for item in annotation]  # Return 'enum' and a list of the names of the enum members
    elif getattr(annotation, "__origin__", None) is not None:
        if annotation._name is not None:
            return f"{to_json_primitive(annotation._name)}[{','.join([to_json_primitive(i.__name__) for i in annotation.__args__])}]"
        else:
            return f"{to_json_primitive(annotation.__origin__.__name__)}[{','.join([to_json_primitive(i.__name__) for i in annotation.__args__])}]"
    else:
        return to_json_primitive(annotation.__name__)


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
        self.functions[func.__name__] = func

    def get_function_metadata(self, func: Callable) -> FunctionMetadata:
        signature = inspect.signature(func)
        docstring = inspect.getdoc(func)
        docstring_parsed = parse(docstring)

        args_map: dict[ArgName, ArgProperties] = dict()
        required = []

        for arg_name, arg in signature.parameters.items():
            json_type = parse_annotation(arg.annotation)

            if isinstance(json_type, tuple) and json_type[0] == "enum":  # If the type is an Enum
                arg_properties: ArgProperties = {
                    "type": "string",
                    "enum": json_type[1],  # Add an 'enum' field with the names of the enum members
                    "description": "",
                }
            else:
                arg_properties: ArgProperties = {"type": json_type, "description": ""}

            if json_type != "any" and arg_name != "self" and arg.default == inspect.Parameter.empty:
                required.append(arg_name)

            for doc_param in docstring_parsed.params:
                if doc_param.arg_name == arg_name:
                    arg_properties["description"] = doc_param.description

            args_map[arg_name] = arg_properties

        metadata: FunctionMetadata = {
            "name": func.__name__,
            "description": docstring_parsed.short_description,
            "parameters": {"type": "object", "properties": args_map, "required": required},
        }

        return metadata

    def get_metadata(self):
        """
        Get all function metadata from the registry.
        """
        return [self.get_function_metadata(func) for func in self.functions.values()]

    def get(self, name: str) -> Callable[..., Any]:
        """
        Get a function from the registry.
        """
        return self.functions[name]


def to_json_primitive(python_type: str) -> JsonPrimitive:
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
    return type_map.get(python_type, "any")


def docstring_parameters(**kwargs):
    def dec(obj):
        obj.__doc__ = obj.__doc__.format(**kwargs)
        return obj

    return dec

class Tool(Callable):
    metadata: FunctionMetadata


def tool(registry: ToolRegistry, depends_on=None) -> Tool:
    if registry is None:
        raise ValueError("The registry cannot be None")
    if not isinstance(registry, ToolRegistry):
        raise TypeError(f"The registry must be an instance of FunctionRegistry, got {registry} instead")

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        # Check if the function has dependencies
        if depends_on:
            # Check if the dependency is a function and get its name, else assume it's a string
            dependency_name = depends_on.__name__ if callable(depends_on) else depends_on

            # Check if the dependency exists in the registry
            if dependency_name not in registry.functions:
                raise ValueError(f"Dependency function '{dependency_name}' is not registered in the registry")

        func_info = registry.get_function_metadata(func)
        func.metadata = func_info
        registry.add(func)  # Register the function in the passed registry
        return func

    return decorator

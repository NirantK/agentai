"""
This module contains the function parser, 
uses docstring to give a JSON format that can be used by the OpenAI API.
"""
import inspect
import typing
import json
import enum
from typing import Any, Callable

from docstring_parser import parse


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


import enum
import inspect
from typing import Any
from docstring_parser import parse


def parse_annotation(annotation):
    if getattr(annotation, "__origin__", None) == typing.Union:
        types = [t.__name__ if t.__name__ != "NoneType" else "None" for t in annotation.__args__]
        return to_json_schema_type(types[0])
    elif issubclass(annotation, enum.Enum):  # If the annotation is an Enum type
        return "enum", [item.name for item in annotation]  # Return 'enum' and a list of the names of the enum members
    elif getattr(annotation, "__origin__", None) is not None:
        if annotation._name is not None:
            return f"{to_json_schema_type(annotation._name)}[{','.join([to_json_schema_type(i.__name__) for i in annotation.__args__])}]"
        else:
            return f"{to_json_schema_type(annotation.__origin__.__name__)}[{','.join([to_json_schema_type(i.__name__) for i in annotation.__args__])}]"
    else:
        return to_json_schema_type(annotation.__name__)


def get_function_info(func: Any) -> str:
    signature = inspect.signature(func)
    docstring = inspect.getdoc(func)
    docstring_parsed = parse(docstring)

    parameters = dict()
    required = []

    for name, param in signature.parameters.items():
        json_type = parse_annotation(param.annotation)

        if isinstance(json_type, tuple) and json_type[0] == "enum":  # If the type is an Enum
            param_info = {
                "type": "string",
                "enum": json_type[1],  # Add an 'enum' field with the names of the enum members
                "description": "",
            }
        else:
            param_info = {"type": json_type, "description": ""}

        if json_type != "any" and name != "self" and param.default == inspect.Parameter.empty:
            required.append(name)

        for doc_param in docstring_parsed.params:
            if doc_param.arg_name == name:
                param_info["description"] = doc_param.description

        parameters[name] = param_info

    function_info = {
        "name": func.__name__,
        "description": docstring_parsed.short_description,
        "parameters": {"type": "object", "properties": parameters, "required": required},
    }

    return json.dumps(function_info, indent=4)


def function_info(func: Callable[..., Any]) -> Callable[..., Any]:
    func_info = get_function_info(func)
    func.json_info = func_info
    return func

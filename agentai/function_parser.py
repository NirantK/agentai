"""
This module contains the function parser, 
uses docstring to give a JSON format that can be used by the OpenAI API.
"""
import inspect
import json
import typing
from typing import Any

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


def parse_annotation(annotation):
    if getattr(annotation, "__origin__", None) == typing.Union:
        types = [t.__name__ if t.__name__ != "NoneType" else "None" for t in annotation.__args__]
        return to_json_schema_type("Optional"), to_json_schema_type(types[0])
    elif getattr(annotation, "__origin__", None) is not None:
        if annotation._name is not None:
            return to_json_schema_type(annotation._name), [to_json_schema_type(i.__name__) for i in annotation.__args__]
        else:
            return to_json_schema_type(annotation.__origin__.__name__), [
                to_json_schema_type(i.__name__) for i in annotation.__args__
            ]
    else:
        return to_json_schema_type(annotation.__name__), None


def get_function_info(func: Any) -> str:
    signature = inspect.signature(func)
    docstring = inspect.getdoc(func)
    docstring_parsed = parse(docstring)

    parameters = dict()
    required = []

    for name, param in signature.parameters.items():
        json_type, subtypes = parse_annotation(param.annotation)

        param_info = {"type": json_type, "description": ""}

        if subtypes is not None and json_type == "array":
            param_info["items"] = {"type": subtypes[0]}

        if param.default != inspect.Parameter.empty:
            if isinstance(param.default, str):
                param_info["default"] = param.default
            else:
                param_info["default"] = str(param.default)

        # If the parameter type is not Optional and it's not 'self', it's required.
        if not json_type == "any" and name != "self":
            required.append(name)

        # Extract description from parsed docstring
        for doc_param in docstring_parsed.params:
            if doc_param.arg_name == name:
                param_info["description"] = doc_param.description

        parameters[name] = param_info

    function_info = {
        "name": func.__name__,
        "description": docstring_parsed.short_description,
        "parameters": {"type": "object", "properties": parameters},
        "required": required,
    }

    return json.dumps(function_info, indent=4)

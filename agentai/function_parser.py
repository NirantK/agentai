import inspect
import json
import typing
from typing import Any

from docstring_parser import parse


def to_json_schema_type(type_name: str) -> str:
    """
    Convert a Python type to a JSON type as asked by the OpenAPI spec.
    Based on JSONSchema: https://json-schema.org/understanding-json-schema/
    and OpenAI API Reference: https://platform.openai.com/docs/api-reference/chat/create

    Args:
        type_name (str): _description_

    Returns:
        str: _description_
    """
    type_map = {
        "str": "string",
        "int": "number",
        "float": "number",
        "bool": "boolean",
        "None": "null",
        "Any": "AnyOf",
        "Dict[str, Any]": "object",
    }
    return type_map.get(type_name, "AnyOf")


def parse_annotation(annotation):
    """
    Parse the annotation of a function parameter.

    Args:
        annotation (_type_): _description_

    Returns:
        _type_: _description_
    """
    if getattr(annotation, "__origin__", None) == typing.Union:
        types = [t.__name__ if t.__name__ != "NoneType" else "None" for t in annotation.__args__]
        return f"Optional[{types[0]}]"
    elif getattr(annotation, "__origin__", None) is not None:
        if annotation._name is not None:
            return f"{annotation._name}[{','.join([i.__name__ for i in annotation.__args__])}]"
        else:
            return f"{annotation.__origin__.__name__}[{','.join([i.__name__ for i in annotation.__args__])}]"
    else:
        return annotation.__name__


def get_function_info(func: Any) -> str:
    signature = inspect.signature(func)
    docstring = inspect.getdoc(func)
    docstring_parsed = parse(docstring)

    parameters = dict()
    required = []

    for name, param in signature.parameters.items():
        param_type = parse_annotation(param.annotation)

        param_info = {"type": param_type, "description": ""}

        if param.default != inspect.Parameter.empty:
            if isinstance(param.default, str):
                param_info["default"] = param.default
            else:
                param_info["default"] = str(param.default)

        # If the parameter type is not Optional and it's not 'self', it's required.
        if not param_type.startswith("Optional") and name != "self":
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

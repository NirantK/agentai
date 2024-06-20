import re
import json


# From https://github.com/Stevenic/alphawave-py/blob/main/src/alphawave/Response.py#L26
def parse_json(text):
    text = "".join(c for c in text if c.isprintable())
    text = text.replace("{\n", "{")
    text = text.replace("}\n", "}")
    # text = re.sub(r"'([^\"']+)'", r'"\1"', text) # all pairs as doublequote
    text = re.sub(r"'([^\"']+)':", r'"\1":', text)  # keys as doublequote
    # text = re.sub(r'"([^\'"]+)":', r"'\1':", text) # keys as singlequote
    # text = text.replace("'", '"')
    # text = text.replace("\'", '"')
    start_brace = text.find("{")
    if start_brace >= 0:
        obj_text = text[start_brace:]
        nesting = ["}"]
        cleaned = "{"
        in_string = False
        i = 1
        while i < len(obj_text) and len(nesting) > 0:
            ch = obj_text[i]
            if in_string:
                cleaned += ch
                if ch == "\\":
                    i += 1
                    if i < len(obj_text):
                        cleaned += obj_text[i]
                    else:
                        return None
                elif ch == '"':
                    in_string = False
            else:
                if ch == '"':
                    in_string = True
                elif ch == "{":
                    nesting.append("}")
                elif ch == "[":
                    nesting.append("]")
                elif ch == "}":
                    close_object = nesting.pop()
                    if close_object != "}":
                        return None
                elif ch == "]":
                    close_array = nesting.pop()
                    if close_array != "]":
                        return None
                elif ch == "<":
                    ch = '"<'
                elif ch == ">":
                    ch = '>"'
                cleaned += ch
            i += 1

        if len(nesting) > 0:
            cleaned += "".join(reversed(nesting))

        try:
            if type(cleaned) == str:
                obj = json.loads(cleaned)
                return obj
            else:
                return cleaned
            return obj if len(obj.keys()) > 0 else None
        except json.JSONDecodeError:
            return cleaned
    else:
        return None

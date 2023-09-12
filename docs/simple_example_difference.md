# Simple Differences Between Using agentai and OpenAI's API Directly

This is to showcase the difference of using agentai vs. using OpenAI's API directly. You can see that the agentai version is much simpler and easier to use, cutting down on the amount of code you need to write. This can be especially useful when you have a large number of functions that you want to expose to your fellow developers.

The example below is a simple weather bot that returns the current weather for a given location and temperature scale.

<table>
<tr>
<th>with agentai</th>
<th>without  agentai</th>
</tr>
<tr>
<td>

```python
from agentai.api import chat_complete, chat_complete_execute_fn
from agentai.annotations import tool
from agentai.tool_registry import ToolRegistry
from agentai.conversation import Conversation
from enum import Enum

weather_registry = ToolRegistry()


class TemperatureUnit(Enum):
    celsius = "celsius"
    fahrenheit = "fahrenheit"


@tool(registry=weather_registry)
def get_current_weather(location: str, scale: TemperatureUnit) -> str:
    """
    Get the current weather

    Args:
        location (str): The city and state, e.g. San Francisco, CA
        scale (str): The temperature scale to use. Infer this from the user's location.

    Returns:
        str: The current weather
    """
    # Your function implementation goes here.
    return f"The current weather in {location} is x degrees {scale}"


conversation = Conversation()
conversation.add_message("user", "what is the weather like today in Chicago?")

chat_response = chat_complete_execute_fn(conversation, tool_registry=weather_registry, model="gpt-3.5-turbo")
print(chat_response) # The current weather in Chicago, IL is x degrees fahrenheit

```

</td>
<td>

```python
import openai
import json
from enum import Enum

class TemperatureUnit(Enum):
    celsius = "celsius"
    fahrenheit = "fahrenheit"

def get_current_weather(location: str, scale: TemperatureUnit) -> str:
    """
    Get the current weather

    Args:
        location (str): The city and state, e.g. San Francisco, CA
        scale (str): The temperature scale to use. Infer this from the user's location.

    Returns:
        str: The current weather
    """
    # Your function implementation goes here.
    return f"The current weather in {location} is x degrees {scale}"

get_current_weather_function = [
    {
        "name": "get_current_weather",
        "description": "Get the current weather for a specific location and temperature scale.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The location for which you want to retrieve the weather, e.g., 'New York, NY'."
                },
                "scale": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "The preferred temperature scale for the location. Choose between 'celsius' or 'fahrenheit'."
                }
            },
            "required": ["location", "scale"]
        }
    }
]

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "what is the current weather like today in Chicago?"}],
    functions=get_current_weather_function,
    function_call="auto",
)

json_response = json.loads(response["choices"][0]["message"]["function_call"]["arguments"])
print(json_response)  # {'location': 'Chicago, IL', 'unit': 'fahrenheit'}
print(get_current_weather(**json_response))  # The current weather in Chicago, IL is x degrees fahrenheit

```

</td>
</tr>
</table>

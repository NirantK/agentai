# AgentAI: OpenAI Functions + Python Functions

It is designed to make it easy to use OpenAI models e.g. GPT3.5-Turbo and GPT4 with existing Python functions by adding a simple decorator.

interact with databases, and handle structured data types.

AgentAI is a simple Python library with these ethos:

1. Let developers write code!
2. Do not invent a new syntax!
3. Make it easy to integrate with existing projects!
4. Make it easy to extend!
5. Have fun and use exclamations!

Unlike some libraries, AgentAI does NOT require you to learn a new syntax. No chains!

Instead, it empowers you to add OpenAI functions using Python decorators and then call them directly from your code.
This makes it easy to integrate AgentAI with your existing projects.

## Features

- **API Calls**: Use AgentAI to decorate your Python functions and make them magical!
- **SQL Database Interaction**: Seamlessly extract and utilize data from SQL databases.
- **Function Execution**: Generate and execute function calls based on conversation context.
- **Conversation Management**: Effectively manage and track the state of conversations. Easily define your own functions which can use messages, functions, and conversation history.

### Next Week

- _Multiple Functions_: Call multiple functions in a single conversation with a DSL/DAG.
- _Retrieval_: Use AgentAI to retrieve information from a vector Database -- but only when needed!
- _Rich Media_: Support for rich media types e.g. images, audio
- _Function Generation_: Generate Python functions based on conversation context

## Installation

Install AgentAI using pip:

```bash
pip install agentai
```

## Getting Started: Asking User for Missing Inputs till all inputs are available

1. **Import required classes and functions**

```python
from agentai.api import chat_complete, chat_complete_execute_fn
from agentai.openai_function import tool, ToolRegistry
from agentai.conversation import Conversation
from enum import Enum
weather_registry = ToolRegistry()
```

2. **Define a function with `@tool` decorator**

```python
class TemperatureUnit(Enum):
    celsius = "celsius"
    fahrenheit = "fahrenheit"


@tool(regsitry=weather_registry)
def get_current_weather(location: str, format: TemperatureUnit) -> str:
    """
    Get the current weather

    Args:
        location (str): The city and state, e.g. San Francisco, CA
        format (str): The temperature unit to use. Infer this from the users location.

    Returns:
        str: The current weather
    """
    # Your function implementation goes here.
    return ""
```

Note that `agentai` automatically parses the Python Enum type (TemperatureUnit) and passes it to the model as a JSONSchema Enum. This saves you time in writing boilerplate JSONSchema which is required by OpenAI API.

3. **Create a Conversation object and add messages**

```python
conversation = Conversation()
conversation.add_message("user", "what is the weather like today?")
```

4. **Use the `chat_complete` function to get a response from the model**

```python
chat_response = chat_complete(conversation.conversation_history, function_registry=weather_registry, model=GPT_MODEL)
```

Output:

```javascript
{'role': 'assistant',
'content': 'In which city would you like to know the current weather?'}
```

5. **Add user response to conversation and call `chat_complete` again**

Once the user provides the required information, the model can generate the function arguments:

```python
conversation.add_message("user", "I'm in Bengaluru, India")
chat_response = chat_complete(conversation.conversation_history, function_registry=weather_registry, model=GPT_MODEL)

eval(chat_response.json()["choices"][0]["message"]["function_call"]["arguments"])
```

Output:

```python
{'location': 'Bengaluru, India', 'format': 'celsius'}
```

## Example: Doing a Database Query with Generated SQL

1. **Define a function with `@tool` decorator**

```python
db_registry = ToolRegistry()

@tool(registry=db_registry)
def ask_database(query: str) -> List[Tuple[str, str]]:
    """
    Use this function to answer user questions about music. Input should be a fully formed SQL query.

    Args:
        query (str): SQL query extracting info to answer the user's question.
                    SQL should be written using this database schema: <database_schema_string>
                    IMPORTANT: Please return a fixed SQL in PLAIN TEXT.
                    Your response should consist of ONLY the SQL query.
    """
    try:
        results = conn.execute(query).fetchall()
        return results
    except Exception as e:
        raise Exception(f"SQL error: {e}")
```

2. **Registering the function and using it**

```python
agentai_functions = [json.loads(func.json_info) for func in [ask_database]]

from agentai.api import chat_complete_execute_fn
agent_system_message = """You are ChinookGPT, a helpful assistant who gets answers to user questions from the Chinook Music Database.
Provide as many details as possible to your users
Begin!"""

sql_conversation = Conversation()
sql_conversation.add_message(role="system", content=agent_system_message)
sql_conversation.add_message("user", "Hi, who are the top 5 artists by number of tracks")
assistant_message = chat_complete_execute_fn(
    conversation=sql_conversation, functions=agentai_functions, model=GPT_MODEL, callable_function=ask_database
)

sql_conversation.display_conversation(detailed=True)
```

Output:

```traceback
system: You are ChinookGPT, a helpful assistant who gets answers to user questions from the Chinook Music Database.
Provide as many details as possible to your users
Begin!


user: Hi, who are the top 5 artists by number of tracks


function: [('Iron Maiden', 213), ('U2', 135), ('Led Zeppelin', 114), ('Metallica', 112), ('Lost', 92)]


assistant: The top 5 artists by number of tracks are:

1. Iron Maiden - 213 tracks
2. U2 - 135 tracks
3. Led Zeppelin - 114 tracks
4. Metallica - 112 tracks
5. Lost - 92 tracks
```

## Detailed Examples

Check out our detailed [notebooks with examples](./docs/) where we demonstrate how to integrate AgentAI with a chatbot to create a powerful conversational assistant that can answer questions using a SQLite database.

## Contributing

We welcome contributions! Please see our [contributing guidelines](./.github/CONTRIBUTING.md) for more details.

## Support

If you encounter any issues or require further assistance, please raise an issue on our [GitHub repository](https://github.com/NirantK/agentai/issues).

We hope you enjoy using AgentAI and find it helpful in powering up your AI models. Happy coding!

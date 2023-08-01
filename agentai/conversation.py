import threading
from typing import List, Optional

import tiktoken
from pydantic import BaseModel
from termcolor import colored


class Message(BaseModel):
    role: str
    content: str
    name: Optional[str]


class Conversation:
    def __init__(self, history: List[Message] = [], id: Optional[str] = None, max_history_length: int = 20):
        self.history: List[Message] = history
        self.role_to_color = {
            "system": "red",
            "user": "green",
            "assistant": "blue",
            "function": "magenta",
        }
        self.id = id
        self.max_history_length = max_history_length

    def add_message(self, role: str, content: str, name: Optional[str] = None) -> None:
        message_dict = {"role": role, "content": content}
        if name:
            message_dict["name"] = name
        message = Message(**message_dict)
        self.history.append(message)
        self.trim_history()

    def display_conversation(self) -> None:
        for message in self.history:
            print(
                colored(
                    f"{message.role}: {message.content}\n\n",
                    self.role_to_color[message.role.lower()],
                )
            )

    def trim_history(self) -> None:
        "Function to keep the message history from growing too large"
        if len(self.history) > self.max_history_length:
            self.history = self.history[-self.max_history_length :]

    def trim_history_by_tokens(self, max_tokens: int) -> None:
        """Function to keep the message history based on the number of tokens
        This is important to keep the message history crisp to not flood over the
        max_tokens limit of the AI models and give lee-way to the user prompt
        """
        local = threading.local()
        try:
            enc = local.gpt2enc
        except AttributeError:
            enc = tiktoken.get_encoding("gpt2")
            local.gpt2enc = enc

        total_tokens = 0
        for i in range(len(self.history) - 1, -1, -1):
            # Iterate over the messages in reverse order - from the latest to the oldest messages
            message = self.history[i]  # Message(role='User', content='I appreciate that. Take care too!', name=None)
            content = message.content
            tokens = len(enc.encode(content))
            total_tokens += tokens
            if total_tokens > max_tokens:
                # Trim the history inplace to keep the total tokens under max_tokens
                self.history = self.history[i + 1 :]
                break

    def get_history(self, max_tokens=100) -> List[Message]:
        """Function to get the conversation history based on the number of tokens"""
        self.trim_history_by_tokens(max_tokens=max_tokens)
        return self.history

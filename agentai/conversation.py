from typing import List, Optional

from pydantic import BaseModel
from termcolor import colored


class Message(BaseModel):
    role: str
    content: str
    name: Optional[str]


class Conversation:
    def __init__(self):
        self.history: List[Message] = []
        self.role_to_color = {
            "system": "red",
            "user": "green",
            "assistant": "blue",
            "function": "magenta",
        }

    def add_message(self, role: str, content: str, name: Optional[str] = None):
        message = {"role": role, "content": content}
        if name is not None:
            message["name"] = name

        self.history.append(Message(**message))

    def display_conversation(self):
        for message in self.history:
            print(
                colored(
                    f"{message.role}: {message.content}\n\n",
                    self.role_to_color[message.role],
                )
            )

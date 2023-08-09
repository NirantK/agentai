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
    def __init__(
        self,
        history: List[Message] = [],
        id: Optional[str] = None,
        max_history_tokens: Optional[int] = None,
        model: Optional[str] = None,
    ) -> None:
        self.history: List[Message] = history
        self.trimmed_history: List[Message] = []
        self.role_to_color = {
            "system": "red",
            "user": "green",
            "assistant": "blue",
            "function": "magenta",
        }
        self.id = id
        self.max_history_tokens = max_history_tokens
        self.model = model

    def add_message(self, role: str, content: str, name: Optional[str] = None) -> None:
        message_dict = {"role": role, "content": content}
        if name:
            message_dict["name"] = name
        message = Message(**message_dict)
        self.history.append(message)
        if self.max_history_tokens and self.model:
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
        """Function to get the conversation history based on the number of tokens"""

        # raise an error if max_history_tokens or model is not set
        if not self.max_history_tokens:
            raise ValueError("max_history_tokens is not set in Conversation")
        if not self.model:
            raise ValueError("model is not set in Conversation")

        local = threading.local()
        try:
            enc = local.encoder
        except AttributeError:
            enc = tiktoken.encoding_for_model(self.model)
            local.encoder = enc

        total_tokens = 0
        # Iterate 2 at a time to avoid cutting in between a (prompt, response) pair
        for i in range(len(self.history) - 1, -1, -2):
            # Iterate over the messages in reverse order - from the latest to the oldest messages
            message = self.history[i]  # Message(role='User', content='I appreciate that. Take care too!', name=None)
            content = message.content
            tokens = len(enc.encode(content))
            total_tokens += tokens
            if total_tokens > self.max_history_tokens:
                # Trim the history to keep the total tokens under max_tokens
                # and store the trimmed history in self.trimmed_history
                # to have a faster access to it later
                self.trimmed_history = self.history[i + 1 :]
                break

    def get_history(self, trimmed: bool = False) -> List[Message]:
        # Return the trimmed history if it exists and trimmed is True
        if trimmed:
            if not self.trimmed_history:
                self.trim_history()
            return self.trimmed_history
        # Return the full history otherwise
        return self.history

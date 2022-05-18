import re
from dataclasses import dataclass
from typing import NewType

Channel = NewType("Channel", str)
User = NewType("User", str)
Word = NewType("Word", str)
Text = NewType("Text", str)


@dataclass(unsafe_hash=True)
class Keyword:
    channel: Channel
    user: User
    word: Word


@dataclass(frozen=True)
class Message:
    channel: Channel
    author: User
    text: Text

    def __contains__(self, word: Keyword) -> bool:
        pattern = re.compile(r"\b" + word.word + r"\b")
        return pattern.search(self.text) is not None

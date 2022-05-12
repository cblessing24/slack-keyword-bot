import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Keyword:
    channel: str
    user: str
    word: str


@dataclass(frozen=True)
class Message:
    channel: str
    user: str
    text: str

    def __contains__(self, word: Keyword) -> bool:
        pattern = re.compile(r"\b" + word.word + r"\b")
        return pattern.search(self.text) is not None

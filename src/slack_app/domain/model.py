import re
from dataclasses import dataclass
from typing import Iterable, Iterator, NewType

Channel = NewType("Channel", str)
User = NewType("User", str)
Word = NewType("Word", str)
Text = NewType("Text", str)


@dataclass(unsafe_hash=True)
class Keyword:
    channel: Channel
    subscriber: User
    word: Word
    active: bool = True


@dataclass(frozen=True)
class Message:
    channel: Channel
    author: User
    text: Text

    def __contains__(self, word: Keyword) -> bool:
        pattern = re.compile(r"\b" + word.word + r"\b")
        return pattern.search(self.text) is not None


def get_subscribers(message: Message, keywords: Iterable[Keyword]) -> Iterator[User]:
    for keyword in keywords:
        if not keyword.active:
            continue
        if keyword.subscriber == message.author:
            continue
        if keyword in message:
            yield keyword.subscriber

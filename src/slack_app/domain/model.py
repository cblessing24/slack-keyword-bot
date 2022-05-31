from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Iterator, NewType, Optional

ChannelName = NewType("ChannelName", str)
User = NewType("User", str)
Word = NewType("Word", str)
Text = NewType("Text", str)


class Channel:
    def __init__(self, channel_name: ChannelName, keywords: Optional[Iterable[Keyword]] = None) -> None:
        self.channel_name = channel_name
        self.keywords = set(keywords) if keywords is not None else set()

    def get_subscribers(self, message: Message) -> Iterator[User]:
        for keyword in self.keywords:
            if keyword.unsubscribed:
                continue
            if keyword.subscriber == message.author:
                continue
            if keyword in message:
                yield keyword.subscriber

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(channel_name='{self.channel_name}', keywords={self.keywords})"


@dataclass(unsafe_hash=True)
class Keyword:
    channel_name: ChannelName
    subscriber: User
    word: Word
    unsubscribed: bool = False


@dataclass(frozen=True)
class Message:
    channel_name: ChannelName
    author: User
    text: Text

    def __contains__(self, word: Keyword) -> bool:
        pattern = re.compile(r"\b" + word.word + r"\b")
        return pattern.search(self.text) is not None

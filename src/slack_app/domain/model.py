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
        self.keywords = list(keywords) if keywords is not None else []


@dataclass(unsafe_hash=True)
class Keyword:
    channel_name: ChannelName
    subscriber: User
    word: Word
    active: bool = True


@dataclass(frozen=True)
class Message:
    channel_name: ChannelName
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

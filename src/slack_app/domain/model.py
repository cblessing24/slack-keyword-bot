from __future__ import annotations

import dataclasses
import re
from typing import Iterable, NewType, Optional

from . import events

ChannelName = NewType("ChannelName", str)
User = NewType("User", str)
Keyword = NewType("Keyword", str)
Text = NewType("Text", str)


class Channel:
    def __init__(self, channel_name: ChannelName, subscriptions: Optional[Iterable[Subscription]] = None) -> None:
        self.channel_name = channel_name
        self.subscriptions = set(subscriptions) if subscriptions is not None else set()
        self.events: list[events.Event] = []

    def subscribe(self, subscription: Subscription) -> None:
        if subscription in self.subscriptions:
            self.events.append(events.AlreadySubscribed(**dataclasses.asdict(subscription)))
            return
        self.subscriptions.add(subscription)
        self.events.append(events.Subscribed(**dataclasses.asdict(subscription)))

    def unsubscribe(self, subscription: Subscription) -> None:
        if subscription not in self.subscriptions:
            self.events.append(events.UnknownSubscription(**dataclasses.asdict(subscription)))
            return
        self.subscriptions.remove(subscription)
        self.events.append(events.Unsubscribed(**dataclasses.asdict(subscription)))

    def find_subscribed(self, message: Message) -> None:
        for subscription in self.subscriptions:
            if subscription.subscriber == message.author:
                continue
            if subscription.keyword in message:
                self.events.append(
                    events.Mentioned(
                        channel_name=message.channel_name,
                        subscriber=subscription.subscriber,
                        keyword=subscription.keyword,
                        author=message.author,
                        text=message.text,
                    )
                )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(channel_name='{self.channel_name}', subscriptions={self.subscriptions})"


@dataclasses.dataclass(unsafe_hash=True)
class Subscription:
    channel_name: ChannelName
    subscriber: User
    keyword: Keyword


@dataclasses.dataclass(frozen=True)
class Message:
    channel_name: ChannelName
    author: User
    text: Text

    def __contains__(self, keyword: Keyword) -> bool:
        pattern = re.compile(r"\b" + keyword + r"\b")
        return pattern.search(self.text) is not None

from __future__ import annotations

from dataclasses import dataclass

from . import model


@dataclass(frozen=True)
class Event:
    pass


@dataclass(frozen=True)
class Subscribed(Event):
    channel_name: str
    subscriber: str
    keyword: str


@dataclass(frozen=True)
class Unsubscribed(Event):
    channel_name: str
    subscriber: str
    keyword: str


@dataclass(frozen=True)
class SubscriberListRequired(Event):
    channel_name: str
    author: str
    text: str


@dataclass(frozen=True)
class SubscriptionsListRequired(Event):
    channel_name: str
    subscriber: str


@dataclass(frozen=True)
class AlreadySubscribed(Event):
    subscription: model.Subscription

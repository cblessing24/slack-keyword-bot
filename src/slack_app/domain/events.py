from __future__ import annotations

from dataclasses import dataclass

from . import model


@dataclass(frozen=True)
class Event:
    pass


@dataclass(frozen=True)
class Subscribed(Event):
    channel_name: model.ChannelName
    subscriber: model.User
    keyword: model.Keyword


@dataclass(frozen=True)
class AlreadySubscribed(Event):
    channel_name: model.ChannelName
    subscriber: model.User
    keyword: model.Keyword

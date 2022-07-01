from dataclasses import dataclass


@dataclass(frozen=True)
class Command:
    """Base class for all commands."""


@dataclass(frozen=True)
class Subscribe(Command):
    channel_name: str
    subscriber: str
    keyword: str


@dataclass(frozen=True)
class Unsubscribe(Command):
    channel_name: str
    subscriber: str
    keyword: str


@dataclass(frozen=True)
class FindMentions(Command):
    channel_name: str
    author: str
    text: str


@dataclass(frozen=True)
class ListSubscriptions(Command):
    channel_name: str
    subscriber: str

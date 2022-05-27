from __future__ import annotations

from typing import Protocol

import pytest

from slack_app.domain.model import Channel, ChannelName, Message, Text, User

from ..conftest import KeywordCreator


class MessageCreator(Protocol):
    def __call__(self, channel_name: str = ..., author: str = ..., text: str = ...) -> Message:
        ...


@pytest.fixture
def create_msg() -> MessageCreator:
    def create(channel_name: str = "mychannel", author: str = "bob", text: str = "Hello World") -> Message:
        return Message(channel_name=ChannelName(channel_name), author=User(author), text=Text(text))

    return create


def test_message_contains_keyword(create_keyword: KeywordCreator, create_msg: MessageCreator) -> None:
    assert create_keyword(word="World") in create_msg(text="Hello World!")


def test_message_does_not_contain_keyword(create_keyword: KeywordCreator, create_msg: MessageCreator) -> None:
    assert create_keyword(word="Goodbye") not in create_msg(text="Hello World!")


def test_message_does_not_contain_partial_keyword(create_keyword: KeywordCreator, create_msg: MessageCreator) -> None:
    assert create_keyword(word="Good") not in create_msg(text="Goodbye World!")


def test_subscribers_are_returned(create_keyword: KeywordCreator, create_msg: MessageCreator) -> None:
    message = create_msg(channel_name="mychannel", author="john", text="hello world")
    in_keyword = create_keyword(channel_name="mychannel", subscriber="bob", word="hello")
    out_keyword = create_keyword(channel_name="mychannel", subscriber="bob", word="goodbye")
    author_keyword = create_keyword(channel_name="mychannel", subscriber="john", word="hello")
    inactive_keyword = create_keyword(channel_name="mychannel", subscriber="alice", word="hello", active=False)
    channel = Channel(ChannelName("mychannel"), keywords={in_keyword, out_keyword, author_keyword, inactive_keyword})
    assert list(channel.get_subscribers(message)) == [User("bob")]


def test_channel_gets_initialized_with_empty_set_by_default() -> None:
    channel = Channel(ChannelName("mychannel"))
    assert channel.keywords == set()

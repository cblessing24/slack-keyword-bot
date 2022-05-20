from __future__ import annotations

from typing import Protocol

import pytest

from slack_app.domain.model import Channel, Message, Text, User, get_subscribers

from ..conftest import KeywordCreator


class MessageCreator(Protocol):
    def __call__(self, channel: str = ..., author: str = ..., text: str = ...) -> Message:
        ...


@pytest.fixture
def create_msg() -> MessageCreator:
    def create(channel: str = "mychannel", author: str = "bob", text: str = "Hello World") -> Message:
        return Message(channel=Channel(channel), author=User(author), text=Text(text))

    return create


def test_message_contains_keyword(create_keyword: KeywordCreator, create_msg: MessageCreator) -> None:
    assert create_keyword(word="World") in create_msg(text="Hello World!")


def test_message_does_not_contain_keyword(create_keyword: KeywordCreator, create_msg: MessageCreator) -> None:
    assert create_keyword(word="Goodbye") not in create_msg(text="Hello World!")


def test_message_does_not_contain_partial_keyword(create_keyword: KeywordCreator, create_msg: MessageCreator) -> None:
    assert create_keyword(word="Good") not in create_msg(text="Goodbye World!")


def test_subscribers_are_returned(create_keyword: KeywordCreator, create_msg: MessageCreator) -> None:
    message = create_msg(channel="mychannel", author="john", text="hello world")
    in_keyword = create_keyword(channel="mychannel", subscriber="bob", word="hello")
    out_keyword = create_keyword(channel="mychannel", subscriber="bob", word="goodbye")
    author_keyword = create_keyword(channel="mychannel", subscriber="john", word="hello")
    assert list(get_subscribers(message, [in_keyword, out_keyword, author_keyword])) == [User("bob")]

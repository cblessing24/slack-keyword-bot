from typing import Callable

import pytest

from slack_app.domain.model import Channel, Keyword, Message, Text, User, Word


def test_keyword_can_be_created() -> None:
    Keyword(channel=Channel("mychannel"), user=User("bob"), word=Word("something"))


def test_message_can_be_created() -> None:
    Message(channel=Channel("mychannel"), user=User("bob"), text=Text("hello world"))


@pytest.fixture
def create_keyword() -> Callable[[Word], Keyword]:
    def create(word: Word) -> Keyword:
        return Keyword(channel=Channel("mychannel"), user=User("bob"), word=word)

    return create


@pytest.fixture
def create_msg() -> Callable[[Text], Message]:
    def create(text: Text) -> Message:
        return Message(channel=Channel("mychannel"), user=User("bob"), text=text)

    return create


def test_message_contains_keyword(
    create_keyword: Callable[[str], Keyword], create_msg: Callable[[str], Message]
) -> None:
    assert create_keyword("World") in create_msg("Hello World!")


def test_message_does_not_contain_keyword(
    create_keyword: Callable[[str], Keyword], create_msg: Callable[[str], Message]
) -> None:
    assert create_keyword("Goodbye") not in create_msg("Hello World!")


def test_message_does_not_contain_partial_keyword(
    create_keyword: Callable[[str], Keyword], create_msg: Callable[[str], Message]
) -> None:
    assert create_keyword("Good") not in create_msg("Goodbye World!")

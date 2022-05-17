from typing import Callable

import pytest

from slack_app.domain.model import Channel, Keyword, Message, Text, User, Word


def test_keyword_can_be_created() -> None:
    Keyword(channel=Channel("mychannel"), user=User("bob"), word=Word("something"))


def test_message_can_be_created() -> None:
    Message(channel=Channel("mychannel"), user=User("bob"), text=Text("hello world"))


@pytest.fixture
def keyword() -> Callable[[Word], Keyword]:
    def _keyword(word: Word) -> Keyword:
        return Keyword(channel=Channel("mychannel"), user=User("bob"), word=word)

    return _keyword


@pytest.fixture
def msg() -> Callable[[Text], Message]:
    def _msg(text: Text) -> Message:
        return Message(channel=Channel("mychannel"), user=User("bob"), text=text)

    return _msg


def test_message_contains_keyword(keyword: Callable[[str], Keyword], msg: Callable[[str], Message]) -> None:
    assert keyword("World") in msg("Hello World!")


def test_message_does_not_contain_keyword(keyword: Callable[[str], Keyword], msg: Callable[[str], Message]) -> None:
    assert keyword("Goodbye") not in msg("Hello World!")


def test_message_does_not_contain_partial_keyword(
    keyword: Callable[[str], Keyword], msg: Callable[[str], Message]
) -> None:
    assert keyword("Good") not in msg("Goodbye World!")

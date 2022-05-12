from typing import Callable

import pytest

from slack_app.model import Keyword, Message


def test_keyword_can_be_created() -> None:
    Keyword(channel='mychannel', user='bob', word='something')


def test_message_can_be_created() -> None:
    Message(channel='mychannel', user='bob', text='hello world')


@pytest.fixture
def keyword() -> Callable[[str], Keyword]:
    def _keyword(word: str) -> Keyword:
        return Keyword(channel='mychannel', user='bob', word=word)
    return _keyword


@pytest.fixture
def msg() -> Callable[[str], Message]:
    def _msg(text: str) -> Message:
        return Message(channel='mychannel', user='bob', text=text)
    return _msg


def test_message_contains_keyword(keyword: Callable[[str,], Keyword], msg: Callable[[str], Message]) -> None:
    assert keyword("World") in msg("Hello World!")


def test_message_does_not_contain_keyword(keyword: Callable[[str,], Keyword], msg: Callable[[str], Message]) -> None:
    assert keyword("Goodbye") not in msg("Hello World!")


def test_message_does_not_contain_partial_keyword(keyword: Callable[[str,], Keyword], msg: Callable[[str], Message]) -> None:
    assert keyword("Good") not in msg("Goodbye World!")

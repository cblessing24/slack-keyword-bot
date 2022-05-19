from slack_app.domain.model import User, get_subscribers

from ..conftest import KeywordCreator, MessageCreator


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

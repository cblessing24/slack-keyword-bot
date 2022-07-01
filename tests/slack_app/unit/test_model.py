from __future__ import annotations

import dataclasses
from typing import Protocol

import pytest

from slack_app.domain import events
from slack_app.domain.model import Channel, ChannelName, Keyword, Message, Text, User

from ..conftest import SubscriptionCreator


class MessageCreator(Protocol):
    def __call__(self, channel_name: str = ..., author: str = ..., text: str = ...) -> Message:
        ...


@pytest.fixture
def create_msg() -> MessageCreator:
    def create(channel_name: str = "mychannel", author: str = "bob", text: str = "Hello World") -> Message:
        return Message(channel_name=ChannelName(channel_name), author=User(author), text=Text(text))

    return create


def test_message_contains_keyword(create_msg: MessageCreator) -> None:
    assert Keyword("World") in create_msg(text="Hello World!")


def test_message_does_not_contain_keyword(create_msg: MessageCreator) -> None:
    assert Keyword("Goodbye") not in create_msg(text="Hello World!")


def test_message_does_not_contain_partial_keyword(create_msg: MessageCreator) -> None:
    assert Keyword("Good") not in create_msg(text="Goodbye World!")


def test_channel_gets_initialized_with_empty_set_by_default() -> None:
    channel = Channel(ChannelName("mychannel"))
    assert channel.subscriptions == set()


def test_subscribe_adds_subscription_to_channel(create_subscription: SubscriptionCreator) -> None:
    channel = Channel(ChannelName("mychannel"))
    subscription = create_subscription(channel_name="mychannel", subscriber="anna", keyword="hello")
    channel.subscribe(subscription)
    assert channel.subscriptions == {subscription}


def test_subscribe_records_event_if_subscription_already_exists(
    create_subscription: SubscriptionCreator,
) -> None:
    channel = Channel(ChannelName("mychannel"))
    subscription = create_subscription(channel_name="mychannel", subscriber="anna", keyword="hello")
    channel.subscribe(subscription)
    channel.subscribe(subscription)
    assert events.AlreadySubscribed(**dataclasses.asdict(subscription)) in channel.events


def test_subscribe_records_event_if_successful(create_subscription: SubscriptionCreator) -> None:
    channel = Channel(ChannelName("mychannel"))
    subscription = create_subscription(channel_name="mychannel", subscriber="anna", keyword="hello")
    channel.subscribe(subscription)
    assert channel.events == [events.Subscribed(**dataclasses.asdict(subscription))]


def test_unsubscribe_removes_subscription_from_channel(create_subscription: SubscriptionCreator) -> None:
    channel = Channel(ChannelName("mychannel"))
    subscription = create_subscription(channel_name="mychannel", subscriber="anna", keyword="hello")
    channel.subscribe(subscription)
    channel.unsubscribe(subscription)
    assert channel.subscriptions == set()


def test_unsubscribe_records_event_if_subscription_is_unknown(create_subscription: SubscriptionCreator) -> None:
    channel = Channel(ChannelName("mychannel"))
    subscription = create_subscription(channel_name="mychannel", subscriber="anna", keyword="hello")
    channel.unsubscribe(subscription)
    assert channel.events == [events.UnknownSubscription(**dataclasses.asdict(subscription))]


def test_unsubscribe_records_event_if_successful(create_subscription: SubscriptionCreator) -> None:
    channel = Channel(ChannelName("mychannel"))
    subscription = create_subscription(channel_name="mychannel", subscriber="anna", keyword="hello")
    channel.subscribe(subscription)
    channel.unsubscribe(subscription)
    assert events.Unsubscribed(**dataclasses.asdict(subscription)) in channel.events


def test_channel_repr(create_subscription: SubscriptionCreator) -> None:
    subscriptions = {create_subscription(channel_name="mychannel", subscriber="anna", keyword="hello")}
    channel = Channel(ChannelName("mychannel"), subscriptions=subscriptions)
    assert repr(channel) == (
        "Channel(channel_name='mychannel', subscriptions={Subscription(channel_name='mychannel', "
        "subscriber='anna', keyword='hello')})"
    )

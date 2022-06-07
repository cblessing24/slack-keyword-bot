from ..domain import events, model
from .unit_of_work import AbstractUnitOfWork, R


def subscribe(event: events.Subscribed, uow: AbstractUnitOfWork[R]) -> None:
    with uow:
        channel = uow.channels.get(model.ChannelName(event.channel_name))
        if not channel:
            channel = model.Channel(model.ChannelName(event.channel_name))
            uow.channels.add(channel)
        subscription = model.Subscription(
            model.ChannelName(event.channel_name), model.User(event.subscriber), model.Keyword(event.keyword)
        )
        channel.subscribe(subscription)
        uow.commit()


def list_subscribers(event: events.SubscriberListRequired, uow: AbstractUnitOfWork[R]) -> set[str]:
    with uow:
        channel = uow.channels.get(model.ChannelName(event.channel_name))
        if not channel:
            raise ValueError("Unknown channel")
        message = model.Message(model.ChannelName(event.channel_name), model.User(event.author), model.Text(event.text))
        return set(channel.find_subscribed(message))


def list_subscriptions(event: events.SubscriptionsListRequired, uow: AbstractUnitOfWork[R]) -> set[str]:
    with uow:
        channel = uow.channels.get(model.ChannelName(event.channel_name))
        if not channel:
            raise ValueError("Unknown channel")
        return {s.keyword for s in channel.subscriptions if s.subscriber == model.User(event.subscriber)}


def unsubscribe(event: events.Unsubscribed, uow: AbstractUnitOfWork[R]) -> None:
    with uow:
        channel = uow.channels.get(model.ChannelName(event.channel_name))
        if not channel:
            raise ValueError("Unknown channel")
        try:
            subscription = next(
                s
                for s in channel.subscriptions
                if s.subscriber == model.User(event.subscriber) and s.keyword == model.Keyword(event.keyword)
            )
        except StopIteration:
            raise ValueError("Unknown subscription")
        channel.subscriptions.remove(subscription)
        uow.commit()

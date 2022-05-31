from ..domain import model
from .unit_of_work import AbstractUnitOfWork, R


def subscribe(uow: AbstractUnitOfWork[R], channel_name: str, subscriber: str, keyword: str) -> None:
    with uow:
        channel = uow.channels.get(model.ChannelName(channel_name))
        if not channel:
            channel = model.Channel(model.ChannelName(channel_name))
            uow.channels.add(channel)
        channel.subscriptions.add(
            model.Subscription(model.ChannelName(channel_name), model.User(subscriber), model.Keyword(keyword))
        )
        uow.commit()


def list_subscribers(uow: AbstractUnitOfWork[R], channel_name: str, author: str, text: str) -> set[str]:
    with uow:
        channel = uow.channels.get(model.ChannelName(channel_name))
        if not channel:
            raise ValueError("Unknown channel")
        message = model.Message(model.ChannelName(channel_name), model.User(author), model.Text(text))
        return set(channel.find_subscribed(message))


def list_subscriptions(uow: AbstractUnitOfWork[R], channel_name: str, subscriber: str) -> set[str]:
    with uow:
        channel = uow.channels.get(model.ChannelName(channel_name))
        if not channel:
            raise ValueError("Unknown channel")
        return {
            s.keyword for s in channel.subscriptions if s.subscriber == model.User(subscriber) and not s.unsubscribed
        }


def unsubscribe(uow: AbstractUnitOfWork[R], channel_name: str, subscriber: str, keyword: str) -> None:
    with uow:
        channel = uow.channels.get(model.ChannelName(channel_name))
        if not channel:
            raise ValueError("Unknown channel")
        try:
            subscription = next(
                s
                for s in channel.subscriptions
                if s.subscriber == model.User(subscriber) and s.keyword == model.Keyword(keyword)
            )
        except StopIteration:
            raise ValueError("Unknown subscription")
        subscription.unsubscribed = True
        uow.commit()

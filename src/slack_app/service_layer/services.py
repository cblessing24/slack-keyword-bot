from ..domain import model
from .unit_of_work import AbstractUnitOfWork, R


def subscribe(uow: AbstractUnitOfWork[R], channel_name: str, subscriber: str, word: str) -> None:
    with uow:
        channel = uow.channels.get(model.ChannelName(channel_name))
        if not channel:
            channel = model.Channel(model.ChannelName(channel_name))
            uow.channels.add(channel)
        channel.keywords.add(model.Keyword(model.ChannelName(channel_name), model.User(subscriber), model.Word(word)))
        uow.commit()


def list_subscribers(uow: AbstractUnitOfWork[R], channel_name: str, author: str, text: str) -> set[str]:
    with uow:
        channel = uow.channels.get(model.ChannelName(channel_name))
        if not channel:
            raise ValueError("Unknown channel")
        message = model.Message(model.ChannelName(channel_name), model.User(author), model.Text(text))
        return set(channel.get_subscribers(message))


def list_subscriptions(uow: AbstractUnitOfWork[R], channel_name: str, subscriber: str) -> set[str]:
    with uow:
        channel = uow.channels.get(model.ChannelName(channel_name))
        if not channel:
            raise ValueError("Unknown channel")
        return {k.word for k in channel.keywords if k.subscriber == model.User(subscriber) and not k.unsubscribed}


def unsubscribe(uow: AbstractUnitOfWork[R], channel_name: str, subscriber: str, word: str) -> None:
    with uow:
        channel = uow.channels.get(model.ChannelName(channel_name))
        if not channel:
            raise ValueError("Unknown channel")
        try:
            keyword = next(
                k for k in channel.keywords if k.subscriber == model.User(subscriber) and k.word == model.Word(word)
            )
        except StopIteration:
            raise ValueError("Unknown keyword")
        keyword.unsubscribed = True
        uow.commit()

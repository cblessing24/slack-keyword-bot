from ..domain import model
from .unit_of_work import AbstractUnitOfWork, R


def add_keyword(uow: AbstractUnitOfWork[R], channel_name: str, user: str, word: str) -> None:
    with uow:
        channel = uow.channels.get(model.ChannelName(channel_name))
        if not channel:
            channel = model.Channel(model.ChannelName(channel_name))
            uow.channels.add(channel)
        channel.keywords.append(model.Keyword(model.ChannelName(channel_name), model.User(user), model.Word(word)))
        uow.commit()


def get_subscribers(uow: AbstractUnitOfWork[R], channel_name: str, author: str, text: str) -> set[str]:
    with uow:
        channel = uow.channels.get(model.ChannelName(channel_name))
        if not channel:
            return set()
        message = model.Message(model.ChannelName(channel_name), model.User(author), model.Text(text))
        return set(model.get_subscribers(message, channel.keywords))


def list_keywords(uow: AbstractUnitOfWork[R], channel_name: str, subscriber: str) -> set[str]:
    with uow:
        channel = uow.channels.get(model.ChannelName(channel_name))
        if not channel:
            return set()
        return {k.word for k in channel.keywords if k.subscriber == model.User(subscriber) and k.active}


def deactivate_keyword(uow: AbstractUnitOfWork[R], channel_name: str, subscriber: str, word: str) -> None:
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
        keyword.active = False
        uow.commit()

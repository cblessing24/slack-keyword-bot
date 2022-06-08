from ..domain import commands, model
from .unit_of_work import AbstractUnitOfWork, R


def subscribe(command: commands.Subscribe, uow: AbstractUnitOfWork[R]) -> None:
    with uow:
        channel = uow.channels.get(model.ChannelName(command.channel_name))
        if not channel:
            channel = model.Channel(model.ChannelName(command.channel_name))
            uow.channels.add(channel)
        subscription = model.Subscription(
            model.ChannelName(command.channel_name), model.User(command.subscriber), model.Keyword(command.keyword)
        )
        channel.subscribe(subscription)
        uow.commit()


def list_subscribers(command: commands.ListSubscribers, uow: AbstractUnitOfWork[R]) -> set[str]:
    with uow:
        channel = uow.channels.get(model.ChannelName(command.channel_name))
        if not channel:
            raise ValueError("Unknown channel")
        message = model.Message(
            model.ChannelName(command.channel_name), model.User(command.author), model.Text(command.text)
        )
        return set(channel.find_subscribed(message))


def list_subscriptions(command: commands.ListSubscriptions, uow: AbstractUnitOfWork[R]) -> set[str]:
    with uow:
        channel = uow.channels.get(model.ChannelName(command.channel_name))
        if not channel:
            raise ValueError("Unknown channel")
        return {s.keyword for s in channel.subscriptions if s.subscriber == model.User(command.subscriber)}


def unsubscribe(command: commands.Unsubscribe, uow: AbstractUnitOfWork[R]) -> None:
    with uow:
        channel = uow.channels.get(model.ChannelName(command.channel_name))
        if not channel:
            raise ValueError("Unknown channel")
        try:
            subscription = next(
                s
                for s in channel.subscriptions
                if s.subscriber == model.User(command.subscriber) and s.keyword == model.Keyword(command.keyword)
            )
        except StopIteration:
            raise ValueError("Unknown subscription")
        channel.subscriptions.remove(subscription)
        uow.commit()

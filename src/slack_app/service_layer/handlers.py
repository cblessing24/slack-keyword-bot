from collections.abc import ItemsView
from typing import Any, Generic, Protocol, Type, TypeVar, cast

from ..domain import commands, events, model
from ..domain.commands import Command
from ..domain.events import Event
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


C = TypeVar("C", bound=commands.Command, contravariant=True)


class CommandHandler(Protocol, Generic[C]):
    def __call__(self, command: C, uow: AbstractUnitOfWork[R]) -> Any:
        ...


class CommandHandlerMap(Protocol):
    def __getitem__(self, command: Type[C]) -> CommandHandler[C]:
        """Return the appropriate command handler for the given command."""

    def items(self) -> ItemsView[Type[Command], CommandHandler[Command]]:
        """Return a view of the command handlers, keyed by command type."""


COMMAND_HANDLERS = cast(
    CommandHandlerMap,
    {
        commands.Subscribe: subscribe,
        commands.ListSubscriptions: list_subscriptions,
        commands.ListSubscribers: list_subscribers,
        commands.Unsubscribe: unsubscribe,
    },
)


E = TypeVar("E", bound=events.Event, contravariant=True)


class EventHandler(Protocol, Generic[E]):
    def __call__(self, event: E, uow: AbstractUnitOfWork[R]) -> None:
        ...


class EventHandlerMap(Protocol):
    def __getitem__(self, event: Type[E]) -> list[EventHandler[E]]:
        """Return the appropriate list of event handlers for the given event."""

    def items(self) -> ItemsView[Type[Event], list[EventHandler[Event]]]:
        """Return a view of the event handlers, keyed by event type."""


EVENT_HANDLERS = cast(EventHandlerMap, {events.Subscribed: [], events.AlreadySubscribed: []})

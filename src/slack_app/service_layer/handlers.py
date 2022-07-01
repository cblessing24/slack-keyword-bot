from collections.abc import ItemsView
from typing import Protocol, Type, TypeVar, Union, cast

from ..adapters.notifications import AbstractNotifications
from ..domain import commands, events, model
from ..domain.commands import Command
from ..domain.events import Event
from .unit_of_work import AbstractUnitOfWork, R, SQLAlchemyUnitOfWork


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


def find_mentions(command: commands.FindMentions, uow: AbstractUnitOfWork[R]) -> None:
    with uow:
        channel = uow.channels.get(model.ChannelName(command.channel_name))
        if not channel:
            raise ValueError("Unknown channel")
        message = model.Message(
            model.ChannelName(command.channel_name), model.User(command.author), model.Text(command.text)
        )
        channel.find_subscribed(message)


def unsubscribe(command: commands.Unsubscribe, uow: AbstractUnitOfWork[R]) -> None:
    with uow:
        channel = uow.channels.get(model.ChannelName(command.channel_name))
        if not channel:
            raise ValueError("Unknown channel")
        subscription = model.Subscription(
            model.ChannelName(command.channel_name), model.User(command.subscriber), model.Keyword(command.keyword)
        )
        channel.unsubscribe(subscription)
        uow.commit()


Message = Union[commands.Command, events.Event]


def send_subscribed_notification(event: events.Subscribed, notifications: AbstractNotifications) -> None:
    notifications.respond(f"You will be notified if '{event.keyword}' is mentioned in <#{event.channel_name}>")


def send_already_subscribed_notification(event: events.AlreadySubscribed, notifications: AbstractNotifications) -> None:
    notifications.respond(f"You are already subscribed to '{event.keyword}' in <#{event.channel_name}>")


def send_unsubscribed_notification(event: events.Unsubscribed, notifications: AbstractNotifications) -> None:
    notifications.respond(
        f"You will be no longer notified if '{event.keyword}' is mentioned in <#{event.channel_name}>"
    )


def send_unknown_subscription_notification(
    event: events.UnknownSubscription, notifications: AbstractNotifications
) -> None:
    notifications.respond(f"You are not subscribed to '{event.keyword}' in <#{event.channel_name}>")


def send_mentioned_notification(event: events.Mentioned, notifications: AbstractNotifications) -> None:
    message = f"<@{event.author}> mentioned '{event.keyword}' in <#{event.channel_name}>:\n> "
    message += "\n> ".join(event.text.split("\n"))
    notifications.send(event.subscriber, message)


def add_subscription_to_read_model(event: events.Subscribed, uow: SQLAlchemyUnitOfWork) -> None:
    with uow:
        uow.session.execute(
            """
            INSERT INTO subscription_view (channel_name, subscriber, keyword)
            VALUES (:channel_name, :subscriber, :keyword)
            """,
            {"channel_name": event.channel_name, "subscriber": event.subscriber, "keyword": event.keyword},
        )
        uow.commit()


def remove_subscription_from_read_model(event: events.Unsubscribed, uow: SQLAlchemyUnitOfWork) -> None:
    with uow:
        uow.session.execute(
            """
            DELETE FROM subscription_view
            WHERE channel_name = :channel_name AND subscriber = :subscriber AND keyword = :keyword
            """,
            {"channel_name": event.channel_name, "subscriber": event.subscriber, "keyword": event.keyword},
        )
        uow.commit()


M = TypeVar("M", bound=Message, contravariant=True)


class MessageHandler(Protocol[M]):
    def __call__(self, message: M) -> Any:
        ...


C = TypeVar("C", bound=commands.Command, contravariant=True)


class CommandHandlerMap(Protocol):
    def __getitem__(self, command: Type[C]) -> MessageHandler[C]:
        """Return the appropriate command handler for the given command."""

    def items(self) -> ItemsView[Type[Command], MessageHandler[Command]]:
        """Return a view of the command handlers, keyed by command type."""


COMMAND_HANDLERS = cast(
    CommandHandlerMap,
    {
        commands.Subscribe: subscribe,
        commands.FindMentions: find_mentions,
        commands.Unsubscribe: unsubscribe,
    },
)


E = TypeVar("E", bound=events.Event, contravariant=True)


class EventHandlerMap(Protocol):
    def __getitem__(self, event: Type[E]) -> list[MessageHandler[E]]:
        """Return the appropriate list of event handlers for the given event."""

    def items(self) -> ItemsView[Type[Event], list[MessageHandler[Event]]]:
        """Return a view of the event handlers, keyed by event type."""


EVENT_HANDLERS = cast(
    EventHandlerMap,
    {
        events.Subscribed: [send_subscribed_notification, add_subscription_to_read_model],
        events.Unsubscribed: [send_unsubscribed_notification, remove_subscription_from_read_model],
        events.UnknownSubscription: [send_unknown_subscription_notification],
        events.AlreadySubscribed: [send_already_subscribed_notification],
        events.Mentioned: [send_mentioned_notification],
    },
)

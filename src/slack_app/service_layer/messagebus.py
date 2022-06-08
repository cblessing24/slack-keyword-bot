import logging
from typing import Any, Generic, Protocol, Type, TypeVar, cast

from ..domain import commands, events
from . import handlers, unit_of_work

logger = logging.getLogger(__name__)

Message = events.Event | commands.Command


def handle(message: Message, uow: unit_of_work.AbstractUnitOfWork[unit_of_work.R]) -> list[Any]:
    results: list[Any] = []
    queue = [message]
    while queue:
        message = queue.pop(0)
        if isinstance(message, events.Event):
            handle_event(message, queue, uow)
        elif isinstance(message, commands.Command):
            cmd_result = handle_command(message, queue, uow)
            results.append(cmd_result)
        else:
            raise TypeError(f"Unknown message type: {type(message)}")
    return results


def handle_event(
    event: events.Event, queue: list[Message], uow: unit_of_work.AbstractUnitOfWork[unit_of_work.R]
) -> None:
    for handler in EVENT_HANDLERS[type(event)]:
        logger.debug(f"Handling event {event!r} with handler {handler!r}")
        try:
            handler(event, uow=uow)
            queue.extend(uow.collect_new_events())
        except Exception:
            logger.exception(f"Exception handling event {event!r}")
            continue


def handle_command(
    command: commands.Command, queue: list[Message], uow: unit_of_work.AbstractUnitOfWork[unit_of_work.R]
) -> Any:
    logger.debug(f"Handling command {command!r}")
    try:
        handler = COMMAND_HANDLERS[type(command)]
        result = handler(command, uow=uow)
        queue.extend(uow.collect_new_events())
        return result
    except Exception:
        logger.exception(f"Exception handling command {command!r}")
        raise


C = TypeVar("C", bound=commands.Command, contravariant=True)


class CommandHandler(Protocol, Generic[C]):
    def __call__(self, command: C, uow: unit_of_work.AbstractUnitOfWork[unit_of_work.R]) -> Any:
        ...


class CommandHandlerMap(Protocol):
    def __getitem__(self, command: Type[C]) -> CommandHandler[C]:
        """Returns the appropriate command handler for the given command."""


COMMAND_HANDLERS = cast(
    CommandHandlerMap,
    {
        commands.Subscribe: handlers.subscribe,
        commands.ListSubscriptions: handlers.list_subscriptions,
        commands.ListSubscribers: handlers.list_subscribers,
        commands.Unsubscribe: handlers.unsubscribe,
    },
)


E = TypeVar("E", bound=events.Event, contravariant=True)


class EventHandler(Protocol, Generic[E]):
    def __call__(self, event: E, uow: unit_of_work.AbstractUnitOfWork[unit_of_work.R]) -> None:
        ...


class EventHandlerMap(Protocol):
    def __getitem__(self, event: Type[E]) -> list[EventHandler[E]]:
        """Returns the appropriate list of event handlers for the given event."""


EVENT_HANDLERS = cast(EventHandlerMap, {events.AlreadySubscribed: []})

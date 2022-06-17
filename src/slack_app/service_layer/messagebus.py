from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from ..domain import commands, events
from .unit_of_work import AbstractUnitOfWork

if TYPE_CHECKING:
    from .handlers import CommandHandlerMap, EventHandlerMap

logger = logging.getLogger(__name__)

Message = events.Event | commands.Command


U = TypeVar("U", bound=AbstractUnitOfWork[Any])


class MessageBus(Generic[U]):
    def __init__(
        self,
        uow: U,
        event_handlers: EventHandlerMap,
        command_handlers: CommandHandlerMap,
    ) -> None:
        self.uow = uow
        self.event_handlers = event_handlers
        self.command_handlers = command_handlers

    def handle(self, message: Message) -> list[Any]:
        results: list[Any] = []
        queue = [message]
        while queue:
            message = queue.pop(0)
            if isinstance(message, events.Event):
                self.handle_event(message, queue)
            elif isinstance(message, commands.Command):
                cmd_result = self.handle_command(message, queue)
                results.append(cmd_result)
            else:
                raise TypeError(f"Unknown message type: {type(message)}")
        return results

    def handle_event(self, event: events.Event, queue: list[Message]) -> None:
        for handler in self.event_handlers[type(event)]:
            logger.debug(f"Handling event {event!r} with handler {handler!r}")
            try:
                handler(event)
                queue.extend(self.uow.collect_new_events())
            except Exception:
                logger.exception(f"Exception handling event {event!r}")
                continue

    def handle_command(self, command: commands.Command, queue: list[Message]) -> Any:
        logger.debug(f"Handling command {command!r}")
        try:
            handler = self.command_handlers[type(command)]
            result = handler(command)
            queue.extend(self.uow.collect_new_events())
            return result
        except Exception:
            logger.exception(f"Exception handling command {command!r}")
            raise

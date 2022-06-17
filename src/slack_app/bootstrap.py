import functools
import inspect
from typing import Mapping, Optional, cast

from .adapters import orm
from .adapters.notifications import AbstractNotifications, SlackNotifications
from .service_layer.handlers import (
    COMMAND_HANDLERS,
    EVENT_HANDLERS,
    CommandHandlerMap,
    EventHandlerMap,
    M,
    MessageHandler,
)
from .service_layer.messagebus import MessageBus, U


def bootstrap(
    uow: U, *, start_mappers: bool = True, notifications: Optional[AbstractNotifications] = None
) -> MessageBus[U]:
    if start_mappers:
        orm.start_mappers()

    if notifications is None:
        notifications = SlackNotifications()

    dependencies = {"uow": uow, "notifications": notifications}
    injected_command_handlers = cast(
        CommandHandlerMap,
        {
            command_type: inject_dependencies(handler, dependencies)
            for command_type, handler in COMMAND_HANDLERS.items()
        },
    )
    injected_event_handlers = cast(
        EventHandlerMap,
        {
            event_type: [inject_dependencies(handler, dependencies) for handler in event_handlers]
            for event_type, event_handlers in EVENT_HANDLERS.items()
        },
    )
    return cast(
        MessageBus[U],
        MessageBus(uow, event_handlers=injected_event_handlers, command_handlers=injected_command_handlers),
    )


def inject_dependencies(handler: MessageHandler[M], dependencies: Mapping[str, object]) -> MessageHandler[M]:
    params = inspect.signature(handler).parameters
    deps = {name: dependency for name, dependency in dependencies.items() if name in params}
    return functools.partial(handler, **deps)

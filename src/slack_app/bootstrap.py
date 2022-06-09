from typing import Optional, overload

from .adapters import orm
from .service_layer.handlers import COMMAND_HANDLERS, EVENT_HANDLERS
from .service_layer.messagebus import MessageBus, U
from .service_layer.unit_of_work import SQLAlchemyUnitOfWork


@overload
def bootstrap(*, start_mappers: bool = ...) -> MessageBus[SQLAlchemyUnitOfWork]:
    ...


@overload
def bootstrap(*, start_mappers: bool = ..., uow: U = ...) -> MessageBus[U]:
    ...


def bootstrap(
    *, start_mappers: bool = True, uow: Optional[U] = None
) -> MessageBus[U] | MessageBus[SQLAlchemyUnitOfWork]:
    if start_mappers:
        orm.start_mappers()
    if not uow:
        return MessageBus(SQLAlchemyUnitOfWork(), event_handlers=EVENT_HANDLERS, command_handlers=COMMAND_HANDLERS)
    return MessageBus(uow, event_handlers=EVENT_HANDLERS, command_handlers=COMMAND_HANDLERS)

from typing import Set

from ..domain import model
from .unit_of_work import AbstractUnitOfWork, R


def add_keyword(uow: AbstractUnitOfWork[R], channel: str, user: str, word: str) -> None:
    with uow:
        uow.keywords.add(model.Keyword(model.Channel(channel), model.User(user), model.Word(word)))
        uow.commit()


def get_subscribers(uow: AbstractUnitOfWork[R], channel: str, author: str, text: str) -> Set[str]:
    keywords = uow.keywords.get(model.Channel(channel))
    message = model.Message(model.Channel(channel), model.User(author), model.Text(text))
    return set(model.get_subscribers(message, keywords))


def list_keywords(uow: AbstractUnitOfWork[R], channel: str, subscriber: str) -> Set[str]:
    keywords = uow.keywords.get(model.Channel(channel))
    return {k.word for k in keywords if k.subscriber == model.User(subscriber)}

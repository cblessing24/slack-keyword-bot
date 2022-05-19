from typing import Set

from sqlalchemy.orm.session import Session

from ..adapters.repository import AbstractRepository
from ..domain import model


def add_keyword(repo: AbstractRepository, session: Session, channel: str, user: str, word: str) -> None:
    repo.add(model.Keyword(model.Channel(channel), model.User(user), model.Word(word)))
    session.commit()


def get_subscribers(repo: AbstractRepository, channel: str, author: str, text: str) -> Set[str]:
    keywords = repo.get(model.Channel(channel))
    message = model.Message(model.Channel(channel), model.User(author), model.Text(text))
    return {k.subscriber for k in keywords if k in message}


def list_keywords(repo: AbstractRepository, channel: str, subscriber: str) -> Set[str]:
    keywords = repo.get(model.Channel(channel))
    return {k.word for k in keywords if k.subscriber == model.User(subscriber)}

from typing import Set

from sqlalchemy.orm.session import Session

from ..adapters.repository import AbstractRepository
from ..domain.model import Channel, Keyword, Message, Text, User, Word


def add_keyword(repo: AbstractRepository, session: Session, channel: str, user: str, word: str) -> None:
    repo.add(Keyword(Channel(channel), User(user), Word(word)))
    session.commit()


def get_subscribers(repo: AbstractRepository, channel: str, author: str, text: str) -> Set[str]:
    keywords = repo.get(Channel(channel))
    message = Message(Channel(channel), User(author), Text(text))
    return {k.subscriber for k in keywords if k in message}


def list_keywords(repo: AbstractRepository, channel: str, subscriber: str) -> Set[str]:
    keywords = repo.get(Channel(channel))
    return {k.word for k in keywords if k.subscriber == User(subscriber)}

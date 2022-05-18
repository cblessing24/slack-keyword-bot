from typing import Set

from sqlalchemy.orm.session import Session

from ..adapters.repository import AbstractRepository
from ..domain.model import Channel, Keyword, Message, User, Word


def add_keyword(repo: AbstractRepository, session: Session, channel: str, user: str, word: str) -> None:
    repo.add(Keyword(Channel(channel), User(user), Word(word)))
    session.commit()


def get_subscribers(repo: AbstractRepository, message: Message) -> Set[User]:
    keywords = repo.get(message.channel)
    return {k.user for k in keywords if k in message}

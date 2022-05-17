from typing import Set

from sqlalchemy.orm.session import Session

from ..adapters.repository import AbstractRepository
from ..domain.model import Keyword, Message, User


def add_keyword(repo: AbstractRepository, session: Session, keyword: Keyword) -> None:
    repo.add(keyword)
    session.commit()


def get_subscribers(repo: AbstractRepository, message: Message) -> Set[User]:
    keywords = repo.get(message.channel)
    return {k.user for k in keywords if k in message}

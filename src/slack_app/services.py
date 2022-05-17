from sqlalchemy.orm.session import Session

from .model import Keyword
from .repository import AbstractRepository


def add_keyword(repo: AbstractRepository, session: Session, keyword: Keyword) -> None:
    repo.add(keyword)
    session.commit()

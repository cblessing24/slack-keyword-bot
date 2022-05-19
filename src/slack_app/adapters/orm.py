from sqlalchemy import Column, Integer, String, Table
from sqlalchemy.orm import registry

from ..domain.model import Keyword

mapper_registry = registry()
metadata = mapper_registry.metadata

keyword = Table(
    "keyword",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("channel", String(255)),
    Column("subscriber", String(255)),
    Column("word", String(255)),
)


def start_mappers() -> None:
    mapper_registry.map_imperatively(Keyword, keyword)

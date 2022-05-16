from sqlalchemy import Column, Integer, MetaData, String, Table
from sqlalchemy.orm import registry

from .model import Keyword

mapper_registry = registry()
metadata = mapper_registry.metadata

keyword = Table(
    "keyword",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("channel", String(255)),
    Column("user", String(255)),
    Column("word", String(255)),
)


def start_mappers() -> None:
    mapper_registry.map_imperatively(Keyword, keyword)

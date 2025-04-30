from sqlalchemy import Column, ForeignKey, Integer, Table

from api.core.database import table_registry

posts_tags = Table(
    'posts_tags',
    table_registry.metadata,
    Column('post_id', Integer, ForeignKey('posts.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True),
)

from api.models.post import Post
from api.repositories.base_repository import BaseRepository


class PostRespository(BaseRepository[Post]):
    model = Post

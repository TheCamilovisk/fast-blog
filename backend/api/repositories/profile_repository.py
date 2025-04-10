from api.models.profile import Profile
from api.repositories.base_repository import BaseRepository


class ProfileRepository(BaseRepository[Profile]):
    model = Profile

    @classmethod
    def get_by_user_id(cls, session, user_id: int) -> Profile | None:
        return session.scalar(
            cls.model.select().filter(cls.model.user_id == user_id)
        )

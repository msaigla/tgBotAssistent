from sqlalchemy import select

from bot.db.repos.base import BaseRepository
from bot.db.models import User
from bot.db.repos.mappers.mappers import UserDataMapper

class UsersRepository(BaseRepository):
    model = User
    mapper = UserDataMapper
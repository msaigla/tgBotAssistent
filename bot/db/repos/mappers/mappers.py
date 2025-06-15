from bot.db.models import UsersOrm, UsersPermissionOrm
from bot.db.repos.mappers.base import DataMapper
from bot.db.schemas.users import User, UserPermission


class UserDataMapper(DataMapper):
    db_model = UsersOrm
    schema = User


class UserPermMapper(DataMapper):
    db_model = UsersPermissionOrm
    schema = UserPermission
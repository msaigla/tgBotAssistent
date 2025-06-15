from sqlalchemy import select, delete, insert, update
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import sessionmaker

from bot.db.models import UsersOrm, ChatHistoriesOrm, UsersPermissionOrm
from bot.db.repos.mappers.mappers import UserDataMapper, UserPermMapper
from bot.db.schemas.users import UserAddDB, UserPatch, User


async def get_all_user(session_maker: sessionmaker):
    async with session_maker() as session:
        async with session.begin():
            query = select(UsersOrm)
            result = await session.execute(query)
            return [UserDataMapper.map_to_domain_entity(model) for model in result.scalars().all()]


async def get_user(chat_id, session_maker: sessionmaker) -> User | None:
    async with session_maker() as session:
        query = select(UsersOrm).filter_by(chat_id=chat_id)
        result = await session.execute(query)
        model = result.scalars().one_or_none()
        if model is None:
            return None
        return UserDataMapper.map_to_domain_entity(model)


async def get_user_perm(login, session_maker: sessionmaker):
    async with session_maker() as session:
        query = select(UsersPermissionOrm).filter_by(login=login)
        result = await session.execute(query)
        model = result.scalars().one_or_none()
        if model is None:
            return None
        return UserPermMapper.map_to_domain_entity(model)


async def delete_user(chat_id, session_maker: sessionmaker):
    async with session_maker() as session:
        async with session.begin():
            query = delete(UsersOrm).filter_by(chat_id=chat_id)
            await session.execute(query)
            query = delete(ChatHistoriesOrm).filter_by(chat_id=chat_id)
            await session.execute(query)


async def create_user(data: UserAddDB, session_maker: sessionmaker) -> None:
    async with session_maker() as session:
        async with session.begin():
            user = insert(UsersOrm).values(**data.model_dump()).returning(UsersOrm)
            result = await session.execute(user)
            model = result.scalars().one()
            return UserDataMapper.map_to_domain_entity(model)


async def add_history(chat_id, role, message, session_maker: sessionmaker) -> None:
    async with session_maker() as session:
        async with session.begin():
            chat_history = ChatHistoriesOrm(
                chat_id=chat_id,
                role=role,
                message=message
            )
            try:
                session.add(chat_history)
            except ProgrammingError as e:
                # TODO: add log
                pass


async def get_history(chat_id, session_maker: sessionmaker) -> list:
    async with session_maker() as session:
        async with session.begin():
            result = await session.execute(
                select(ChatHistoriesOrm).filter(ChatHistoriesOrm.chat_id == chat_id)  # type: ignore
            )
            results = result.scalars().all()
            vals = []
            for result in results:
                vals.append({
                    'role': result.role,
                    'content': result.message,
                })
            print(vals)
            return vals


async def update_user(chat_id, data: UserPatch, session_maker: sessionmaker) -> None:
    async with session_maker() as session:
        async with session.begin():
            user = update(UsersOrm).filter_by(chat_id=chat_id).values(**data.model_dump()).returning(UsersOrm)
            result = await session.execute(user)
            model = result.scalars().one()
            return UserDataMapper.map_to_domain_entity(model)


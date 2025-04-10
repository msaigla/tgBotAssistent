from sqlalchemy import select, delete
from sqlalchemy.exc import ProgrammingError, NoResultFound
from sqlalchemy.orm import sessionmaker, selectinload

from bot.db.models import User, ChatHistory


async def get_all_user(session_maker: sessionmaker):
    async with session_maker() as session:
        async with session.begin():
            queries = await session.execute(select(User).select_from(User))
            res = queries.scalars().all()
            results = []
            for query in res:
                results.append(
                    {
                        'chat_id': query.chat_id,
                        'username': query.username,
                        'gender': query.gender,
                        'city': query.city,
                        'where_practicing': query.where_practicing,
                        'were_clients': query.were_clients,
                        'massage_technique': query.massage_technique,
                        'using_social': query.using_social,
                        'lang': query.lang,
                        'row_sheet': query.row_sheet,
                        'number_of_days': query.number_of_days
                    }
                )
            try:
                return results
            except:
                return None


async def get_user(chat_id, session_maker: sessionmaker):
    async with session_maker() as session:
        result = await session.execute(
            select(User).filter(User.chat_id == chat_id)  # type: ignore
        )
        try:
            res = result.one_or_none()
            print(res)
            return res
        except:
            return None


async def delete_user(chat_id, session_maker: sessionmaker):
    async with session_maker() as session:
        async with session.begin():
            query = delete(User).where(User.chat_id == chat_id)
            await session.execute(query)
            query = delete(ChatHistory).where(ChatHistory.chat_id == chat_id)
            await session.execute(query)


async def create_user(user: list, row: str, session_maker: sessionmaker) -> None:
    async with session_maker() as session:
        async with session.begin():
            user = User(
                chat_id=user[0],
                username=user[1],
                gender=user[2],
                city=user[3],
                where_practicing=user[4],
                were_clients=user[5],
                massage_technique=user[6],
                using_social=user[7],
                lang='ru',
                row_sheet=row,
                number_of_days=0
            )
            try:
                session.add(user)
            except ProgrammingError as e:
                # TODO: add log
                pass


async def add_history(chat_id, role, message, session_maker: sessionmaker) -> None:
    async with session_maker() as session:
        async with session.begin():
            chat_history = ChatHistory(
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
                select(ChatHistory).filter(ChatHistory.chat_id == chat_id)  # type: ignore
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


async def update_day(chat_id, day: int, session_maker: sessionmaker) -> None:
    async with session_maker() as session:
        async with session.begin():
            user = await session.get(User, chat_id)
            user.number_of_days = day
            await session.commit()


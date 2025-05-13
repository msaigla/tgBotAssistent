import enum
from datetime import datetime
from typing import Annotated

from sqlalchemy import text, BigInteger, MetaData, String
from sqlalchemy.orm import Mapped, mapped_column

from bot.db.base import BaseModel

metadata_obj = MetaData()

created_at = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
updated_at = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"),
                                               onupdate=datetime.utcnow)]


class User(BaseModel):
    __tablename__ = 'users'

    chat_id = mapped_column(BigInteger, nullable=False, unique=True, primary_key=True)
    username: Mapped[str] = mapped_column(String(32), unique=False, nullable=True)
    gender: Mapped[str] = mapped_column(String(32), unique=False, default='MAN')
    city: Mapped[str] = mapped_column(String(128), unique=False, nullable=True)
    where_practicing: Mapped[str] = mapped_column(String(128), unique=False, nullable=True)
    were_clients: Mapped[str] = mapped_column(String(128), unique=False, nullable=True)
    massage_technique: Mapped[str] = mapped_column(String(128), unique=False, nullable=True)
    using_social: Mapped[str] = mapped_column(String(128), unique=False, nullable=True)
    lang: Mapped[str] = mapped_column(String(32), unique=False, default='ru')
    row_sheet: Mapped[str] = mapped_column(String(32), unique=False, nullable=True)
    number_of_days: Mapped[int] = mapped_column(unique=False, default=0)
    create_at: Mapped[created_at]
    update_at: Mapped[updated_at]

    @property
    def stats(self) -> str:
        """
        :return:
        """
        return ""

    def __str__(self) -> str:
        return f'<Users:{self.chat_id}>'

    def __repr__(self):
        return self.__str__()


class ChatHistory(BaseModel):
    __tablename__ = 'chat_histories'
    id = mapped_column(BigInteger, primary_key=True)
    chat_id = mapped_column(BigInteger)
    role: Mapped[str] = mapped_column(String(32), unique=False, nullable=True)
    message: Mapped[str]
    create_at: Mapped[created_at]

    @property
    def stats(self) -> str:
        """
        :return:
        """
        return ""

    def __str__(self) -> str:
        return f'<ChatHistory:{self.chat_id}>'

    def __repr__(self):
        return self.__str__()

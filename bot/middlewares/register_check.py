#  Copyright (c) 2022.

from typing import Callable, Dict, Any, Awaitable, Union

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from bot.db.requests import is_user_exists, create_user


class RegisterCheck(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any]
    ) -> Any:
        """ Сама функция для обработки вызова """
        # if event.web_app_data:
        #     return await handler(event, data)

        session_maker = data['session_maker']
        # redis = data['redis']
        # user = event.from_user
        #
        # # Получаем менеджер сессий из ключевых аргументов, переданных в start_polling()
        # if not await is_user_exists(user_id=event.from_user.id, session_maker=session_maker, redis=redis):
        #     print ("in func")
        #     await create_user(user_id=event.from_user.id,
        #                       username=event.from_user.username, session_maker=session_maker, locale=user.language_code)
            # await data['bot'].send_message(event.from_user.id, 'Ты успешно зарегистрирован(а)!')

        return await handler(event, data)
from aiogram import Router, types, F

from sqlalchemy.orm import sessionmaker

from bot.handlers.chat_GPT import gpt4
from bot.handlers.google_sheet_api import new_many_clients_user, new_fell_user
from bot.translations import _

router = Router()


@router.callback_query(F.data.startswith("many_clients_"))
async def many_clients_user(call: types.CallbackQuery, session_maker: sessionmaker) -> None:
    many_clients = call.data[13:]
    await call.message.edit_text(
        await _("MSG_QUESTION_MANY_CLIENTS", call.message.chat.id, session_maker) + "\n" +
        await _(many_clients, call.message.chat.id, session_maker)
    )
    await new_many_clients_user(call.message.chat.id, await _(many_clients, call.message.chat.id, session_maker))


@router.callback_query(F.data.startswith("fell_"))
async def fell_user(call: types.CallbackQuery, session_maker: sessionmaker) -> None:
    fell = call.data[5:]
    await call.message.edit_text(
        await _("MSG_QUESTION_FEEL", call.message.chat.id, session_maker) + "\n" +
        await _(fell, call.message.chat.id, session_maker)
    )
    await call.message.answer(
        await gpt4(
            "Я себя чувствую " + await _(fell, call.message.chat.id, session_maker),
            call.message.chat.id,
            session_maker
        )
    )
    await new_fell_user(call.message.chat.id, await _(fell, call.message.chat.id, session_maker))

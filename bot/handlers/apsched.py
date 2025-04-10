from aiogram import Bot, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm import sessionmaker

from bot.db.requests import get_all_user, update_day
from bot.translations import _


async def send_message_cron(bot: Bot, session_maker: sessionmaker):
    results = await get_all_user(session_maker=session_maker)
    print(results)
    for result in results:
        if result['number_of_days'] == 0:
            many_clients_markup = InlineKeyboardBuilder()
            many_clients_markup.row(
                types.InlineKeyboardButton(
                    text=await _("0", result['chat_id'], session_maker),
                    callback_data="many_clients_0"
                )
            )
            many_clients_markup.row(
                types.InlineKeyboardButton(
                    text=await _("1-2", result['chat_id'], session_maker),
                    callback_data="many_clients_1-2"
                )
            )
            many_clients_markup.row(
                types.InlineKeyboardButton(
                    text=await _("3-5", result['chat_id'], session_maker),
                    callback_data="many_clients_3-5"
                )
            )
            many_clients_markup.row(
                types.InlineKeyboardButton(
                    text=await _("6+", result['chat_id'], session_maker),
                    callback_data="many_clients_6+"
                )
            )
            await bot.send_message(
                result['chat_id'],
                await _("7_DAY_PASSED", result['chat_id'], session_maker),
            )
            await bot.send_message(
                result['chat_id'],
                await _("MSG_QUESTION_MANY_CLIENTS", result['chat_id'], session_maker),
                reply_markup=many_clients_markup.as_markup()
            )
            feel_markup = InlineKeyboardBuilder()
            feel_markup.row(
                types.InlineKeyboardButton(
                    text=await _("ASSUREDLY", result['chat_id'], session_maker),
                    callback_data="feel_ASSUREDLY"
                )
            )
            feel_markup.row(
                types.InlineKeyboardButton(
                    text=await _("NEED_SUPPORT", result['chat_id'], session_maker),
                    callback_data="feel_NEED_SUPPORT"
                )
            )
            feel_markup.row(
                types.InlineKeyboardButton(
                    text=await _("WANT_ADVICE", result['chat_id'], session_maker),
                    callback_data="feel_WANT_ADVICE"
                )
            )
            await bot.send_message(
                result['chat_id'],
                await _("MSG_QUESTION_FEEL", result['chat_id'], session_maker),
                reply_markup=feel_markup.as_markup()
            )
            await update_day(result['chat_id'], 0, session_maker)
        else:
            await update_day(result['chat_id'], result['number_of_days'] + 1, session_maker)
            hint_markup = InlineKeyboardBuilder()
            if result['gender'] == await _("MAN", result['chat_id'], session_maker):
                hint_markup.row(
                    types.InlineKeyboardButton(
                        text=await _("DID_MAN", result['chat_id'], session_maker),
                        callback_data="okey_DID_MAN"
                    )
                )
            else:
                hint_markup.row(
                    types.InlineKeyboardButton(
                        text=await _("DID_WOMEN", result['chat_id'], session_maker),
                        callback_data="okey_DID_WOMEN"
                    )
                )
            hint_markup.row(
                types.InlineKeyboardButton(
                    text=await _("DID_NOT", result['chat_id'], session_maker),
                    callback_data="hint_DID_NOT"
                )
            )
            hint_markup.row(
                types.InlineKeyboardButton(
                    text=await _("WANT_HINT", result['chat_id'], session_maker),
                    callback_data="hint_WANT_HINT"
                )
            )
            await bot.send_message(
                result['chat_id'],
                await _("MSG_QUESTION_HINT", result['chat_id'], session_maker),
                reply_markup=hint_markup.as_markup()
            )

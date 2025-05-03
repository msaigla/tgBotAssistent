import os

from datetime import datetime

from aiogram import Router, types, F, Bot
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from sqlalchemy.orm import sessionmaker

from bot.db.requests import create_user, get_user, update_day, delete_user
from bot.handlers.chat_GPT import gpt4
from bot.structures.fsm_groups import CreateUserFSM
from bot.translations import _

from bot.handlers.google_sheet_api import add_new_user, new_many_clients_user, delete_user_from_sheet

router = Router()


@router.message(Command('clear_user'))
async def cmd_clear(message: types.Message, session_maker: sessionmaker, bot: Bot):
    msg = await message.answer(
        "очистка..."
    )
    await delete_user(message.chat.id, session_maker)
    await delete_user_from_sheet(message.chat.id)
    try:
        # Все сообщения, начиная с текущего и до первого (message_id = 0)
        for i in range(message.message_id, 0, -1):
            await bot.delete_message(
                chat_id=message.chat.id, message_id=i)
    except TelegramBadRequest as ex:
        # Если сообщение не найдено (уже удалено или не существует),
        # код ошибки будет "Bad Request: message to delete not found"
        if ex.message == "Bad Request: message to delete not found":
            print("Все сообщения удалены")
    # await message.answer(
    #     "очистка завершена! Для начала введите команду /start"
    # )
    await msg.delete()


@router.message(CommandStart())
async def cmd_start(message: types.Message, session_maker: sessionmaker, state: FSMContext) -> None:
    user = await get_user(message.chat.id, session_maker)
    if user is None:
        await message.answer(
            await _("START_MESSAGE", message.chat.id, session_maker)
        )
        await message.answer(
            await _("MSG_QUESTION_NAME", message.chat.id, session_maker)
        )
        await state.set_state(CreateUserFSM.name)
    else:
        await message.answer(
            "Вы уже зарегистрированы!"
        )
        await state.set_state(CreateUserFSM.finish)


@router.message(CreateUserFSM.name)
async def name_user(message: types.Message, state: FSMContext, session_maker: sessionmaker) -> None:
    await state.update_data(name=message.text)
    await state.set_state(CreateUserFSM.gender)
    gender_markup = InlineKeyboardBuilder()
    gender_markup.row(
        types.InlineKeyboardButton(
            text=await _("MAN", message.chat.id, session_maker),
            callback_data="gender_MAN"
        )
    )
    gender_markup.row(
        types.InlineKeyboardButton(
            text=await _("WOMEN", message.chat.id, session_maker),
            callback_data="gender_WOMEN"
        )
    )
    await message.answer(
        await _("MSG_QUESTION_GENDER", message.chat.id, session_maker),
        reply_markup=gender_markup.as_markup()
    )


@router.callback_query(F.data.startswith("gender_"), CreateUserFSM.gender)
async def gender_user(call: types.CallbackQuery, state: FSMContext, session_maker: sessionmaker) -> None:
    gender = call.data[7:]
    await state.update_data(gender=gender)
    await state.set_state(CreateUserFSM.city)
    await call.message.edit_text(
        await _("MSG_QUESTION_GENDER", call.message.chat.id, session_maker) + " " +
        await _(gender, call.message.chat.id, session_maker)
    )
    # await call.message.delete_reply_markup()
    await call.message.answer(
        await _("MSG_QUESTION_CITY", call.message.chat.id, session_maker)
    )


@router.message(CreateUserFSM.city)
async def city_user(message: types.Message, state: FSMContext, session_maker: sessionmaker) -> None:
    city = message.text
    await state.update_data(city=city)
    await state.set_state(CreateUserFSM.where_practicing)
    where_practicing_markup = InlineKeyboardBuilder()
    where_practicing_markup.row(
        types.InlineKeyboardButton(
            text=await _("HOUSE", message.chat.id, session_maker),
            callback_data="where_practicing_HOUSE"
        )
    )
    where_practicing_markup.row(
        types.InlineKeyboardButton(
            text=await _("DEPARTURE", message.chat.id, session_maker),
            callback_data="where_practicing_DEPARTURE"
        )
    )
    where_practicing_markup.row(
        types.InlineKeyboardButton(
            text=await _("OFFICE", message.chat.id, session_maker),
            callback_data="where_practicing_OFFICE"
        )
    )
    where_practicing_markup.row(
        types.InlineKeyboardButton(
            text=await _("NOWHERE", message.chat.id, session_maker),
            callback_data="where_practicing_NOWHERE"
        )
    )
    await message.answer(
        await _("MSG_PRACTICE", message.chat.id, session_maker),
        reply_markup=where_practicing_markup.as_markup()
    )


@router.callback_query(F.data.startswith("where_practicing_"), CreateUserFSM.where_practicing)
async def where_practicing_user(call: types.CallbackQuery, state: FSMContext, session_maker: sessionmaker) -> None:
    where_practicing = call.data[17:]
    await state.update_data(where_practicing=where_practicing)
    await state.set_state(CreateUserFSM.were_clients)
    await call.message.edit_text(
        await _("MSG_PRACTICE", call.message.chat.id, session_maker) + "\n" +
        await _(where_practicing, call.message.chat.id, session_maker),
    )
    were_clients_markup = InlineKeyboardBuilder()
    were_clients_markup.row(
        types.InlineKeyboardButton(
            text=await _("NO", call.message.chat.id, session_maker),
            callback_data="were_clients_NO"
        )
    )
    were_clients_markup.row(
        types.InlineKeyboardButton(
            text=await _("WERE_1-2", call.message.chat.id, session_maker),
            callback_data="were_clients_WERE_1-2"
        )
    )
    were_clients_markup.row(
        types.InlineKeyboardButton(
            text=await _("NO_REGULARLY", call.message.chat.id, session_maker),
            callback_data="were_clients_NO_REGULARLY"
        )
    )
    await call.message.answer(
        await _("MSG_QUESTION_CLIENTS", call.message.chat.id, session_maker),
        reply_markup=were_clients_markup.as_markup()
    )


@router.callback_query(F.data.startswith("were_clients_"), CreateUserFSM.were_clients)
async def were_clients_user(call: types.CallbackQuery, state: FSMContext, session_maker: sessionmaker) -> None:
    were_clients = call.data[13:]
    await state.update_data(were_clients=were_clients)
    await state.set_state(CreateUserFSM.massage_technique)
    await call.message.edit_text(
        await _("MSG_QUESTION_CLIENTS", call.message.chat.id, session_maker) + "\n" +
        await _(were_clients, call.message.chat.id, session_maker),
    )
    massage_technique_markup = InlineKeyboardBuilder()
    massage_technique_markup.row(
        types.InlineKeyboardButton(
            text=await _("FACE", call.message.chat.id, session_maker),
            callback_data="massage_technique_FACE"
        )
    )
    massage_technique_markup.row(
        types.InlineKeyboardButton(
            text=await _("BODY", call.message.chat.id, session_maker),
            callback_data="massage_technique_BODY"
        )
    )
    massage_technique_markup.row(
        types.InlineKeyboardButton(
            text=await _("FOOT", call.message.chat.id, session_maker),
            callback_data="massage_technique_FOOT"
        )
    )
    massage_technique_markup.row(
        types.InlineKeyboardButton(
            text=await _("LYMPHATIC", call.message.chat.id, session_maker),
            callback_data="massage_technique_LYMPHATIC"
        )
    )
    await call.message.answer(
        await _("MSG_QUESTION_TECHNIQUE", call.message.chat.id, session_maker),
        reply_markup=massage_technique_markup.as_markup()
    )


@router.callback_query(F.data.startswith("massage_technique_"), CreateUserFSM.massage_technique)
async def massage_technique_user(call: types.CallbackQuery, state: FSMContext, session_maker: sessionmaker) -> None:
    massage_technique = call.data[18:]
    await state.update_data(massage_technique=massage_technique)
    await state.set_state(CreateUserFSM.using_social)
    await call.message.edit_text(
        await _("MSG_QUESTION_TECHNIQUE", call.message.chat.id, session_maker) + "\n" +
        await _(massage_technique, call.message.chat.id, session_maker),
    )
    using_social_markup = InlineKeyboardBuilder()
    using_social_markup.row(
        types.InlineKeyboardButton(
            text=await _("GOOD", call.message.chat.id, session_maker),
            callback_data="using_social_GOOD"
        )
    )
    using_social_markup.row(
        types.InlineKeyboardButton(
            text=await _("LITTLE_BIG", call.message.chat.id, session_maker),
            callback_data="using_social_LITTLE_BIG"
        )
    )
    using_social_markup.row(
        types.InlineKeyboardButton(
            text=await _("WITHOUT_THEM", call.message.chat.id, session_maker),
            callback_data="using_social_WITHOUT_THEM"
        )
    )
    await call.message.answer(
        await _("MSG_QUESTION_SNW", call.message.chat.id, session_maker),
        reply_markup=using_social_markup.as_markup()
    )


@router.callback_query(F.data.startswith("using_social_"), CreateUserFSM.using_social)
async def using_social_user(call: types.CallbackQuery, state: FSMContext, session_maker: sessionmaker) -> None:
    using_social = call.data[13:]
    await state.update_data(using_social=using_social)
    data = await state.get_data()
    await state.set_state(CreateUserFSM.finish)
    results = [
        call.message.chat.id,
        data.get("name"),
        await _(data.get("gender"), call.message.chat.id, session_maker),
        data.get("city"),
        await _(data.get("where_practicing"), call.message.chat.id, session_maker),
        await _(data.get("were_clients"), call.message.chat.id, session_maker),
        await _(data.get("massage_technique"), call.message.chat.id, session_maker),
        await _(data.get("using_social"), call.message.chat.id, session_maker)
    ]
    await call.message.edit_text(
        await _("MSG_QUESTION_SNW", call.message.chat.id, session_maker) + "\n" +
        await _(using_social, call.message.chat.id, session_maker),
    )
    row = await add_new_user(results)
    await create_user(results, row, session_maker)
    await call.message.answer(
        await gpt4(
            ("Меня зовут {}. " +
             "Мой гендер {}. " +
             "Живу я в {}. " +
             "Я практикую массаж {}. " +
             "Клиентов у меня {}. " +
             "Я использую технику на {}" +
             "Мой уровень владения соцсетями - {}").format(
                data.get("name"),
                await _(data.get("gender"), call.message.chat.id, session_maker),
                data.get("city"),
                await _(data.get("where_practicing"), call.message.chat.id, session_maker),
                await _(data.get("were_clients"), call.message.chat.id, session_maker),
                await _(data.get("massage_technique"), call.message.chat.id, session_maker),
                await _(data.get("using_social"), call.message.chat.id, session_maker)
            ),
            call.message.chat.id,
            session_maker
        ),
        parse_mode=ParseMode.MARKDOWN,
    )


@router.callback_query(F.data.startswith("okey_DID_"))
async def did(call: types.CallbackQuery, session_maker: sessionmaker) -> None:
    DID = call.data[5:]
    await call.message.edit_text(
        await _("MSG_QUESTION_HINT", call.message.chat.id, session_maker) + "\n" +
        await _(DID, call.message.chat.id, session_maker)
    )
    msg = ""
    if DID == "DID_WOMEN" or "DID_MAN":
        msg = " Дай новое задание"
    await call.message.answer(
        await gpt4(
            ((await _(DID, call.message.chat.id, session_maker)) + msg),
            call.message.chat.id,
            session_maker
        ),
        parse_mode=ParseMode.MARKDOWN,
    )


@router.callback_query(F.data.startswith("hint_DID_NOT"))
async def did(call: types.CallbackQuery, session_maker: sessionmaker) -> None:
    hint = call.data[5:]
    await call.message.edit_text(
        await _("MSG_QUESTION_HINT", call.message.chat.id, session_maker) + "\n" +
        await _(hint, call.message.chat.id, session_maker)
    )
    await call.message.answer(
        await gpt4(
            await _(hint, call.message.chat.id, session_maker),
            call.message.chat.id,
            session_maker
        ),
        parse_mode=ParseMode.MARKDOWN,
    )


@router.callback_query(F.data.startswith("hint_WANT_HINT"))
async def did(call: types.CallbackQuery, session_maker: sessionmaker) -> None:
    hint = call.data[5:]
    await call.message.edit_text(
        await _("MSG_QUESTION_HINT", call.message.chat.id, session_maker) + "\n" +
        await _(hint, call.message.chat.id, session_maker)
    )
    # hint_markup = InlineKeyboardBuilder()
    # hint_markup.row(
    #     types.InlineKeyboardButton(
    #         text=await _("SCARY_SUGGEST", call.message.chat.id, session_maker),
    #         callback_data="problem_SCARY_SUGGEST"
    #     )
    # )
    # hint_markup.row(
    #     types.InlineKeyboardButton(
    #         text=await _("I_DO_NOT_WRITE", call.message.chat.id, session_maker),
    #         callback_data="problem_I_DO_NOT_WRITE"
    #     )
    # )
    # hint_markup.row(
    #     types.InlineKeyboardButton(
    #         text=await _("WANT_HINT", call.message.chat.id, session_maker),
    #         callback_data="problem_WANT_HINT"
    #     )
    # )
    # hint_markup.row(
    #     types.InlineKeyboardButton(
    #         text=await _("OTHER", call.message.chat.id, session_maker),
    #         callback_data="OTHER"
    #     )
    # )
    await call.message.answer(
        await gpt4(
            await _(hint, call.message.chat.id, session_maker),
            call.message.chat.id,
            session_maker
        ),
        parse_mode=ParseMode.MARKDOWN,
    )


@router.message(CreateUserFSM.finish)
async def message_gpt(message: types.Message, state: FSMContext, session_maker: sessionmaker) -> None:
    await message.answer(
        await gpt4(
            message.text,
            message.chat.id,
            session_maker
        ),
        parse_mode=ParseMode.MARKDOWN,
    )
    await state.set_state(CreateUserFSM.finish)


@router.message(F.text)
async def message_gpt(message: types.Message, state: FSMContext, session_maker: sessionmaker) -> None:
    user = await get_user(message.chat.id, session_maker)
    print('this')
    if user is not None:
        await message.answer(
            await gpt4(
                message.text,
                message.chat.id,
                session_maker
            ),
            parse_mode=ParseMode.MARKDOWN,
        )
        await state.set_state(CreateUserFSM.finish)
    else:
        await message.answer(
            "Выполните команду /start"
        )

import asyncio
import os

from datetime import datetime

import httpx
from aiogram.enums import ChatAction, ParseMode
from openai import AsyncOpenAI
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker

from bot.db.requests import add_history, get_history, get_user
from bot.translations import translations

load_dotenv()

if os.getenv('PROXY'):
    client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'),
                         http_client=httpx.AsyncClient(
                             proxy=os.getenv('PROXY'),
                             transport=httpx.HTTPTransport(local_address="0.0.0.0"),
                         ))
else:
    client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))


typing_speed = int(os.getenv('WRITE_SIMBOL'))


async def gpt4(question: str, chat_id, session_maker: sessionmaker):
    await add_history(chat_id, 'user', question, session_maker)
    user = await get_user(chat_id, session_maker)
    history = ([{"role": "developer", "content": translations['ru']["GPT_INSTRUCTION"].format(
        user.name,
        user.gender,
        user.city,
        user.massage_technique,
        user.where_practicing,
        user.using_social,
        user.were_clients,
    )}] +
               await get_history(chat_id, session_maker))
    if user.premium < datetime.date(datetime.now()):
        if user.trial > 0:
            completion = await client.chat.completions.create(
                # instructions=translations['ru']["GPT_INSTRUCTION"],
                model="gpt-4o",
                messages=history,
                temperature=0.7
            )
            await add_history(chat_id, "developer", completion.choices[0].message.content, session_maker)
            return f"_trial версия (осталось {user.trial} дней)_\n" + completion.choices[0].message.content
        else:
            return f"Срок действия вашей лицензии истёк!"
    else:
        completion = await client.chat.completions.create(
            # instructions=translations['ru']["GPT_INSTRUCTION"],
            model="gpt-4o",
            messages=history,
            temperature=0.7
        )
        await add_history(chat_id, "developer", completion.choices[0].message.content, session_maker)
        return completion.choices[0].message.content



async def write_response_gpt(message, question: str, session_maker: sessionmaker):
    response_text = await gpt4(
        question,
        message.chat.id,
        session_maker
    )

    # Длительность печати
    typing_duration = len(response_text) / typing_speed
    typing_duration = min(typing_duration, 10)  # Ограничим максимум, например, 10 сек

    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    await asyncio.sleep(typing_duration)
    await message.answer(
        response_text,
        parse_mode=ParseMode.MARKDOWN,
    )


async def translate_gpt(lang: str, text: str):
    question = "Переведи с ru на {}: {}".format(lang, text)
    response = await client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": str(question)
            }
        ],
        model="gpt-4o"
    )
    return response.choices[0].message.content

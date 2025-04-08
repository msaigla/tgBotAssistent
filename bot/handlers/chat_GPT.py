import os

import httpx
from openai import AsyncOpenAI
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker

from bot.db.requests import add_history, get_history
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


async def gpt4(question: str, chat_id, session_maker: sessionmaker):
    print(question)
    await add_history(chat_id, 'user', question, session_maker)
    history = ([{"role": "developer", "content": translations['ru']["GPT_INSTRUCTION"]}] +
               await get_history(chat_id, session_maker))
    completion = await client.chat.completions.create(
        # instructions=translations['ru']["GPT_INSTRUCTION"],
        model="gpt-4o",
        messages=history,
        temperature=0.7
    )
    await add_history(chat_id, "developer", completion.choices[0].message.content, session_maker)
    return completion.choices[0].message.content


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

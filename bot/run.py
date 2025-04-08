import asyncio
import logging
import os
import pathlib

from datetime import datetime

from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.redis import RedisStorage
from sqlalchemy.engine import URL

from bot.db.engine import create_async_engine, get_session_maker

from bot.handlers import apsched
from bot.handlers.main import router as router_main
from bot.handlers.day7 import router as router_day7

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.db.requests import redis


async def bot_start(logger: logging.Logger) -> None:
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=os.getenv('TG_TOKEN'))

    dp = Dispatcher(storage=RedisStorage(redis=redis))
    dp.include_router(router_main)
    dp.include_router(router_day7)

    await bot.delete_webhook()

    postgres_url = URL.create(
        "postgresql+asyncpg",
        username=os.getenv("DB_USER"),
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        password=os.getenv("DB_PASS"),
        port=os.getenv("DB_PORT")
    )

    async_engine = create_async_engine(postgres_url)
    session_maker = get_session_maker(async_engine)

    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(apsched.send_message_cron,
                      trigger='cron',
                      hour=int(os.getenv("AUTO_MESSAGE_HOUR")),
                      # minute=datetime.now().minute + 1,
                      start_date=datetime.now(),
                      kwargs={'bot': bot, 'session_maker': session_maker})
    scheduler.start()

    await dp.start_polling(bot,
                           session_maker=session_maker,
                           logger=logger,
                           redis=redis,
                           allowed_updates=dp.resolve_used_update_types())


def setup_env():
    """Настройка переменных окружения"""
    from dotenv import load_dotenv
    path = pathlib.Path(__file__).parent
    dotenv_path = path.joinpath('.env')
    if dotenv_path.exists():
        load_dotenv(dotenv_path)


def main():
    """Функция для запуска через poetry"""
    logger = logging.getLogger(__name__)
    try:
        setup_env()
        asyncio.run(bot_start(logger))
        logger.info('Bot started')
    except (KeyboardInterrupt, SystemExit):
        logger.info('Bot stopped')


if __name__ == '__main__':
    main()

import asyncio
import logging
from aiogram import Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from data import loader
from aiogram.types import BotCommand
from handlers import start_handler, admin_handler, admin_message_handler, battles_user_handler
from utils.schedulers import *

async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command='/start', description='ОБНОВИТЬ БОТА'),]
    await bot.set_my_commands(main_menu_commands)

async def main_start():
    bot = Bot(
        token=config.Token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)  # Correct way in aiogram 3.7.0+
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(
       start_handler.dp,
       admin_handler.dp,
       admin_message_handler.dp,
       battles_user_handler.dp
    )

    dp.startup.register(set_main_menu)
    await db.db_start()
    scheduler.add_job(scheduled_task, 'interval', seconds=60)
    scheduler.start()
    await bot.delete_webhook(drop_pending_updates=False)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        encoding='cp1251',
        handlers=[
            logging.FileHandler("log/py_log.log"),
            logging.StreamHandler()
        ]
    )
    
    asyncio.run(main_start())
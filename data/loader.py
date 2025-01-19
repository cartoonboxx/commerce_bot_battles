from aiogram import Bot
from aiogram.client.bot import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from data import config

def start_bot(token: str):
    bot = Bot(
        token=token,
        default=DefaultBotProperties(parse_mode="HTML")
    )
    return bot

scheduler = AsyncIOScheduler()
bot = start_bot(config.Token)
from django.shortcuts import render
from django.views.generic import TemplateView
from aiogram import Bot
from aiogram.client.bot import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from data.config import Token
# import asyncio

def start_bot(token: str):
    bot = Bot(
        token=token,
        default=DefaultBotProperties(parse_mode="HTML")
    )
    return bot

scheduler = AsyncIOScheduler()
bot = start_bot(Token)

TEMPLATES_PATH = 'prizes_app/'

def index(request):
    # asyncio.run(send_bot())
    return render(request, TEMPLATES_PATH + 'index.html')

# async def send_bot():
#     await bot.send_message(794764771, text="hello from webapp")


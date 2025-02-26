from django.shortcuts import render
from django.views.generic import TemplateView
from aiogram import Bot
from aiogram.client.bot import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from data.config import Token

def start_bot(token: str):
    bot = Bot(
        token=token,
        default=DefaultBotProperties(parse_mode="HTML")
    )
    return bot

scheduler = AsyncIOScheduler()
bot = start_bot(Token)

TEMPLATES_PATH = 'prizes_app/'

async def index(request):
    await bot.send_message(794764771, text="hello from webapp")
    return render(request, TEMPLATES_PATH + 'index.html')

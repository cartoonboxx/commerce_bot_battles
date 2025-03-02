from django.shortcuts import render
from aiogram import Bot
from aiogram.client.bot import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler
# import asyncio
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *
import datetime

# def start_bot(token: str):
#     bot = Bot(
#         token=token,
#         default=DefaultBotProperties(parse_mode="HTML")
#     )
#     return bot
#
# scheduler = AsyncIOScheduler()
# bot = start_bot(Token)

TEMPLATES_PATH = 'prizes_app/'

def index(request):
    # asyncio.run(send_bot())
    return render(request, TEMPLATES_PATH + 'index.html')

@csrf_exempt
def create_new_prize_app(request):
    data = request.POST
    prize_id = data.get('prize_id')
    tg_stars = data.get('tgstars')
    winners = data.get('winners')
    time_ = data.get('time')
    endtime = datetime.datetime.now() + datetime.timedelta(minutes=int(time_))
    endtime = endtime.strftime("%H:%M:%S")
    prize = PrizeAppModel.objects.create(
        id=prize_id,
        tg_stars=tg_stars,
        count_winners=winners,
        time=time_,
        endtime=endtime,
    )

    return HttpResponse(prize)

def prize_app_render(request, prize_id: int):
    print(prize_id)
    context = {
        'prize_id': prize_id
    }
    return render(request, 'prizes_app/index.html', context=context)



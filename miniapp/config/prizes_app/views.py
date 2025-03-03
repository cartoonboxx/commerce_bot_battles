from django.shortcuts import render
from .models import *
import datetime

def prize_app_render(request, prize_id: int):
    print(prize_id)

    current_prize_app = PrizeAppModel.objects.get(
        id=prize_id
    )

    current_time = datetime.datetime.now()
    current_time = current_time.strftime("%H:%M:%S")

    time_format = "%H:%M:%S"
    time1 = datetime.datetime.strptime(current_prize_app.endtime, time_format)
    time2 = datetime.datetime.strptime(current_time, time_format)

    time_difference = time1 - time2

    total_seconds = int(time_difference.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    time = f"{hours:02}:{minutes:02}:{seconds}"

    endtime = current_prize_app.endtime

    all_users = UserPrizeModel.objects.all()

    context = {
        'prize_id': prize_id,
        'prizeObj': current_prize_app,
        'starsByOne': current_prize_app.tg_stars // current_prize_app.count_winners,
        'timeEnd': endtime[:5],
        'fh': time[0],
        'lh': time[1],
        'fm': time[3],
        'lm': time[4],
        'fs': time[6],
        'ls': time[7],
        'users': all_users
    }
    return render(request, 'prizes_app/index.html', context=context)



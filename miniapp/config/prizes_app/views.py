from django.shortcuts import render
from django.http import HttpResponse
from .models import *
import datetime
import urllib

def prize_app_render(request, prize_id: int):
    print(prize_id)

    try:
        current_prize_app = PrizeAppModel.objects.get(
            id=prize_id
        )
    except Exception as ex:
        return HttpResponse("Page Not Found")

    current_time = datetime.datetime.now()
    current_time = current_time.strftime("%H:%M:%S")

    time_format = "%H:%M:%S"
    time1 = datetime.datetime.strptime(current_prize_app.endtime, time_format)
    time2 = datetime.datetime.strptime(current_time, time_format)

    time_difference = time1 - time2

    total_seconds = int(time_difference.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    time_arr = [hours, minutes, seconds]
    for index, timeDiv in enumerate(time_arr):
        if timeDiv < 10:
            time_arr[index] = f'0{timeDiv}'

    time = f"{time_arr[0]}:{time_arr[1]}:{time_arr[2]}"

    endtime = current_prize_app.endtime

    all_users = UserPrizeModel.objects.filter(
        prize_id=prize_id
    )
    print(time)

    base_url = 'https://t.me/share/url'
    share_url = f'https://t.me/vndfkjnkjdfgbknvds_bot?start=prizeApp_{prize_id}_from_{794764771}'
    text = f"Привет, "
    encoded_text = urllib.parse.quote(text, safe='')
    encoded_url = urllib.parse.quote(share_url, safe='')
    full_url = f"{base_url}?url={encoded_url}&text={encoded_text}"

    is_finished = current_prize_app.isFinished
    print(is_finished)

    winners_list = UserWinnersPrizeModel.objects.filter(
        prize_id=prize_id
    )

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
        'users': all_users,
        'url_button': full_url,
        'isFinished': is_finished,
        'winners': winners_list
    }
    return render(request, 'prizes_app/index.html', context=context)



from django.shortcuts import render
from .models import *

def prize_app_render(request, prize_id: int):
    print(prize_id)

    current_prize_app = PrizeAppModel.objects.get(
        id=prize_id
    )

    context = {
        'prize_id': prize_id,
        'prizeObj': current_prize_app,
        'starsByOne': current_prize_app.tg_stars // current_prize_app.count_winners,
        'fh': current_prize_app.endtime[0],
        'lh': current_prize_app.endtime[1],
        'fm': current_prize_app.endtime[3],
        'lm': current_prize_app.endtime[4],
        'fs': current_prize_app.endtime[6],
        'ls': current_prize_app.endtime[7]
    }
    return render(request, 'prizes_app/index.html', context=context)



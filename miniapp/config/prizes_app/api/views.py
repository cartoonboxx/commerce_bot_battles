from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from ..models import *
import datetime

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
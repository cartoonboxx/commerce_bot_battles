from django.http import HttpResponse, JsonResponse, HttpRequest
from django.core import serializers
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from ..models import *
import json
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


def add_user_if_not_exists(request):
    data = request.GET

    users = UserPrizeModel.objects.all()
    for user in users:
        if int(user.user_id) == int((data.get('user_id'))):
            return HttpResponse('Пользователь уже есть')

    user_prize = UserPrizeModel(
        user_id=data.get('user_id'),
        name=data.get('name'),
        photo=data.get('photo'),
    )

    user_prize.save()

    return HttpResponse(f"Пользователь {data.get('name')} создан")

@csrf_exempt
def collect_all_users(request):
    try:
        users = UserPrizeModel.objects.all()
        print('users_collected')
        serialized_users = serializers.serialize('json', users)

        users_list = json.loads(serialized_users)

        return JsonResponse(users_list, safe=False)
    except Exception as ex:
        return JsonResponse({})

def remove_user(request):
    data = request.GET
    try:
        UserPrizeModel.objects.filter(user_id=data.get('user_id')).delete()
    except Exception as ex:
        return HttpResponse('Пользователя уже удалили')

    return HttpResponse(f"Пользователь {data.get('user_id')} покинул игру")

def finish_prize(request):
    data = request.GET
    prize_id = data.get('prize_id')
    print(request.GET, prize_id)
    prize_obj = PrizeAppModel.objects.filter(
        id=prize_id
    )[0]

    prize_obj.isFinished = True
    prize_obj.save()

    return HttpResponse('isFinished')
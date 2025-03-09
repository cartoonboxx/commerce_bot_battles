from django.http import HttpResponse, JsonResponse, HttpRequest
from django.core import serializers
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from ..models import *
import json, datetime, random

@csrf_exempt
def create_new_prize_app(request):
    data = request.POST
    prize_id = data.get('prize_id')
    tg_stars = data.get('tgstars')
    winners = data.get('winners')
    time_ = data.get('time')
    endtime = datetime.datetime.now() + datetime.timedelta(minutes=int(time_))
    print(endtime)
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
        if int(user.user_id) == int((data.get('user_id'))) and int(user.prize_id) == int((data.get('prize_id'))):
            return HttpResponse('Пользователь уже есть')

    filter_data = InvitedUsersModel.objects.filter(
        user_id=data.get('user_id'),
        prize_id=data.get('prize_id')
    )
    if len(filter_data):
        user_prize = UserPrizeModel(
            user_id=data.get('user_id'),
            name=data.get('name'),
            photo=data.get('photo'),
            prize_id=data.get('prize_id'),
            invited_from=filter_data[0].invited_from
        )
    else:
        user_prize = UserPrizeModel(
            user_id=data.get('user_id'),
            name=data.get('name'),
            photo=data.get('photo'),
            prize_id=data.get('prize_id')
        )

    user_prize.save()

    return HttpResponse(f"Пользователь {data.get('name')} создан")

@csrf_exempt
def collect_all_users(request):
    data = request.GET

    prize_id = data.get('prize_id')

    try:
        users = UserPrizeModel.objects.filter(
            prize_id=prize_id
        )

        serialized_users = serializers.serialize('json', users)

        users_list = json.loads(serialized_users)

        return JsonResponse(users_list, safe=False)
    except Exception as ex:
        return JsonResponse({})

def remove_user(request):
    data = request.GET
    try:
        UserPrizeModel.objects.filter(
            user_id=data.get('user_id'),
            prize_id=int(data.get('prize_id'))
        ).delete()
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

def get_data_prize(reqeust):
    data = reqeust.GET
    prize_id = data.get('prize_id')
    prize_data = PrizeAppModel.objects.get(
        id=prize_id
    )

    users = UserPrizeModel.objects.filter(
        prize_id=prize_id
    )
    serialized_users = serializers.serialize('json', users)
    users_list = json.loads(serialized_users)

    winners = UserWinnersPrizeModel.objects.filter(
        prize_id=prize_id
    )
    serialized_winners = serializers.serialize('json', winners)
    winners_list = json.loads(serialized_winners)

    return JsonResponse({
        'prize_info': {
            'tg_stars': prize_data.tg_stars,
            'count_winners': prize_data.count_winners,
            'endTime': prize_data.endtime[:5]
        },
        'users': users_list,
        'winners': winners_list
    }, safe=False)

def collect_winners(request):
    data = request.GET
    prize_id = data.get('prize_id')

    winners_objs = UserWinnersPrizeModel.objects.filter(
        prize_id=prize_id
    )

    if not len(winners_objs):
        prize_data = PrizeAppModel.objects.get(
            id=prize_id
        )

        users = UserPrizeModel.objects.filter(
            prize_id=prize_id
        )

        participants = [{
            'name': user.name,
            'user_id': user.user_id,
            'invites': UserPrizeModel.calc_len_invites(user.user_id),
            'photo': user.photo,
            'chance': user.calc_user_chance(),

        } for user in users]

        winners = []
        unique_winners = set()

        while len(winners) < prize_data.count_winners and len(winners) < len(users):
            winner = pick_winner(participants)

            winner_tuple = tuple(winner.items())

            if winner_tuple not in unique_winners:
                unique_winners.add(winner_tuple)
                winners.append(winner)

        for winner in winners:
            winnerObj = UserWinnersPrizeModel(
                name=winner.get('name'),
                user_id=winner.get('user_id'),
                photo=winner.get('photo'),

                prize_id=prize_id,

                chance=winner.get('chance'),
                invites=winner.get('invites'),
            )

            winnerObj.save()
    else:
        winners_serialized = serializers.serialize('json', winners_objs)
        result = json.loads(winners_serialized)
        winners = [{
            'name': winner.name,
            'user_id': winner.user_id,
            'invites': UserPrizeModel.calc_len_invites(winner.user_id),
            'photo': winner.photo,
            'chance': winner.calc_user_chance(),
        } for winner in result]

    return JsonResponse(winners, safe=False)

def pick_winner(participants, base_weight=1, coefficient=1):
    if not participants:
        return None

    total_weight = sum(
        base_weight + participant['invites'] * coefficient
        for participant in participants
    )

    random_value = random.random() * total_weight
    remaining_weight = random_value

    for participant in participants:
        weight = base_weight + participant['invites'] * coefficient
        if remaining_weight <= weight:
            return participant
        remaining_weight -= weight

    return participants[-1]

def add_invite(request):
    data = request.GET

    user_id = data.get('user_id')
    invited_from = data.get('invited_from')
    prize_id = data.get('prize_id')

    filter_data = InvitedUsersModel.objects.filter(
        user_id=user_id,
        prize_id=prize_id
    )

    if not len(filter_data) and user_id != invited_from:
        invite = InvitedUsersModel(
            user_id=user_id,
            prize_id=prize_id,
            invited_from=invited_from
        )

        invite.save()

    return HttpResponse('added')

def get_all_winners(request):
    data = request.GET

    prize_id = data.get('prize_id')

    winners = UserWinnersPrizeModel.objects.filter(
        prize_id = prize_id
    )

    serialized_winners = serializers.serialize('json', winners)

    winners_list = json.loads(serialized_winners)

    return JsonResponse(winners_list, safe=False)
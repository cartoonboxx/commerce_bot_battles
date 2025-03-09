from django.urls import path
from .views import *

urlpatterns = [
    path('create_new_prize', create_new_prize_app),
    path('users', collect_all_users),
    path('adduser/', add_user_if_not_exists),
    path('removeuser', remove_user),
    path('finish_prize', finish_prize),
    path('data', get_data_prize),
    path('collect_winners', collect_winners),
    path('add_invite', add_invite)
]
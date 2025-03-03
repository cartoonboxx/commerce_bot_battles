from django.urls import path
from .views import *

urlpatterns = [
    path('create_new_prize/', create_new_prize_app),
    path('users/', collect_all_users),
    path('adduser', add_user_if_not_exists)
]
from django.urls import path
from .views import *

urlpatterns = [
    path('', index),
    path('api/create_new_prize', create_new_prize_app),
    path('<prize_id>', prize_app_render)
]
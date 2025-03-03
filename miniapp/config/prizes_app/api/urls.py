from django.urls import path
from .views import *

urlpatterns = [
    path('create_new_prize/', create_new_prize_app),
]
from django.contrib import admin
from .models import *

@admin.register(PrizeAppModel)
class PrizeAppModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'tg_stars', 'count_winners')

    class Meta:
        verbose_name = 'Розыгрыш'
        verbose_name_plural = 'Розыгрыши'

@admin.register(UserPrizeModel)
class UserPrizeModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user_id', 'invited_from')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

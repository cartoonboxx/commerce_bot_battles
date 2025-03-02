from django.contrib import admin
from .models import *

@admin.register(PrizeAppModel)
class PrizeAppModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'tg_stars', 'count_winners')

    # prepopulated_fields = {'slug': ('name',)}

    class Meta:
        verbose_name = 'Розыгрыш'
        verbose_name_plural = 'Розыгрыши'

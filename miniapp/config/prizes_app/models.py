from django.db import models

class PrizeAppModel(models.Model):
    tg_stars = models.IntegerField(verbose_name='Tg Stars')
    count_winners = models.IntegerField(verbose_name='Winner Count')
    time = models.IntegerField(verbose_name='Time (mins)')
    endtime = models.TextField(verbose_name='EndTime')

    def __str__(self):
        return f'{self.tg_stars} - {self.count_winners}'

    class Meta:
        verbose_name = 'Конкурс'
        verbose_name_plural = 'Конкурсы'

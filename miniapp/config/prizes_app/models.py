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

class UserPrizeModel(models.Model):
    name = models.CharField(verbose_name='Имя пользователя', max_length=100)
    user_id = models.IntegerField(verbose_name='Айди пользователя')
    invited_from = models.IntegerField(verbose_name='Приглашен от айди')

    def collect_users_invites(self):
        return UserPrizeModel.objects.filter(
            invited_id=self.user_id
        )

    def calc_len_invites(self):
        return len(self.collect_users_invites())

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Пользователь конкурса'
        verbose_name_plural = 'Пользователи конкурсов'
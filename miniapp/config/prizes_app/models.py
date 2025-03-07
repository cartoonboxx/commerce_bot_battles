from django.db import models

class PrizeAppModel(models.Model):
    tg_stars = models.IntegerField(verbose_name='Tg Stars')
    count_winners = models.IntegerField(verbose_name='Winner Count')
    time = models.IntegerField(verbose_name='Time (mins)')
    endtime = models.TextField(verbose_name='EndTime')

    isFinished = models.BooleanField(verbose_name='Статус окончания', default=False)

    def __str__(self):
        return f'{self.tg_stars} - {self.count_winners}'

    class Meta:
        verbose_name = 'Конкурс'
        verbose_name_plural = 'Конкурсы'

class UserPrizeModel(models.Model):
    name = models.CharField(verbose_name='Имя пользователя', max_length=100)
    user_id = models.IntegerField(verbose_name='Айди пользователя')
    invited_from = models.IntegerField(verbose_name='Приглашен от айди', blank=True, null=True)
    photo = models.CharField(verbose_name='Фото', max_length=150)

    prize_id = models.IntegerField(verbose_name='Айди розыгрыша')

    @staticmethod
    def collect_users_invites(user_id):
        return UserPrizeModel.objects.filter(
            invited_from=user_id
        )

    @staticmethod
    def calc_len_invites(user_id):
        return len(UserPrizeModel.collect_users_invites(user_id))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Пользователь конкурса'
        verbose_name_plural = 'Пользователи конкурсов'

class UserWinnersPrizeModel(UserPrizeModel):

    def calc_user_chance(self):
        base_weight = 1
        coefficient = 1
        participants = [{
            'user_id': user.user_id,
            'invites': UserPrizeModel.calc_len_invites(user.user_id)
        } for user in UserPrizeModel.objects.all()]

        total_weight = sum(
            base_weight + participant['invites'] * coefficient
            for participant in participants
        )

        result = []
        for participant in participants:
            weight = base_weight + participant['invites'] * coefficient
            chance = (weight / total_weight) * 100 if total_weight else 0  # avoid division by zero

            result.append({
                **participant,  # Copy existing participant data
                'weight': weight,
                'chance': chance,
            })

        for user in result:
            if user.get('user_id') == self.user_id:
                current_chance = user.get('chance')
                return current_chance

        return 0


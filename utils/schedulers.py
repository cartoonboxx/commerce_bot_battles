from database import db
from database.db import *
from .utils import *
from aiogram.utils.keyboard import InlineKeyboardBuilder
from functions.admin_functions import check_users_tasks
from data.loader import *
from datetime import time
import datetime
import random

async def scheduled_task():
    date_now = datetime.datetime.now().date()
    time_now = datetime.datetime.now()
    battles = await db.check_all_battles_where_status_3_return_id()
    for battle_id in battles:
        battle_photos = await db.check_all_battle_photos_where_status_1_and_battle_id(battle_id)

        for battle_photo in battle_photos:
            photo_time_str = battle_photo[9]

            try:
                photo_time = datetime.datetime.strptime(photo_time_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                try:
                    photo_time = datetime.datetime.strptime(photo_time_str, '%H:%M:%S')
                    photo_time = datetime.datetime.combine(date_now, photo_time.time())
                except ValueError:
                    print(f"Неверный формат времени: {photo_time_str}")
                    continue

            time_difference = time_now - photo_time
            print(time_difference)
            if int(time_difference.total_seconds()) // 60 == 10 or\
                    int(time_difference.total_seconds()) // 60 == 20:
                tg_id = battle_photo[1]
                try:
                    current_voices = 0
                    battle_info = await check_battle_info(battle_id)
                    min_voice = battle_info[11]
                    user_info = await check_battle_where_battle_id_and_tg_id_exist_and_status_1(battle_id, tg_id)
                    users_in_battle = await check_all_battle_photos_where_status_1_and_battle_id_and_number_post(battle_id, user_info[6])
                    print('Отладка')
                    print(user_info)
                    print(users_in_battle)
                    user_voices = user_info[4]

                    max_user_voices = 0
                    for user in users_in_battle:
                        max_user_voices = max(max_user_voices, user[4])

                    if max_user_voices == 0 or max_user_voices < min_voice:
                        current_voices = min_voice
                    else:
                        current_voices = max_user_voices

                    url = encode_url(tg_id)

                    user_data = await db.check_info_users_by_tg_id(user_info[1])

                    text = f"‼️ <b>Вам не хватает {current_voices - user_voices + 1} голосов, чтобы пройти в следующий раунд</b>\n\nЖмите <b>🔥 Хочу больше голосов</b>, чтобы получить больше голосов"
                    if user_voices < current_voices and user_info[6] != 0 and user_data[7]:
                        print(user_voices, current_voices)
                        kb = InlineKeyboardBuilder()
                        user_data = await db.check_info_users_by_tg_id(user_info[1])
                        if user_data[7]:
                            kb.button(text='🔕 Выкл. уведомления', callback_data=f'mailing_callback;{user_data[1]};{battle_info[5]};{battle_id}')
                        else:
                            kb.button(text='🔔 Вкл. уведомления', callback_data=f'mailing_callback;{user_data[1]};{battle_info[5]};{battle_id}')
                        channel_info = await db.check_channel_info_by_id(battle_info[1])
                        channel_data = await bot.get_chat(channel_info[2])
                        new_postlink = await db.get_user_link_post(tg_id)
                        print(new_postlink)
                        kb.button(text='Ссылка на пост', url=new_postlink[2])
                        print('Установлена ссылка на пост')
                        if not channel_data.username:
                            kb.button(text="Ссылка на канал", url=battle_info[5])
                        print('Проверена ссылка на канал')
                        if await check_users_tasks(battle_id, tg_id):
                            kb.button(text="🔥 Хочу больше голосов", callback_data=f'wanted_more_voices;{battle_id};{battle_info[5]}')
                        kb.adjust(1)
                        await bot.send_message(
                            chat_id=tg_id,
                            text=text, reply_markup=kb.as_markup(),
                            disable_web_page_preview=True)
                except Exception as e:
                    print(e)

async def delete_every_24_hours_scheduler():
    all_battles = await db.check_all_battles()
    for battle in all_battles:
        battle_id = battle[0]
        current_day_votes_sum = await calc_all_votes_in_battle(battle_id)
        if current_day_votes_sum == battle[24]:
            await db.delete_battle_by_id(battle_id)
        else:
            await db.update_yesterday_votes(battle_id)

    '''Удалить каналы, батлы, батлофотки, если бота нет в админах'''

    all_channels = await db.check_all_channels()
    for channel in all_channels:
        try:
            await bot.get_chat(channel[2])
        except Exception as ex:
            await db.delete_all_info_where_channel_id(channel[0])

    '''Удаление админов, у которых нет каналов'''
    all_admins = await db.check_all_admins()
    for admin in all_admins:
        admin_channels = await db.checkk_all_channels_where_tg_id(admin[1])
        if not admin_channels:
            await db.delete_admin(admin[1])


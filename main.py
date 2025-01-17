import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
import urllib
from data import config, loader
from database.db import *
from database import db
from aiogram.types import BotCommand
from handlers import start_handler, admin_handler, admin_message_handler, battles_user_handler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import datetime
from datetime import time
import random
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Создаем экземпляр шедулера
scheduler = AsyncIOScheduler()


motivations = [f"‼️ ВЫ ПРОИГРЫВАЕТЕ\n\nВам нехватает  ГОЛОСОВ, чтобы пройти в следующий раунд\n\nВаша ссылка для принятия голосов:.\nСсылка на канал -"]

def encode_url(account_id):

    # Замените это на ваш фактический ID

    # Основная ссылка для шаринга в Telegram
    base_url = 'https://t.me/share/url'

    # Ссылка на бот с вашим ID
    bot_url = f'https://t.me/{config.bot_name}?start={account_id}'

    # Текст, который вы хотите отправить
    text = "👉 Привет, можешь пожалуйста проголосовать за меня в боте?"

    # Кодируем каждый параметр отдельно
    encoded_bot_url = urllib.parse.quote(bot_url, safe='')
    encoded_text = urllib.parse.quote(text, safe='')

    # Создаём полную ссылку
    full_url = f"{base_url}?url={encoded_bot_url}&text={encoded_text}"
    return full_url

bot = loader.start_bot(config.Token)


async def scheduled_task():
    # Получить текущую дату и время
    date_now = datetime.datetime.now().date()
    time_now = datetime.datetime.now()

    battles = await db.check_all_battles_where_status_3_return_id()

    for battle_id in battles:
        battle_photos = await db.check_all_battles_photo_where_id(battle_id)

        for battle_photo in battle_photos:
            photo_time_str = battle_photo[9]


            # Попробуем сначала как полную дату и время
            try:
                photo_time = datetime.datetime.strptime(photo_time_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                # Предполагаем, что это может быть только время
                try:
                    photo_time = datetime.datetime.strptime(photo_time_str, '%H:%M:%S')
                    photo_time = datetime.datetime.combine(date_now, photo_time.time())
                except ValueError:
                    print(f"Неверный формат времени: {photo_time_str}")
                    continue

            # Вычисляем разницу во времени
            time_difference = time_now - photo_time

            # Проверяем разницу во времени
            if time_difference.total_seconds() > 600:

                tg_id = battle_photo[1]
                await db.update_last_like(tg_id, time_now.strftime('%Y-%m-%d %H:%M:%S'), battle_id)

                try:
                    current_voices = 0
                    battle_info = await check_battle_info(battle_id)
                    min_voice = battle_info[11]
                    users_in_battle = await check_users_from_battle(battle_id)
                    user_info = await check_battle_where_battle_id_and_tg_id_exist_and_status_1(battle_id, tg_id)
                    user_voices = user_info[4]

                    max_user_voices = 0
                    for user in users_in_battle:
                        max_user_voices = max(max_user_voices, user[4])

                    if max_user_voices == 0 or max_user_voices < min_voice:
                        current_voices = min_voice
                    else:
                        current_voices = max_user_voices

                    # Подготовка клавиатуры и сообщения
                    url = encode_url(tg_id)
                    # найти нужный батл айди

                    text = f"‼️ <b>ВЫ ПРОИГРЫВАЕТЕ</b>\n\nВам не хватает <b>{current_voices - user_voices + 1} ГОЛОСОВ</b>, чтобы пройти в следующий раунд\n\n<a href='https://t.me/{config.bot_name}?start=vote{battle_id}page{user_info[6]}'>Ваша ссылка на голосование</a>"
                    if user_voices != max_user_voices and current_voices > 0 and user_info[6] != 0:
                        kb = InlineKeyboardBuilder()
                        kb.button(text="Ссылка на канал", url=battle_info[5])
                        kb.adjust(1)
                        await bot.send_message(
                            chat_id=tg_id,
                            text=text, reply_markup=kb.as_markup(),
                            disable_web_page_preview=True)
                except Exception as e:
                    print(e)


async def scheduled_task2():
    active_battles = await db.check_battles_where_status_1_return_battle_info()

    for battle_info in active_battles:
        registration_start_time = datetime.datetime.strptime(battle_info[8], '-').time()
        registration_end_time = datetime.datetime.strptime(battle_info[9], '%H:%M').time()

        current_time = datetime.datetime.now().time()

        if registration_start_time <= current_time < registration_end_time:
            remaining_seconds = (datetime.datetime.combine(datetime.datetime.today(), registration_end_time) -
                                 datetime.datetime.combine(datetime.datetime.today(), current_time)).total_seconds()
            minutes_left = remaining_seconds // 60

            interval_seconds = int((datetime.datetime.combine(datetime.datetime.today(), registration_end_time) -
                                   datetime.datetime.combine(datetime.datetime.today(), registration_start_time)).total_seconds())
            first_mailing_seconds = int((registration_end_time.hour * 3600 + registration_end_time.minute * 60) - interval_seconds / 3)
            second_mailing_seconds = int((registration_end_time.hour * 3600 + registration_end_time.minute * 60) - 2 * interval_seconds / 3)

            first_mailing = time(first_mailing_seconds // 3600, (first_mailing_seconds % 3600) // 60)
            second_mailing = time(second_mailing_seconds // 3600, (second_mailing_seconds % 3600) // 60)
            
            if current_time.strftime('%H:%M') == first_mailing.strftime('%H:%M') or current_time.strftime('%H:%M') == second_mailing.strftime('%H:%M'):
                battle_id = battle_info[0]
                all_photos = await db.check_all_battle_photos_where_battle_id(battle_id)
                random_motiv = [f"⏰ Батл, в котором вы приняли участие, начинается через {minutes_left} МИНУТ\n\nСсылка на канал - {battle_info[5]}"]
                random_motiv = random.choice(random_motiv)
                for photo in all_photos:
                    tg_id = photo[1]
                    try:
                        await bot.send_message(chat_id=tg_id,text=random_motiv)
                    except Exception as e:
                        print(e)
            else:
                print(int(minutes_left))
        

        


            

async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command='/start', description='ОБНОВИТЬ БОТА'),]
    await bot.set_my_commands(main_menu_commands)

from aiogram.client.bot import DefaultBotProperties

async def main_start():
    bot = Bot(
        token=config.Token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)  # Correct way in aiogram 3.7.0+
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(
       start_handler.dp,
       admin_handler.dp,
       admin_message_handler.dp,
       battles_user_handler.dp
    )

    # Register main menu
    dp.startup.register(set_main_menu)

    # Initialize the database
    await db.db_start()

    # Start the scheduler
    scheduler.add_job(scheduled_task, 'interval', seconds=60)  # Run every 60 seconds
    scheduler.add_job(scheduled_task2, 'interval', seconds=55)
    scheduler.start()

    # Delete webhook if set
    await bot.delete_webhook(drop_pending_updates=False)

    # Start polling
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())



if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        encoding='cp1251',
        handlers=[
            logging.FileHandler("log/py_log.log"),
            logging.StreamHandler()
        ]
    )
    
    asyncio.run(main_start())
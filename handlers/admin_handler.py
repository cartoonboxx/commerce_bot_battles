from aiogram import types
import asyncio
from data.config import *
from keyboards.another import back_main_menu_add_channel_opt
from test import bot_url
from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from data import loader, config
from database import db
from aiogram.types.input_file import FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from states.classes_states import *
from aiogram.types import InputMediaPhoto
from functions.admin_functions import *
from database.db import *
import datetime



dp = Router()
bot = loader.start_bot(config.Token)

def replace_last_digits(url, new_digits):
    # Найти индекс последнего "/"
    last_slash_index = url.rfind('/')
    
    # Если символ найден, отделяем всё, что после него
    if last_slash_index != -1:
        # Заменяем всё после последнего "/" на новые цифры
        new_url = url[:last_slash_index+1] + str(new_digits)
        return new_url
    else:
        # Если нет "/", возвращаем исходную ссылку
        return url

class AddVoices(StatesGroup):
    q1 = State()
    q2 = State()

class Mailing(StatesGroup):
    q1 = State()
    q2 = State()

async def create_battle(call: types.CallbackQuery, battle_id):
    battle_info = await db.check_battle_info(battle_id)
    post_start_battle = battle_info[17]
    if post_start_battle == 0:
            post_start_battle = 'Не нужен'
    else:
            post_start_battle = f'Нужен'
    await call.message.edit_text(f'''<b>🛠️ Создание фото-батла: (1 ШАГ ИЗ 2)</b>

- Название:  {battle_info[3]}
- Ссылка на канал: {battle_info[5]}
- Пост о начале батла: {post_start_battle}
- Приз: {battle_info[6]}
- Время начала: {battle_info[8]}
- Время завершения: {battle_info[9]}
- Минимальное кол-во участников: {battle_info[10]}                                                    
''', reply_markup=await create_battle_kb(battle_id, battle_info[5]), disable_web_page_preview=True)
    
@dp.callback_query(lambda c: c.data.startswith('spisokadminov'))
async def admin_menu_handler(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split(';')[1]
    if action == 'mailing':
        await callback.message.answer('Введите сообщение для рассылки')
        await state.set_state(Mailing.q1)

#кнопка назад из добавления канала
def back_from_addchannel():
    kb = InlineKeyboardBuilder()
    kb.button(text='🔙 Назад', callback_data='back_from_addchannel')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)

async def settings_channel(callback: types.CallbackQuery, channel_id):
    channel_info = await db.check_channel_info_by_id(channel_id)
    name = channel_info[3]  
    await callback.message.edit_text(f'<b>⚙️ Настройки канала "{name}"</b>', reply_markup=await back_main_menu_add_channel_opt(channel_id))


@dp.callback_query(lambda c: c.data.startswith('optionchannel'))
async def option_channel_handler(callback: types.CallbackQuery):
    print('вот тут что-то')
    channel_id = callback.data.split(';')[1] 
    await settings_channel(callback, channel_id)
    
@dp.callback_query(lambda c: c.data.startswith('backtocreate'))
async def backtocreate(callback: types.CallbackQuery):
    battle_id = callback.data.split(';')[1] 
    await create_battle(callback, battle_id)


@dp.callback_query(lambda c: c.data.startswith('channelsetting'))
async def channel_setting_handler(callback: types.CallbackQuery, state:FSMContext):
    await state.clear()
    action = callback.data.split(';')[1]
    channel_id = callback.data.split(';')[2]
    await chennelsetting_func(callback,channel_id, action, state )

@dp.callback_query(lambda c: c.data.startswith('approvedelete'))
async def approve_delete_channel_handler(callback: types.CallbackQuery):
    channel_id = callback.data.split(';')[1]
    await delete_channel_func(callback, channel_id)

@dp.callback_query(lambda c: c.data.startswith('2approvedelete'))
async def approve_delete_channel_handler2(callback: types.CallbackQuery):
    channel_id = callback.data.split(';')[1]
    await delete_channel_func2(callback, channel_id)

@dp.callback_query(lambda c: c.data.startswith('battlesettings'))
async def battlesettings(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    action = callback.data.split(';')[1]
    battle_id = callback.data.split(';')[2]

    await battle_settings_func(callback, battle_id,action, state)



@dp.callback_query(lambda c: c.data.startswith('optionactivebattle'))
async def option_active_battle_handler(callback: types.CallbackQuery):
    battle_id = callback.data.split(';')[1]
    await active_battle_func(callback, battle_id)


@dp.callback_query(lambda c: c.data.startswith('activebattlesettings'))
async def active_battle_settings_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    action = callback.data.split(';')[1]
    battle_id = callback.data.split(';')[2]
    await active_battle_options_func(callback, battle_id, action, state)

@dp.callback_query(lambda c: c.data.startswith('saveRoundParam'))
async def saveRoundParam(callback: types.CallbackQuery, state: FSMContext):
    data = callback.data.split(';')
    post = data[-2]
    battle_id = data[-1]
    await state.clear()
    await db.updatePostFieldBattles(post, battle_id)
    await active_battle_func(callback, battle_id)



@dp.callback_query(lambda c: c.data.startswith('approveactivebattlesettings'))
async def approve_active_battle_settings_handler(callback: types.CallbackQuery):
    battle_id = callback.data.split(';')[1]
    await callback.answer('Батл успешно начался', show_alert=True)
    await db.update_status_battle(battle_id, Status.ENDROUND.value)
    await active_battle_func(callback, battle_id)
    battle_info = await db.check_battle_info(battle_id)
    
    channel_id = battle_info[1]
    channel_info = await db.check_channel_info_by_id(channel_id)
    channel_tg_id = channel_info[2]
    members_in_post = battle_info[13]
    all_battle_users = await db.check_all_battle_photos_where_status_1_and_battle_id(battle_id)
    posts = [all_battle_users[i:i + members_in_post] for i in range(0, len(all_battle_users), members_in_post)]

    count = 0
    
    for index, post in enumerate(posts):
        count+=1
        media_group = []
        for user in post:
            media_photo = InputMediaPhoto(media=user[3])
            media_group.append(media_photo)
              # Обновление для каждого пользователя
        kb = InlineKeyboardBuilder()

        if battle_info[20] == '-':
            text = f'''⚔️ <b>{battle_info[7]}</b>
<b>💰 ПРИЗ — {battle_info[6]}</b>

<b><a href="https://t.me/{bot_name}?start=b{battle_id}">✅ ИДЕТ НАБОР НА БАТЛ ТУТ</a></b>

📝 <b>Условия:</b> обогнать соперника и набрать минимум {battle_info[11]} голосов
⏳<b>Итоги:</b> {battle_info[15]} по МСК'''
        else:
            text = battle_info[20]
        await asyncio.sleep(5)
        try:
            await bot.send_media_group(chat_id=channel_tg_id, media=media_group)
            
        except Exception:
            await db.update_status_battle(battle_id, Status.Error.value)
            await active_battle_func(callback, battle_id)
            await callback.message.answer('Произошла ошибка при отправке фото в канал, нажмите продолжить')
            
            last_user_id = post[-1][0]
            await db.update_error_number(last_user_id-1, battle_id)
            last_number_post = index + 1
            await db.update_error_post(last_number_post, battle_id)
            return
        
        await asyncio.sleep(5)
        try:
            kb.button(text=f'✅ Проголосовать', url=f'https://t.me/{config.bot_name}?start=vote{battle_id}page{index+1}')
            kb.adjust(1)
            message = await bot.send_message(chat_id=channel_tg_id, text=text, reply_markup=kb.as_markup())
            message_id = message.message_id
            await db.update_id_post(message_id, battle_id)

            
        except Exception:
            await db.update_status_battle(battle_id, Status.Error.value)
            await active_battle_func(callback, battle_id)
            await callback.message.answer('Произошла ошибка при отправке фото в канал, нажмите продолжить')
            
            last_user_id = post[-1][0]
            await db.update_error_number(last_user_id-1, battle_id)
            last_number_post = index + 1
            await db.update_error_post(last_number_post, battle_id)
            return
        post_link = channel_info[6]  # Основной шаблон ссылки
        new_channel_link = replace_last_digits(post_link, str(message_id)) 
        for i, user in enumerate(post, start=1):
            
            await db.update_number_post_in_battle_photos_by_id(user[0], index + 1)
            try:
                kb = InlineKeyboardBuilder()
                kb.button(text='Ссылка на пост', url=new_channel_link)
                kb.button(text='Ссылка на канал', url=battle_info[5])
                kb.adjust(1)

                current_battle = await check_battle_info(battle_id)

                if current_battle[22] == 0:
                    await bot.send_message(chat_id=user[1], text=f'''✅ <b>ВАШЕ ФОТО ОПУБЛИКОВАНО</b>\n\nПоздравляем, вы участвуете в фото-батле. Набирайте голоса и увидимся в следующем раунде
            ''', disable_web_page_preview=True, reply_markup=kb.as_markup())
                elif current_battle[22] != 0 and current_battle[7] != 'Финал':
                    await bot.send_message(chat_id=user[1], text=f'''✅ <b>ВЫ ПРОШЛИ В СЛЕДУЮЩИЙ РАУНД</b>\n\nВы прошли предыдущий раунд. Набирайте голоса и увидимся в ФИНАЛЕ
                ''', disable_web_page_preview=True, reply_markup=kb.as_markup())
                if current_battle[7] == "Финал":
                    await bot.send_message(chat_id=user[1], text=f'''✅💪 <b>ВЫ В ФИНАЛЕ</b>\n\nПоздравляем, вы победили всех на своем пути и остались с наисельнейшими участниками. Набирайте голоса и заберете приз.
''', disable_web_page_preview=True, reply_markup=kb.as_markup())

            except Exception as e:
                print(e)
        await db.update_count_in_posts(battle_id, count)

@dp.callback_query(lambda c: c.data.startswith('aprovecontinuebattleesettings'))
async def aprove_continue_battle_handler(callback: types.CallbackQuery):
    battle_id = callback.data.split(';')[1]
    await callback.answer('Батл успешно продолжается', show_alert=True)
    await db.update_status_battle(battle_id, Status.ENDROUND.value)

    await active_battle_func(callback, battle_id)
    battle_info = await db.check_battle_info(battle_id)

    channel_id = battle_info[1]
    channel_info = await db.check_channel_info_by_id(channel_id)
    channel_tg_id = channel_info[2]
    members_in_post = battle_info[13]
    start_error_user_id = battle_info[18]
    all_battle_users = await db.check_all_battle_photos_where_status_1_and_battle_id_bigger_than(battle_id, start_error_user_id)
    posts = [all_battle_users[i:i + members_in_post] for i in range(0, len(all_battle_users), members_in_post)]
    count2 = battle_info[16]
    count = battle_info[19]
    
    for index, post in enumerate(posts, start=count):
        count2+=1
        media_group = []
        for user in post:
            media_photo = InputMediaPhoto(media=user[3])
            media_group.append(media_photo)
              # Обновление для каждого пользователя
        kb = InlineKeyboardBuilder()
        # kb.button(text='🔄 Обновить результаты', callback_data=f'reloadresults;{battle_id};{count}')
        # for i, user in enumerate(post, start=1):
        #     if i == 1:
        #         emoji = '1️⃣'
        #     if i == 2:
        #         emoji = '2️⃣'
        #     if i == 3:
        #         emoji = '3️⃣'
        #     if i == 4:
        #         emoji = '4️⃣'
        #     if i == 5:
        #         emoji = '5️⃣'
        #     if i == 6:
        #         emoji = '6️⃣'
        #     if i == 7:
        #         emoji = '7️⃣'
        #     if i == 8:
        #         emoji = '8️⃣'
        #     if i == 9:
        #         emoji = '9️⃣'
        #     if i == 10:
        #         emoji = '🔟'
        #     kb.button(text=f'{emoji} {user[4]}', url=f'https://t.me/{config.bot_name}?start={user[0]}')
        kb.button(text=f'✅ Проголосовать', url=f'https://t.me/{config.bot_name}?start=vote{battle_id}')
        kb.adjust(1)
        if battle_info[20] == '-':
            text = f'''⚔️ <b>{battle_info[7]}</b>\n<b>💰 ПРИЗ — {battle_info[6]}</b>\n\n<b><a href="https://t.me/{bot_name}?start=b{battle_id}">✅ ИДЕТ НАБОР НА БАТЛ ТУТ</a></b>\n\n📝 <b>Условия:</b> обогнать соперника и набрать минимум {battle_info[11]} голосов\n⏳<b>Итоги:</b> {battle_info[15]} по МСК'''
        else:
            text = battle_info[20]
        await asyncio.sleep(5)
        try:
            await bot.send_media_group(chat_id=channel_tg_id, media=media_group)
            
        except Exception:
            await db.update_status_battle(battle_id, Status.Error.value)
            await active_battle_func(callback, battle_id)
            await callback.message.answer('Произошла ошибка при отправке фото в канал, нажмите продолжить')
            last_user_id = post[-1][0]
            await db.update_error_number(last_user_id-1, battle_id)
            last_number_post = index
            await db.update_error_post(last_number_post, battle_id)
            return
            
        
        await asyncio.sleep(5)
        try:
            message = await bot.send_message(chat_id=channel_tg_id, text=text, reply_markup=kb.as_markup())
            message_id = message.message_id
            
        except Exception:
            await db.update_status_battle(battle_id, Status.Error.value)
            await active_battle_func(callback, battle_id)
            await callback.message.answer('Произошла ошибка при отправке фото в канал, нажмите продолжить')
            
            last_user_id = post[-1][0]
            await db.update_error_number(last_user_id-1, battle_id)
            last_number_post = index
            await db.update_error_post(last_number_post, battle_id)
            return
        post_link = channel_info[6]  # Основной шаблон ссылки
        new_channel_link = replace_last_digits(post_link, str(message_id))  # Обновляем ID сообщения

        for i, user in enumerate(post, start=1):
            # Генерация уникальной ссылки для каждого пользователя
            individual_channel_link = replace_last_digits(post_link, str(message_id))
            print(f"Generated link for user {user[0]}: {individual_channel_link}")  # Логируем ссылку
            
            await db.update_number_post_in_battle_photos_by_id(user[0], index)
            try:
                kb = InlineKeyboardBuilder()
                kb.button(text='Ссылка на пост', url=individual_channel_link)
                await bot.send_message(
                    chat_id=user[1], 
                    text=f'''Ваше фото было опубликовано\n\nСсылка на вступление в канал - {battle_info[5]}''', 
                    disable_web_page_preview=True, 
                    reply_markup=kb.as_markup()
                )
            except Exception as e:
                print(e)

        await db.update_count_in_posts(battle_id, count2)

@dp.message(Command('database'))
async def send_database_file(message: types.Message):
    # Убедитесь, что файл базы данных существует
    
        # Отправляем файл пользователю
    if message.from_user.id in config.admins:
        await message.answer_document(FSInputFile('photobattle.db'))
    


@dp.callback_query(lambda c: c.data.startswith('endapproveactivebattle'))
async def end_approve_active_battle_handler(callback: types.CallbackQuery):
    battle_id = callback.data.split(';')[1]
    await callback.answer('Батл успешно завершился', show_alert=True)
    await db.update_status_battle(battle_id, Status.NEXTROUND.value)
    battle_info = await db.check_battle_info(battle_id)
    
    count = battle_info[16]
    min_voices = battle_info[11]
    
    for i in range(1, count + 1):
        # Получение всех участников для текущего поста
        post = await db.check_battle_photos_by_battle_id_and_number_post(battle_id, i)
        
        # Если нет участников, продолжить следующую итерацию
        if not post:
            continue

        # Отфильтровать участников, у которых голоса меньше минимального
        eligible_participants = [user for user in post if user[4] >= min_voices]
        
        if not eligible_participants:
            await callback.message.answer(f'Пост {i}: нет победителей, не достигнувших минимального количества голосов')
            for user in post:
                await db.delete_user_from_battle_photos(user[0])
            continue
            
        
        max_votes = max(user[4] for user in eligible_participants)
        
        winners = [user for user in eligible_participants if user[4] == max_votes]
        for winner in winners:
            await db.update_battle_photos_votes_and_number_post(winner[0], 0,0)
        for user in post:

            
            if user not in winners:
                
                await db.delete_user_from_battle_photos(user[0])

        if winners:
            # await callback.message.answer(f'Пост {i}: победители - {[user[1] for user in winners]} с {max_votes} голосами')
            kb = InlineKeyboardBuilder()
            kb.button(text="✅ Продолжить", callback_data=f'continueToNextRound;{battle_id}')
            kb.adjust(1)
            await callback.message.answer(f'⚔️ Итоги раунда: проходит {len(winners)} человек в следующий раунд', reply_markup=kb.as_markup())

    await db.update_battles_descr_round_users_min_golos_end_round_by_id(battle_id)
    await db.delete_all_battle_voices_where_battle_id(battle_id)

@dp.callback_query(lambda c: c.data.startswith('continueToNextRound'))
async def continueToNextRound(call: types.CallbackQuery):

    battle_id = call.data.split(';')[-1]

    battle_info = await db.check_battle_info(battle_id)
    current_round = battle_info[22]
    print('current round', current_round)
    await db.update_number_round(current_round + 1, battle_id)

    await active_battle_answer_func(call.message, battle_id)


@dp.callback_query(lambda c: c.data.startswith('secapprovedeletebattle'))
async def approve_delete_battle_handler(callback: types.CallbackQuery):
    battle_id = callback.data.split(';')[1]
    await db.delete_battle_by_id(battle_id)
    await callback.message.edit_text('<b>✅ Батл удален из системы. Посты с батлами не удаляются. </b>')



async def build_keyboard(post, battle_id, count, current_page):
    kb = InlineKeyboardBuilder()
    if len(post) == 0:
        kb.button(text='Голосование завершено ☑️', callback_data=f'sfanfjsjfsajfiajs')
    else:
        kb.button(text='🔄 Обновить результаты', callback_data=f'reloadresults;{battle_id};{count};{current_page}')
        for i, user in enumerate(post, start=1):
            if i == 1:
                emoji = '1️⃣'
            if i == 2:
                emoji = '2️⃣'
            if i == 3:
                emoji = '3️⃣'
            if i == 4:
                emoji = '4️⃣'
            if i == 5:
                emoji = '5️⃣'
            if i == 6:
                emoji = '6️⃣'
            if i == 7:
                emoji = '7️⃣'
            if i == 8:
                emoji = '8️⃣'
            if i == 9:
                emoji = '9️⃣'
            if i == 10:
                emoji = '🔟'
            kb.button(text=f'{emoji} - {user[4]}', callback_data=f"voteby;{battle_id};{user[0]}")
        # kb.button(text=f'✅ Проголосовать', url=f'https://t.me/{config.bot_name}?start=vote{battle_id}')
        kb.adjust(1, 2, 3, 4)
    return kb

@dp.callback_query(lambda c: c.data.startswith('reloadresults'))
async def reload_results_handler(callback: types.CallbackQuery):
    print(callback.data.split(';'))
    battle_id = callback.data.split(';')[1]
    count = int(callback.data.split(';')[2])
    page = int(callback.data.split(';')[3])

    all_photos = await db.all_photo_by_battle(battle_id)
    current_medias = []
    for i in range((page - 1) * count, page * count):
        current_medias.append(all_photos[i])
    
    kb = await build_keyboard(current_medias, battle_id, count, page)
    try:
        await callback.message.edit_reply_markup(reply_markup=kb.as_markup())
    except Exception as e:
        print(e)

@dp.callback_query(lambda c: c.data.startswith('firstround;iagree'))
async def firstround_createbattle_continue(call: types.CallbackQuery, state: FSMContext):
    battle_id = call.data.split(';')[-1]
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Запомнил(а)", callback_data=f"firstround;publish;{battle_id}")
    kb.adjust(1)
    await call.message.edit_text('''<b>⚠️ Внимание</b>\n\nПосты будут выкладываться в канал сразу после того, как вы одобрите количество фото, которое указали на втором шаге в поле «Участников в посте»''', reply_markup=kb.as_markup())

@dp.callback_query(lambda c: c.data.startswith('firstround;publish'))
async def firstround_createbattle_publish(callback: types.CallbackQuery, state: FSMContext):
    battle_id = callback.data.split(';')[-1]

    battle_info = await db.check_battle_info(battle_id)

    await callback.message.edit_text('<b>✅ Батл создан </b> \n\nПерейдите в ⚔️ Наборы на фото-батлы, чтобы продолжить настройку')

    tg_id = callback.from_user.id
    await db.update_battle_statistic_plus_1(tg_id)
    await db.update_admin_count_minus_1(tg_id)
    channel_id = battle_info[1]
    channel_info = await db.check_channel_info_by_id(channel_id)
    channel_tg_id = channel_info[2]
    kb = InlineKeyboardBuilder()
    kb.button(text='Участвовать', url=f'https://t.me/{config.bot_name}?start=b{battle_id}')
    try:
        post_id = battle_info[17]
        if post_id is not None:
            await bot.copy_message(chat_id=channel_tg_id, from_chat_id=callback.message.chat.id,
                               message_id=battle_info[17], reply_markup=kb.as_markup()
                               )



    except Exception as e:
        print(e)
        await callback.message.answer('Ошибка отправки поста о батле')


@dp.callback_query(lambda c: c.data.startswith('firstround;createbattle'))
async def start_first_round(call: types.CallbackQuery, state: FSMContext):
    battle_id = call.data.split(';')[-1]
    battle_info = await db.check_battle_info(battle_id)

    if battle_info[13] == 0 or battle_info[11] == 0 or battle_info[15] == '-':
        await call.answer('Заполните все поля', show_alert=True)
        return

    # await db.update_status_battle(battle_id, Status.ENDROUND.value)
    post_id = battle_info[17]
    if post_id is not None:
        kb = InlineKeyboardBuilder()
        kb.button(text='✅ Продолжить', callback_data=f"firstround;iagree;{battle_id}")
        kb.button(text='🔙 Назад', callback_data=f"firstround;returnstep2;{battle_id}")
        kb.adjust(1)

        await call.message.edit_text(text=f'''<b>Данный пост будет публиковаться вместе с фото участников 📷</b>\n\n<i><b>✅ Всё верно? Проверьте данные поста, шаблон поста поменять не сможете</b></i>
        ''', reply_markup=kb.as_markup())
    else:
        await call.message.edit_text('<b>✅ Батл создан </b> \n\nПерейдите в ⚔️ Наборы на фото-батлы, чтобы продолжить настройку')

@dp.callback_query(lambda c: c.data.startswith('firstround;returnstep2'))
async def return_step_2_page_battle(call: types.CallbackQuery, state: FSMContext):
    battle_id = call.data.split(';')[-1]
    await call.message.delete()
    await firstround_menu_setting(call.message, battle_id)

@dp.callback_query(lambda c: c.data.startswith('firstround;users_in_post'))
async def set_users_in_post(call: types.CallbackQuery, state: FSMContext):
    battle_id = call.data.split(';')[-1]

    await call.message.edit_text(
            '<b>⚙️ Введите кол-во участников. в одном посте от 2 до 10.</b> \n\nУказывайте только число.',
    reply_markup=await kb_return_2page_battlecreate(battle_id))
    await state.set_state(AddActiveBattleParticipants.q1)
    await state.update_data(battle_id=battle_id)
    await state.update_data(round=1)

@dp.callback_query(lambda c: c.data.startswith('firstround;end_time_round'))
async def set_end_time_round(call: types.CallbackQuery, state: FSMContext):
    battle_id = call.data.split(';')[-1]

    await call.message.edit_text(
        '<b>⚙️ Введите время конца раунда в формате: “сегодня в 12:00"</b>\n\nУказывайте время по московскому времени.',
    reply_markup=await kb_return_2page_battlecreate(battle_id))
    await state.set_state(AddActiveBattleEnd.q1)
    await state.update_data(battle_id=battle_id)
    await state.update_data(round=1)

@dp.callback_query(lambda c: c.data.startswith('firstround;min_votes_win'))
async def set_min_votes_win(call: types.CallbackQuery, state: FSMContext):
    battle_id = call.data.split(';')[-1]

    await call.message.edit_text(
        '<b>⚙️ Введите минимальное количество голосов для победы в раунде.</b>\n\nПобеда учитывается, если человек набрал минималку и обогнал соперников.',
    reply_markup=await kb_return_2page_battlecreate(battle_id))
    await state.set_state(AddVoicesToWin.q1)
    await state.update_data(battle_id=battle_id)
    await state.update_data(round=1)

@dp.callback_query(lambda c: c.data.startswith('firstround;returnback'))
async def firstround_menu_returnback(call: types.CallbackQuery, state: FSMContext):
    battle_id = call.data.split(';')[-1]

    battle_info = await db.check_battle_info(battle_id)
    channel_id = battle_info[1]
    post_start_battle = battle_info[17]
    channel_info = await db.check_channel_info_by_id(channel_id)
    channel_tg_id = channel_info[5]
    time_now = datetime.datetime.now().strftime("%H:%M")

    await db.update_battle_channel_link_by_battle_id(battle_id, channel_tg_id)
    if post_start_battle == 0:
        post_start_battle = 'Не нужен'
    else:
        post_start_battle = f'Нужен'

    await call.message.edit_text(f'''<b>🛠️ Создание фото-батла: (1 ШАГ ИЗ 2)</b>

- Название:  {battle_info[3]}
- Ссылка на канал: {channel_tg_id}
- Пост о начале батла: {post_start_battle}
- Приз: {battle_info[6]}
- Время начала: {time_now}
- Время завершения: {battle_info[9]}
- Минимальное кол-во участников: {battle_info[10]}                                                    
    ''', reply_markup=await create_battle_kb(battle_id, channel_id), disable_web_page_preview=True)


    


from aiogram import types
import datetime
from aiogram import Bot
from data.config import *
from aiogram import types, Router
from aiogram.types import Message, InputMediaPhoto
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from data import loader, config
from database import db
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardMarkup
from functions.admin_functions import back_main_menu_channels, delete_channel_func, admin_subscribed_to_channel, check_users_tasks
from handlers.admin_handler import settings_channel
from keyboards.another import cabinet_back, create_battle, statics_back
from keyboards.kb import gocooperation
from keyboards.dev import channel_is_deletes, channels_dev, mailing_dev, nakrutka_menu, start_menu_for_dev, true_channels_delete
from states.classes_states import *
from keyboards import admin_kb, kb
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
import urllib.parse
import aiosqlite
from database.db import name_db
from keyboards import dev
from constants.constants import *
from aiogram import F
from utils.payment import *
from functions.money_converter import *

dp = Router()
bot = loader.start_bot(config.Token)

def encode_url(account_id):
    base_url = 'https://t.me/share/url'
    bot_url = f'https://t.me/{config.bot_name}?start={account_id}'
    text = "👉 Привет, можешь пожалуйста проголосовать за меня в боте?"
    encoded_bot_url = urllib.parse.quote(bot_url, safe='')
    encoded_text = urllib.parse.quote(text, safe='')
    full_url = f"{base_url}?url={encoded_bot_url}&text={encoded_text}"
    return full_url

async def check_sub_cahnnels(channels, user_id):
    for channel in channels:
        chat_member = await bot.get_chat_member(chat_id=channel, user_id=user_id)

        if chat_member.status in ['left', 'kicked']:
            return False
    return True

def subscribe_kb(chat_url, account_id = 0):
    first_time_kb = [[InlineKeyboardButton(text="Канал проекта", url=chat_url)],
                    [InlineKeyboardButton(text="✅ Проверить", callback_data=f"subcribed;{account_id}")], ]

    keyboard_main = InlineKeyboardMarkup(inline_keyboard=first_time_kb)
    return keyboard_main

def get_my_voice_kb(id):
    first_time_kb = [[InlineKeyboardButton(text="✅ Подтверждаю", callback_data=f"getmyvoice;{id}")], ]

    keyboard_main = InlineKeyboardMarkup(inline_keyboard=first_time_kb)
    return keyboard_main

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    if message.chat.type == 'private':
        await state.clear()
        tg_id = message.from_user.id
        username = message.from_user.username
        first_name = message.from_user.first_name
        await db.add_user_if_not_exist(tg_id, first_name, username)

        if tg_id in admins:
            await message.answer(
                "<b>⚙️ Меню управления (главный админ):</b>", reply_markup=start_menu_for_dev())
            return

        admin_exist = await db.check_admin_exist_return_bool(tg_id)
        if admin_exist:
            await message.answer("<b>⚙️ Меню управления:</b>", reply_markup=admin_kb.start_menu_for_admins())
            return

        account_id = message.text.split()
        try:
            if len(account_id) > 1:
                account_id = account_id[1]

                if account_id.startswith("support_"):
                    channel_id = account_id.split("_")[1]
                    channel_info = await db.check_channel_info_by_id(channel_id)
                    name = channel_info[3]
                    await state.update_data(channel_id=channel_id)
                    await state.update_data(channel_info=channel_info)
                    await message.answer(f"💬 <b>Здравствуйте, @{username}!</b>\n\n"
                        f"Вы обращаетесь в службу поддержки канала <b>{name}.</b>\n\n"
                        "Пожалуйста, напишите свой вопрос, можно отправить фото.",
                        parse_mode="HTML")
                    await state.set_state(waiting_for_answers.q3)
                    return

                if account_id.startswith('b'):
                    if '_from' not in account_id:
                        battle_id = account_id[1:]
                    else:
                        account_id = account_id.split('_')
                        battle_id = account_id[0][1:]

                    is_user_blocked = await db.check_battle_block_battle_id_tg_id_exist_return_bool(
                        battle_id, message.from_user.id)
                    if is_user_blocked:
                        await message.answer('Вы заблокированы в этом батле')
                        return

                    battle_info = await db.check_battle_info(battle_id)
                    if battle_info[21] == 0:
                        await message.answer('<b>❌ Набор фото закрыт, попробуйте позже.</b>')
                        return

                    is_user_exist = await db.check_battle_where_battle_id_and_tg_id_exist_and_status_1_return_bool(
                        battle_id, message.from_user.id)
                    if is_user_exist:
                        await message.answer('Вы уже участвуете в этом батле')
                        return

                    if len(account_id) == 2:
                        from_user = account_id[1][4:]
                        if from_user:
                            '''Сохраняем отправленного пользователя'''
                            await db.save_invited_user(message.chat.id, from_user, battle_id)

                    print(account_id, len(account_id), account_id[1][4:])

                    await state.set_state(SendPhotoForBattle.q1)
                    await state.update_data(battle_id=battle_id)
                    await message.answer('<b>📝 Отправьте фото, которое не несет 18+ и оскорбительного характера.</b>')
                    return

                if account_id.startswith('vote'):
                    current_page = None
                    for i in range(len(account_id)):
                        if account_id[i] == 'p':
                            current_page = account_id[i::]
                            break
                    current_page = int(current_page.replace('page', '', 1)) # определенная страница с фотографиями

                    battle_id = account_id.replace('vote', '', 1)
                    for i in range(len(battle_id)):
                        if battle_id[i] == 'p':
                            battle_id = battle_id[0:i]
                            break

                    battle_info = await db.check_battle_info(battle_id)
                    available_count_photo_in_post = battle_info[13]
                    media = await db.all_photo_by_battle(battle_id)
                    current_media = []
                    for i in range((current_page - 1) * available_count_photo_in_post,
                                   current_page * available_count_photo_in_post):
                        try:
                            current_media.append(media[i])
                        except Exception as ex:
                            print("Не хватило фотографии")


                    channel_id = battle_info[1]
                    channel_info = await db.check_channel_info_by_id(channel_id)
                    channel_tg_id = channel_info[2]
                    members_in_post = battle_info[13]
                    all_battle_users = await db.check_all_battle_photos_where_status_1_and_battle_id(battle_id)
                    posts = [all_battle_users[i:i + members_in_post] for i in
                             range(0, len(all_battle_users), members_in_post)]

                    count = 0
                    for index, post in enumerate(posts):
                        post = current_media
                        count += 1
                        media_group = []
                        for user in current_media:
                            media_photo = InputMediaPhoto(media=user[3])
                            media_group.append(media_photo)

                        kbr = InlineKeyboardBuilder()
                        kbr.button(text='🔄 Обновить результаты', callback_data=f'reloadresults;{battle_id};'
                                                                               f'{available_count_photo_in_post};{current_page}')
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
                            kbr.button(text=f'{emoji} - {user[4]}', callback_data=f"voteby;{battle_id};{user[0]}")
                        kbr.adjust(1,2,3,4)
                        break

                    if battle_info[23] == 2:
                        await bot.send_media_group(chat_id=message.chat.id, media=media_group)

                        await bot.send_message(chat_id=message.chat.id, text="<b>🙋 Выберите участника, голос за которого хотите отдать:</b>", reply_markup=kbr.as_markup())
                    else:
                        await bot.send_photo(chat_id=message.chat.id, photo=current_media[-1][3], caption='<b>🙋 Выберите участника, голос за которого хотите отдать:</b>', reply_markup=kbr.as_markup())
                    return

                battle_photos_info = await db.check_battle_photos_where_id1(account_id)
                battle_id = battle_photos_info[2]
                is_exist = await db.check_battle_voices_tg_id_exist_return_bool(tg_id, battle_id)

                user_info = await db.check_user_photo_by_id(account_id, battle_id)
                support_kb = InlineKeyboardBuilder()
                support_kb.button(text='Поддержать участника 🆙', callback_data=f'support_user_votes;{user_info[1]};{battle_id}')
                support_kb.adjust(1)

                if is_exist:
                    await message.answer('<b>🚫 Вы уже проголосовали в этом раунде</b>',
                                         reply_markup=support_kb.as_markup())
                    return

                battle_info = await db.check_battle_info(battle_id)
                channel_link = battle_info[5]
                channel_id = battle_info[1]
                channel_info = await db.check_channel_info_by_id(channel_id)
                channel_tg_id = [channel_info[2]]

                if await check_sub_cahnnels(channel_tg_id, message.from_user.id):
                    await message.answer_photo(photo=battle_photos_info[3],
                                                caption='<b>Вы хотите проголосовать? Изменить или отменить голос уже не будет возможным</b>',
                                                reply_markup=get_my_voice_kb(account_id))
                else:
                    await message.answer("<b>Чтобы проголосовать, необходимо подписаться на канал</b>",
                                         reply_markup=subscribe_kb(channel_link, account_id))
                return

        except Exception as e:
            account_id = 0
            await message.answer("🏘 Меню", reply_markup=kb.start_menu_for_users())
            return

        await message.answer(
            f"👋 Добро пожаловать, @{username}!\n\n"
            "📖 Пожалуйста, ознакомьтесь с <a href='https://telegra.ph/Politika-konfidencialnosti-kanala-PhotoBattliys-10-05'>политикой конфиденциальности</a>.\n\n"
            "<b>💬 Используя бота, вы автоматически соглашаетесь с данными условиями. Приятного использования!</b>",
            reply_markup=kb.start_menu_for_users(),
            parse_mode='HTML',
            disable_web_page_preview=True)

@dp.message(Command("update_info_database"))
async def cmd_update_database_info(message: types.Message, state: FSMContext):
    channels = await db.check_all_channels()
    for channel in channels:
        if channel[8] == '-':
            await db.set_type_send_photos(channel[0], 'admin-chat')

    '''Установка параметра 0 вчерашним счетчиков (таблица battles)'''

@dp.callback_query(lambda c: c.data.startswith('voteby'))
async def vote_in_battle(callback: types.CallbackQuery):
    tg_id = callback.message.from_user.id

    data = callback.data.split(';')
    account_id = data[2]
    battle_photos_info = await db.check_battle_photos_where_id1(account_id)
    battle_id = battle_photos_info[2]
    is_exist = await db.check_battle_voices_tg_id_exist_return_bool(tg_id, battle_id)

    user_info = await db.check_user_photo_by_id(account_id, battle_id)
    support_kb = InlineKeyboardBuilder()
    support_kb.button(text='Поддержать участника 🆙', callback_data=f'support_user_votes;{user_info[1]};{battle_id}')
    support_kb.adjust(1)

    if is_exist:
        await callback.message.answer('<b>🚫 Вы уже проголосовали в этом раунде</b>', reply_markup=support_kb.as_markup())
        return

    battle_info = await db.check_battle_info(battle_id)
    channel_link = battle_info[5]
    channel_id = battle_info[1]
    channel_info = await db.check_channel_info_by_id(channel_id)
    channel_tg_id = [channel_info[2]]

    if await check_sub_cahnnels(channel_tg_id, callback.from_user.id):
        await callback.message.answer_photo(photo=battle_photos_info[3],
                                   caption='<b>Вы хотите проголосовать? Изменить или отменить голос уже не будет возможным</b>',
                                   reply_markup=get_my_voice_kb(account_id))
    else:
        kb = InlineKeyboardBuilder()
        kb.button(text='Ссылка на канал', url=channel_link)
        kb.adjust(1)
        await callback.message.answer("Чтобы проголосовать, необходимо подписаться на канал",
                             reply_markup=kb.as_markup())
    return

@dp.message(lambda message: message.text == "🥇 Рекламные инструменты")
async def sponsors_and_chats(message: types.Message, state: FSMContext):
    kb = InlineKeyboardBuilder()
    kb.button(text='1. Спонсоры (задания)', callback_data='sponsors')
    kb.button(text='2. Изменить обязательный канал для админов', callback_data='change_chat_for_admins')
    kb.button(text='3. Продажа голосов', callback_data='votes_seller')
    kb.adjust(1)
    await message.answer('<b>⚙️ Выберите инструмент:</b>', reply_markup=kb.as_markup())

@dp.callback_query(lambda c: c.data == 'votes_seller')
async def votes_seller_handler(call: types.CallbackQuery, state: FSMContext):
    kb = InlineKeyboardBuilder()
    kb.button(text='Начислить голоса', callback_data='votes_operation;1')
    kb.button(text='Снять голоса', callback_data='votes_operation;0')
    kb.adjust(1)
    await call.message.edit_text('<b>💰 Продажа голосов:</b>', reply_markup=kb.as_markup())

@dp.callback_query(lambda c: c.data.startswith('votes_operation'))
async def votes_operation_handler(call: types.CallbackQuery, state: FSMContext):
    isAdd = int(call.data.split(';')[1])
    if isAdd:
        await call.message.answer('[1/2] Введите tg_id пользователя, которому хотите начислить голоса')
    else:
        await call.message.answer('[1/2] Введите tg_id пользователя, которому хотите снять голоса')
    await state.set_state(VotesOperation.tg_id)
    await state.update_data(isAdd=isAdd)

@dp.message(VotesOperation.tg_id)
async def votes_operation_tg_id_handler(message: types.Message, state: FSMContext):
    user_id = message.text
    if user_id.isdigit():
        await state.update_data(user_id=user_id)
        '''Отправлять батлы'''
        battles_selected = await db.check_all_battles_where_user_id_and_posted(user_id)
        kb = InlineKeyboardBuilder()
        if len(battles_selected):
            for battle in battles_selected:
                kb.button(text=f'{battle[3]}', callback_data=f'add_user_donated_votes;{battle[0]}')

            kb.adjust(1)
            await message.answer('Выберите батл, в который хотите добавить пользователю голосов',
                                 reply_markup=kb.as_markup())
        else:
            await message.answer('Пользователь нигде не участвует')
            await state.clear()
    else:
        await message.answer('Не похоже на tg_id пользователя! Попробуйте еще раз')

@dp.callback_query(lambda c: c.data.startswith('add_user_donated_votes'))
async def add_user_donated_votes(call: types.CallbackQuery, state: FSMContext):
    battle_id = call.data.split(';')[1]
    await state.update_data(battle_id=battle_id)
    await call.message.edit_text('[2/2] Введите количество голосов')
    await state.set_state(VotesOperation.count)

@dp.message(VotesOperation.count)
async def votes_operation_count_handler(message: types.Message, state: FSMContext):
    count = message.text
    data = await state.get_data()
    if count.isdigit():
        await state.update_data(count=count)
        user = await bot.get_chat(chat_id=data.get('user_id'))
        if data.get('isAdd'):
            await message.answer(f'<b>❗ Вы точно хотите начислить {count} голосов пользователю {user.first_name}, @{user.username} ({user.id})</b>\n\nВведите <code>1234</code>, чтобы продолжить')
        else:
            await message.answer(
                f'<b>❗ Вы точно хотите снять {count} голосов пользователю {user.first_name}, @{user.username} ({user.id})</b>\n\nВведите <code>1234</code>, чтобы продолжить')
        await state.set_state(VotesOperation.access)
    else:
        await message.answer('Введено не число! Попробуйте еще раз')

@dp.message(VotesOperation.access)
async def votes_operation_access_handler(message: types.Message, state: FSMContext):
    if message.text == '1234':
        data = await state.get_data()
        if data.get('isAdd'):
            kb = InlineKeyboardBuilder()
            kb.button(text='✅ Да', callback_data='votesOperationAccess;1')
            kb.button(text='❌ Нет', callback_data='votesOperationAccess;0')
            kb.adjust(1)
            await message.answer('❓ Оповестить противников в посте о покупке голосов', reply_markup=kb.as_markup())
        else:
            kb = InlineKeyboardBuilder()
            kb.button(text='Продолжить', callback_data='votesOperationAccess;0')
            kb.adjust(1)
            await message.answer('Для продолжения нажмите кнопку ниже', reply_markup=kb.as_markup())
    else:
        await message.answer('Введите 1234, чтобы продолжить!')

@dp.callback_query(lambda c: c.data.startswith('votesOperationAccess'))
async def votesOperationAccess(call: types.CallbackQuery, state: FSMContext):
    isNotificate = int(call.data.split(';')[1])
    data = await state.get_data()
    battle_id = data.get('battle_id')
    await call.message.edit_text('Операция выполнена!')
    if data.get('isAdd'):
        '''Добавить функционал'''
        if isNotificate:
            user_photo = await db.check_user_photo_by_tg_id(data.get('user_id'), battle_id)
            photos = await db.check_all_battle_photos_where_status_1_and_battle_id_and_number_post(battle_id, user_photo[6])
            for photo in photos:
                kb = InlineKeyboardBuilder()
                kb.button(text='🎁 Купить голоса', callback_data=f'support_payment;{photo[1]};{battle_id}')
                kb.adjust(1)
                if str(data.get('user_id')) != str(photo[1]):
                    await bot.send_message(
                        chat_id=photo[1],
                        text='<b>❌ Кто-то из ваших противников в посте приобрел голоса.\n\nВам нужно действовать быстрее, чтобы не проиграть!</b>',
                        reply_markup=kb.as_markup())
        await db.add_battle_photos_votes_where_tg_id_and_battle_id(data.get('user_id'), data.get('count'), data.get('battle_id'))
        await call.answer(f'✅ {data.get("count")} голосов начислено', show_alert=True)

        battle_id = data.get('battle_id')
        count = data.get('count')
        await db.update_donations(data.get('user_id'), battle_id, count)

    else:
        await db.take_battle_photos_votes_where_tg_id_and_battle_id(data.get('user_id'), data.get('count'), data.get('battle_id'))
        await call.answer(f'✅ {data.get("count")} голосов снято', show_alert=True)

    await state.clear()

@dp.callback_query(lambda c: c.data == 'change_chat_for_admins')
async def change_chat_for_admins(call: types.CallbackQuery):
    kb = InlineKeyboardBuilder()
    if await db.check_admin_channel_from_table():
        channel = await db.check_admin_channel_from_table()
        kb.button(text='Изменить канал', callback_data='set_channel_admins')
        await call.message.edit_text(f'Текущий канал для админов: <b>{channel[1]}</b>', reply_markup=kb.as_markup())
    else:
        kb.button(text='Установить канал', callback_data='set_channel_admins')
        await call.message.edit_text('<b>❌ Канал для админов не установлен. </b>', reply_markup=kb.as_markup())

@dp.callback_query(lambda c: c.data == 'set_channel_admins')
async def set_channel_admins(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(AddAdminChatAdmins.q1)
    await call.message.edit_text('<b>[1/2] Отправьте боту любое сообщение из этого канала.</b>')

@dp.message(AddAdminChatAdmins.q1)
async def add_admin_chat_admins(message: types.Message, state: FSMContext):
    if message.forward_from_chat.type == 'channel':
        chat_id = message.forward_from_chat.id
        title = message.forward_from_chat.title
        await state.update_data(chat_id=chat_id)
        await state.update_data(title=title)
        await state.set_state(AddAdminChatAdmins.q2)
        await message.answer('<b>[2/2] Отправьте ссылку на этот канал.</b>')
    else:
        await message.answer('<b>❌ Это не канал! Попробуйте еще раз.</b>')

@dp.message(AddAdminChatAdmins.q2)
async def adding_admin_channel_link(message: types.Message, state: FSMContext):
    if 'https://t.me/' in message.text:
        url = message.text
        data = await state.get_data()
        chat_id = data.get('chat_id')
        title = data.get('title')
        await db.add_admin_channel_to_table(title, chat_id, url)
        await state.clear()
        await message.answer('<b>✅ Канал для админов добавлен!</b>')
    else:
        await message.answer('<b>❌ Некорректная ссылка, попробуйте еще раз. </b>')

@dp.callback_query(lambda c: c.data == 'sponsors')
async def watch_sponsors(call: types.CallbackQuery):
    kb = InlineKeyboardBuilder()
    sponsors = await db.check_all_sponsors()
    for sponsor in sponsors:
        kb.button(text=sponsor[1], callback_data=f'checksponsor;{sponsor[0]}')

    kb.button(text='Добавить спонсора', callback_data=f'add_sponsor')
    kb.adjust(1)
    await call.message.edit_text('<b>Текущие спонсоры:</b>', reply_markup=kb.as_markup())

@dp.callback_query(lambda c: c.data.startswith('add_sponsor'))
async def add_sponsor_handler(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(AddChannel.q1)
    await call.message.edit_text('<b>⚒️ Чтобы добавить спонсора, выполните следующее:</b>\n\n1. Добавьте бота в админы канала.\n\n2. Отправьте боту любое сообщение из этого канала')

@dp.message(AddChannel.q1)
async def adding_sponsor(message: types.Message, state: FSMContext):
    if message.forward_from_chat.type == 'channel':
        chat_id = message.forward_from_chat.id
        title = message.forward_from_chat.title
        await state.update_data(chat_id=chat_id)
        await state.update_data(title=title)
        await state.set_state(AddChannel.q2)
        await message.answer('<b>[2/2] Отправьте ссылку на этот канал.</b>')
    else:
        await message.answer('<b>❌ Это не канал! Попробуйте еще раз.</b>')

@dp.message(AddChannel.q2)
async def adding_sponsor_link(message: types.Message, state: FSMContext):
    if 'https://t.me/' in message.text:
        url = message.text
        data = await state.get_data()
        chat_id = data.get('chat_id')
        title = data.get('title')
        await db.add_sponsor_to_table(title, chat_id, url)
        await state.clear()
        await message.answer('<b>✅ Канал спонсора добавлен!</b>')
    else:
        await message.answer('<b>❌ Некорректная ссылка, попробуйте еще раз. </b>')

@dp.callback_query(lambda c: c.data.startswith('checksponsor'))
async def check_sponsor(call: types.CallbackQuery):
    spon_id = call.data.split(';')[1]
    info = await db.check_sponsor_by_id(spon_id)
    kb = InlineKeyboardBuilder()
    kb.button(text='🗑️ Удалить спонсора', callback_data=f'delete_sponsor;{spon_id}')
    kb.adjust(1)
    await call.message.edit_text(f'Название канала: {info[1]}', reply_markup=kb.as_markup())

@dp.callback_query(lambda c: c.data.startswith('delete_sponsor'))
async def delete_sponsor(call: types.CallbackQuery):
    spon_id = call.data.split(';')[1]
    await db.delete_sponsor_from_table(spon_id)
    await call.answer('<b>✅ Спонсор удален!</b>', show_alert=True)
    await watch_sponsors(call)

@dp.message(lambda message: message.text == "🧱 Создать фото-батл")
async def handle_profile(message: types.Message, state: FSMContext):
    if message.chat.type == 'private':
        await state.clear()
        tg_id = message.from_user.id
        admin_exist = await db.check_admin_exist_return_bool(tg_id)
        if admin_exist or tg_id in admins:
            if await admin_subscribed_to_channel(message.chat.id):
                await message.answer(
                    "<b>Меню создания фото-батла:</b>",
                    reply_markup=create_battle())
                return
            else:
                admin_channel = await db.check_admin_channel_from_table()
                if admin_channel:
                    admin_link = admin_channel[2]
                    kb = InlineKeyboardBuilder()
                    kb.button(text='Ссылка на канал', url=admin_link)
                    kb.button(text='✅ Проверить', callback_data='check_subscribe_admin')
                    kb.adjust(1)
                    await message.answer('<b>✅ Чтобы пользоваться ботом, нужно подписаться на канал.</b>', reply_markup=kb.as_markup())
                    return
        await message.answer(
            "<b>🚫 Неизвестная команда.</b>")
        return

@dp.callback_query(lambda c: c.data.startswith('mailing_callback'))
async def mailing_callback(call: types.CallbackQuery):
    tg_id = call.data.split(';')[1]
    link_channel = call.data.split(';')[2]
    battle_id = call.data.split(';')[3]
    battle_info = await db.check_battle_info(battle_id)
    await db.update_mailing_user_by_tg_id(tg_id)
    user_data = await db.check_info_users_by_tg_id(tg_id)
    user_info = await db.check_battle_where_battle_id_and_tg_id_exist_and_status_1(battle_id, tg_id)
    kb = InlineKeyboardBuilder()
    if user_data[7]:
        kb.button(text='🔕 Выкл. уведомления', callback_data=f'mailing_callback;{user_data[1]};{link_channel};{battle_id}')
    else:
        kb.button(text='🔔 Вкл. уведомления', callback_data=f'mailing_callback;{user_data[1]};{link_channel};{battle_id}')
    channel_info = await db.check_channel_info_by_id(battle_info[1])
    channel_data = await bot.get_chat(channel_info[2])
    new_postlink = await db.get_user_link_post(tg_id)
    print(new_postlink)
    kb.button(text='Ссылка на пост', url=new_postlink[2])
    if not channel_data.username:
        kb.button(text="Ссылка на канал", url=battle_info[5])
    if await check_users_tasks(battle_id, tg_id):
        kb.button(text="🔥 Хочу больше голосов", callback_data=f'wanted_more_voices;{battle_id};{battle_info[5]}')
    kb.adjust(1)

    text_reply = call.message.html_text
    await call.message.edit_text(text=text_reply, reply_markup=kb.as_markup(), disable_web_page_preview=True)

@dp.callback_query(lambda c: c.data.startswith('back_to_notification'))
async def back_to_notification(call: types.CallbackQuery):
    tg_id = call.message.chat.id
    battle_id = call.data.split(';')[1]
    link_channel = call.data.split(';')[2]
    battle_info = await db.check_battle_info(battle_id)

    user_data = await db.check_info_users_by_tg_id(tg_id)
    user_info = await db.check_battle_where_battle_id_and_tg_id_exist_and_status_1(battle_id, tg_id)

    kb = InlineKeyboardBuilder()
    if user_data[7]:
        kb.button(text='🔕 Выкл. уведомления',
                  callback_data=f'mailing_callback;{user_data[1]};{link_channel};{battle_id}')
    else:
        kb.button(text='🔔 Вкл. уведомления',
                  callback_data=f'mailing_callback;{user_data[1]};{link_channel};{battle_id}')
    channel_info = await db.check_channel_info_by_id(battle_info[1])
    channel_data = await bot.get_chat(channel_info[2])
    new_postlink = await db.get_user_link_post(tg_id)
    print(new_postlink)
    kb.button(text='Ссылка на пост', url=new_postlink[2])
    if not channel_data.username:
        kb.button(text="Ссылка на канал", url=battle_info[5])
    if await check_users_tasks(battle_id, tg_id):
        kb.button(text="🔥 Хочу больше голосов", callback_data=f'wanted_more_voices;{battle_id};{battle_info[5]}')
    kb.adjust(1)

    vote_link = f'https://t.me/{bot_name}?start=vote{battle_id}page{user_info[6]}'

    battle_info = await db.check_battle_info(battle_id)
    min_voice = battle_info[11]
    user_info = await db.check_battle_where_battle_id_and_tg_id_exist_and_status_1(battle_id, tg_id)
    users_in_battle = await db.check_all_battle_photos_where_status_1_and_battle_id_and_number_post(battle_id,
                                                                                                 user_info[6])

    user_voices = user_info[4]

    max_user_voices = 0
    for user in users_in_battle:
        max_user_voices = max(max_user_voices, user[4])

    if max_user_voices == 0 or max_user_voices < min_voice:
        current_voices = min_voice
    else:
        current_voices = max_user_voices

    text_reply = f'''‼️ <b>Вам не хватает {current_voices - user_voices + 1} голосов, чтобы пройти в следующий раунд</b>\n\nЖмите <b>🔥 Хочу больше голосов</b>, чтобы получить больше голосов'''
    await call.message.edit_text(text=text_reply, reply_markup=kb.as_markup(), disable_web_page_preview=True)

@dp.callback_query(lambda c: c.data.startswith('wanted_more_voices'))
async def wanted_more_voices(call: types.CallbackQuery):
    battle_id = call.data.split(';')[1]
    link_channel = call.data.split(';')[2]
    try:
        isShowBack = call.data.split(';')[3]
    except Exception as ex:
        isShowBack = False
    channel_info = await db.check_channel_info_by_link(link_channel)
    status_voiced = await bot.get_user_chat_boosts(chat_id=channel_info[2], user_id=call.message.chat.id)
    status_voiced = status_voiced.boosts

    user_info = await db.check_info_users_by_tg_id(call.message.chat.id)
    user_in_battle_info = await db.check_user_photo_by_tg_id(tg_id=call.message.chat.id, battle_id=battle_id)
    battle_info = await db.check_battle_info(battle_id)

    kb = InlineKeyboardBuilder()
    kb.button(text=f'Использовать доп. голоса', callback_data=f'add_voices_use;{battle_id}')
    if call.from_user.is_premium:
        if status_voiced:
            kb.button(text='✅ Проголосовать за канал', callback_data=f'voice_to_channel_premium;{battle_id};{link_channel}')
        else:
            kb.button(text='❌ Проголосовать за канал', callback_data=f'voice_to_channel_premium;{battle_id};{link_channel}')
    if await db.check_all_sponsors() and not user_in_battle_info[10]:
        kb.button(text='❌ Подписаться на спонсоров', callback_data=f'spon_subs;{battle_id};{link_channel}')
    if battle_info[21]:
        kb.button(text='♾️ Пригласить друга на фото-батл', callback_data=f'invite_friend;{battle_id};{link_channel}')

    if not isShowBack:
        kb.button(text='🔙 Назад', callback_data=f'back_to_notification;{battle_id};{link_channel}')
    kb.adjust(1)

    await call.message.edit_text(text=f'''<b>📝 Вы можете получить дополнительные голоса, выполнив задания:</b>\n\n💰 Накопленные голоса: {user_info[8]}''', reply_markup=kb.as_markup())

@dp.callback_query(lambda c: c.data.startswith('invite_friend'))
async def invite_friend_handler(call: types.CallbackQuery):
    battle_id = call.data.split(';')[1]
    link_channel = call.data.split(';')[2]
    kb = InlineKeyboardBuilder()

    base_url = 'https://t.me/share/url'
    share_url = f'https://t.me/{bot_name}?start=b{battle_id}_from{call.message.chat.id}'
    text = f"Привет, можешь по-участвовать в фото-батле, приз выдают за победу в финале"
    encoded_text = urllib.parse.quote(text, safe='')
    encoded_url = urllib.parse.quote(share_url, safe='')
    full_url = f"{base_url}?url={encoded_url}&text={encoded_text}"

    kb.button(text='Пригласить друга', url=full_url)
    # kb.button(text='✅ Проверить', callback_data=f'check_invites;{battle_id};{link_channel}')
    kb.button(text='🔙 Назад', callback_data=f'wanted_more_voices;{battle_id};{link_channel}')
    kb.adjust(1)
    await call.message.edit_text('<b>📝 Задание - Пригласить друга на фото-батл:</b>\n\n✅ За каждого друга, который отправит фото и наберет 3 голоса будет начислено 3 голоса', reply_markup=kb.as_markup())

@dp.callback_query(lambda c: c.data.startswith('check_invites'))
async def check_invites_handler(call: types.CallbackQuery):
    '''Проверить'''
    battle_id = call.data.split(';')[1]
    link_channel = call.data.split(';')[2]
    user_id = call.message.chat.id
    users_invited = await db.check_invited_friends(user_id, battle_id)
    save_user = ''
    if users_invited:
        vote_counter = 0
        user_battle_info = await db.check_user_photo_by_tg_id(user_id, battle_id)
        for user in users_invited:
            if str(user_battle_info[11]) != str(user[1]):
                vote_counter += 1
            else:
                save_user_battle_info = await db.check_user_photo_by_tg_id(user[1], battle_id)
                if save_user_battle_info[6] == 0 and save_user_battle_info[12] == 0:
                    vote_counter += 1
                    await db.update_give_votes_battle_photos(user[1], battle_id)
                save_user = user[1]

        voices_added = vote_counter * 3

        await db.clear_invites_but_save_one(user_id, battle_id, save_user)
        await db.update_add_voices_users(voices_added, user_id)
        user_info = await db.check_info_users_by_tg_id(user_id)
        kb = InlineKeyboardBuilder()
        kb.button(text=f'Использовать накопленные голоса', callback_data=f'add_voices_use;{battle_id}')
        if await check_users_tasks(battle_id, user_id):
            kb.button(text="🔥 Хочу больше голосов", callback_data=f'wanted_more_voices;{battle_id};{link_channel}')
        kb.adjust(1)
        if voices_added != 0:
            await call.message.edit_text(f'✅ Начислено {voices_added} голосов за {len(users_invited)} друзей\n\n💰 Ваш баланс голосов: {user_info[8]} шт', reply_markup=kb.as_markup())
        else:
            await call.message.edit_text(f'<b>❌ Кто-то из пользователей уже перешел по вашей ссылке!</b>', reply_markup=kb.as_markup())
    else:
        await call.message.answer('<b>❌ Не выполнено, пока никто не перешел по вашей ссылке.</b>')

@dp.callback_query(lambda c: c.data.startswith('spon_subs'))
async def sponsors_subscribe(call: types.CallbackQuery):
    battle_id = call.data.split(';')[1]
    link_channel = call.data.split(';')[2]
    user_battle_info = await db.check_user_photo_by_tg_id(tg_id=call.message.chat.id, battle_id=battle_id)

    if user_battle_info[10]:
        await call.answer('❌ Вы уже выполнили это задание!', show_alert=True)
        return

    kb = InlineKeyboardBuilder()
    sponsors = await db.check_all_sponsors()
    for sponsor in sponsors:
        kb.button(text=sponsor[1], url=sponsor[2])
    kb.button(text='✅ Проверить', callback_data=f'check_subscribe_sponsors;{battle_id};{link_channel}')
    kb.button(text='🔙 Назад', callback_data=f'wanted_more_voices;{battle_id};{link_channel}')
    kb.adjust(1)
    await call.message.edit_text('<b>📝 Задание - Подписаться на спонсоров:</b>\n\n✅ За выполнение будет выдано 2 голоса', reply_markup=kb.as_markup())

@dp.callback_query(lambda c: c.data.startswith('check_subscribe_sponsors'))
async def check_subscribe_sponsors(call: types.CallbackQuery):
    battle_id = call.data.split(';')[1]
    link_channel = call.data.split(';')[2]
    sponsors = await db.check_all_sponsors()
    for sponsor in sponsors:
        print(sponsor[3])
        member = await call.message.bot.get_chat_member(sponsor[3], user_id=call.message.chat.id)
        if member.status == 'left':
            await call.message.answer('❌ Не выполнено')
            return


    await db.update_user_sponsor_data(call.message.chat.id, battle_id)
    await db.update_add_voices_users(2, call.message.chat.id)

    user_info = await db.check_info_users_by_tg_id(call.message.chat.id)
    kb = InlineKeyboardBuilder()
    kb.button(text=f'Использовать доп. голоса', callback_data=f'add_voices_use;{battle_id}')
    if await check_users_tasks(battle_id, call.message.chat.id):
        kb.button(text="🔥 Хочу больше голосов", callback_data=f'wanted_more_voices;{battle_id};{link_channel}')
    kb.adjust(1)
    await call.message.edit_text(f'✅ Начислено 2 голосов за подписку\n\n💰 Ваш баланс голосов: {user_info[8]} шт',
                                 reply_markup=kb.as_markup())

@dp.callback_query(lambda c: c.data.startswith('voice_to_channel_premium'))
async def voice_to_channel_premium(call: types.CallbackQuery):
    battle_id = call.data.split(';')[1]
    link_channel = call.data.split(';')[2]
    channel_info = await db.check_channel_info_by_link(link_channel)
    info = await bot.get_chat(channel_info[2])
    try:
        channel_boost = await bot.get_user_chat_boosts(chat_id=channel_info[2], user_id=call.message.chat.id)
        if channel_boost.boosts:
            await call.answer('❌ Вы уже проголосовали за канал', show_alert=True)
            return
    except Exception as ex:
        print('Ошибка:', ex)

    boost_link = f'https://t.me/boost?c={str(info.id).replace("-100", "")}'

    kb = InlineKeyboardBuilder()
    kb.button(text='Проголосовать', url=boost_link)
    kb.button(text='✅ Проверить', callback_data=f'check_boost_chan;{info.id};{battle_id}')
    kb.button(text='🔙 Назад', callback_data=f'wanted_more_voices;{battle_id};{link_channel}')
    kb.adjust(1)
    await call.message.edit_text('<b>📝 Задание - Проголосовать за канал:</b>\n\n✅ За выполнение будет выдано 3 голоса',
                                 reply_markup=kb.as_markup())

@dp.callback_query(lambda c: c.data.startswith('check_boost_chan'))
async def check_boost_channel(call: types.CallbackQuery):
    channel_id = call.data.split(';')[1]
    battle_id = call.data.split(';')[2]
    channel_data = await db.check_channel_where_channel_id(channel_id)
    link_channel = channel_data[5]
    try:
        channel_boost = await bot.get_user_chat_boosts(chat_id=channel_id, user_id=call.message.chat.id)
        if channel_boost.boosts:

            await db.update_add_voices_users(3, call.message.chat.id)
            user_info = await db.check_info_users_by_tg_id(call.message.chat.id)
            kb = InlineKeyboardBuilder()
            kb.button(text=f'Использовать доп. голоса ({user_info[8]} шт)', callback_data=f'add_voices_use;{battle_id}')
            if await check_users_tasks(battle_id, call.message.chat.id):
                kb.button(text="🔥 Хочу больше голосов",
                          callback_data=f'wanted_more_voices;{battle_id};{link_channel}')
            kb.adjust(1)
            await call.message.edit_text(text=f'✅ Начислено 3 голосов\n\n💰 Ваш баланс голосов: {user_info[8]} шт', reply_markup=kb.as_markup())
            # who_invited = await db.find_invited_from_friend(call.message.chat.id, battle_id)
            # if who_invited[2]:
            #     '''Отправить сообщение и увеличить голоса'''
            #     await db.update_add_voices_users(1, who_invited[2])
            return
        else:
            await call.answer('❌ Не выполнено')
    except Exception as ex:
        print('Ошибка:', ex)

@dp.callback_query(lambda c: c.data.startswith('add_voices_use'))
async def add_voices_use(call: types.CallbackQuery):
    battle_id = call.data.split(';')[1]
    user_info = await db.check_info_users_by_tg_id(call.message.chat.id)
    votes = user_info[8]
    tg_id = user_info[1]
    if not votes:
        await call.answer('У вас больше нет голосов!', show_alert=True)
    await db.use_add_voices(votes, battle_id, tg_id)
    await call.answer('Вы использовали доп.голоса', show_alert=True)
    text_edit = call.message.html_text
    print(text_edit)
    text_edit = text_edit.replace(f'{votes}', '0')
    print(text_edit)
    try:
        await call.message.edit_text(text=text_edit, reply_markup=call.message.reply_markup)
    except Exception as ex:
        print('Менять нечего!')


@dp.callback_query(lambda c: c.data.startswith('create_battle'))
async def go_create_battle(call: types.CallbackQuery):
    tg_id = call.from_user.id
    channels = await db.checkk_all_channels_where_tg_id(tg_id)
    await call.message.edit_text('<b> ⚙️ Выберите канал для создания фото-батла:</b>', reply_markup=await back_main_menu_channels(channels))

@dp.callback_query(lambda c: c.data.startswith('backmainmenu'))
async def back_from_create_battle(call: types.CallbackQuery):
    await call.message.edit_text('<b>Меню создания фото-батла:</b>', reply_markup=create_battle())

@dp.callback_query(lambda c: c.data.startswith('backtochannels'))
async def back_from_create_battle(call: types.CallbackQuery):
    tg_id = call.from_user.id
    channels = await db.checkk_all_channels_where_tg_id(tg_id)
    await call.message.edit_text('<b> ⚙️ Выберите канал для создания фото-батла:</b>', reply_markup=await back_main_menu_channels(channels))

@dp.callback_query(lambda c: c.data.startswith('back_from_addchannel'))
async def go_create_battle(call: types.CallbackQuery):
    tg_id = call.from_user.id
    channels = await db.checkk_all_channels_where_tg_id(tg_id)
    await call.message.edit_text('<b> ⚙️ Выберите канал для создания фото-батла: </b>', reply_markup=await back_main_menu_channels(channels))

@dp.message(lambda message: message.text == "🤝 Сотрудничество")
async def handle_profile(message: types.Message, state: FSMContext):
    if message.chat.type == 'private':
        await state.clear()
        tg_id = message.from_user.id
        if tg_id in admins:
            await message.answer(
                "<b>🚫 У вас нет доступа к этому разделу.</b>")
            return
        admin_exist = await db.check_admin_exist_return_bool(tg_id)
        if admin_exist:
            await message.answer(
                "<b>🚫 У вас нет доступа к этому разделу.</b>")
            return
    await message.answer(f"""<b>Сотрудничество с ботом 📸</b>\n\nСделайте фото батлы проще и удобнее вместе с нами!\n\n<b>✨ Что вы получаете бесплатно:</b>\n\n- Прием фотографий и поддержка в одном месте   \n- Автоматизация публикации постов и итогов \n- Уведомления о ходе батла \n\n<b>Убедимся, что у вас есть канал для батлов. Готовы начать? 👌</b>""", reply_markup=gocooperation(), parse_mode="HTML")

@dp.message(lambda message: message.text == "🧑‍💼 Каналы")
async def handle_profile(message: types.Message, state: FSMContext):
    if message.chat.type == 'private':
        await state.clear()
        tg_id = message.from_user.id
        if tg_id in admins:
            # await db.update_channels_in_table()

            channels, total_moments = await get_paginated_items34(0)
            items_kb = await build_items_kb34(channels, 0, total_moments)
            message = await message.answer(
                "<b>Список каналов, использующие бота:</b>",
                reply_markup=items_kb.as_markup())

            await db.update_info_watcher_channels(message.message_id)
            return
        admin_exist = await db.check_admin_exist_return_bool(tg_id)
        if admin_exist:
            await message.answer(
                "<b>🚫 Неизвестная команда.</b>")
            return

        await message.answer(
            "<b>🚫 Неизвестная команда.</b>")
        return

async def get_paginated_items34(page: int = 0):
    channels = await db.check_all_channels()
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    return channels[start:end], len(channels)

async def build_items_kb34(channels, page, total_moments):
    categories_kb = InlineKeyboardBuilder()
    all_channels = await db.check_all_channels()
    for channel in channels:
        channel_info = await db.check_channel_info_by_id(channel[0])
        name = channel_info[3]
        try:
            # await bot.get_chat(channel_info[2])
            categories_kb.button(text=f"{name}", callback_data=f'channelcheckitem;{channel[0]};{page}')
        except Exception as ex:
            print(f'Бот был удален из канала {name}')

    categories_kb.adjust(1)
    buttons = [
        InlineKeyboardButton(text='⏮️', callback_data=f'channelspageitems;{0}'),
        InlineKeyboardButton(text='◀️', callback_data=f'channelspageitems;{page-1}'),
        InlineKeyboardButton(text=f'{page+1}/{(total_moments // ITEMS_PER_PAGE) + 1}', callback_data='current'),
        InlineKeyboardButton(text='▶️', callback_data=f'channelspageitems;{page+1}'),
        InlineKeyboardButton(text='⏭️', callback_data=f'channelspageitems;{len(all_channels) // 10 if len(all_channels) % 10 != 0 else len(all_channels) // 10 - 1}')
    ]

    categories_kb.row(*buttons)
    back_button = InlineKeyboardButton(text='🔙 Назад', callback_data='cancel_menu_channels')
    categories_kb.row(back_button)

    return categories_kb

@dp.callback_query(lambda c: c.data.startswith('channelcheckitem'))
async def battle_check_item_handler(call: types.CallbackQuery):
    current_page = call.data.split(';')[2]
    channel_id = call.data.split(';')[1]
    kb = InlineKeyboardBuilder()
    channel_info = await db.check_channel_info_by_id(channel_id)
    channel_data = await bot.get_chat(channel_info[2])
    admins = await channel_data.get_administrators()
    creator = ''
    for admin in admins:
        if admin.status == 'creator':
            creator = admin
    name = channel_info[3]
    link = channel_info[5]

    kb.button(text='⚔️ Активные наборы на фото-батлы', callback_data=f'channel_battles;{channel_id}')
    kb.button(text='🗑️ Удалить канал', callback_data=f'channel_delete;{channel_id}')
    kb.button(text='🔙 Назад', callback_data=f'backtochannel_list;{current_page}')
    kb.adjust(1)
    await call.message.edit_text(f'''<b>Канал {name}</b>\n\nСсылка: {link}\n\nВладелец канала @{creator.user.username}''',disable_web_page_preview=True, reply_markup=kb.as_markup())

@dp.callback_query(lambda c: c.data.startswith('channel_battles'))
async def show_battles(call: types.CallbackQuery):
    data = call.data.split(';')[-1]

    async with aiosqlite.connect(name_db) as db:
        async with db.execute(f'''SELECT * FROM battles WHERE (channel_id = {data} AND status = 0)''') as cursor:
            battles = await cursor.fetchall()

            kb = InlineKeyboardBuilder()
            for battle in battles:
                kb.button(text=f'{battle[3]}', callback_data=f'chosed_battle;{battle[0]}')

            kb.button(text='🔙 Назад', callback_data=f'channelcheckitem;{data}')
            kb.adjust(1)
            await call.message.edit_text(f'''Список наборов:''',
                                         reply_markup=kb.as_markup())

@dp.callback_query(lambda c: c.data.startswith('chosed_battle'))
async def show_current_battle(call: types.CallbackQuery):
    battle_id = call.data.split(';')[-1]
    async with aiosqlite.connect(name_db) as db:
        async with db.execute(f'''SELECT * FROM battles WHERE id = {battle_id}''') as cursor:
            current_battle = await cursor.fetchall()
            current_battle = current_battle[0]

    title = current_battle[3]
    status = current_battle[14]
    channel_id = current_battle[1]

    kb = InlineKeyboardBuilder()

    if status:
        kb.button(text=f'⚔️ Удалить из каталога', callback_data=f'updatestatuscatalog;1;{battle_id};0')
    else:
        kb.button(text=f'⚔️ Выставить в каталог "наборы на фото-батлы"', callback_data=f'updatestatuscatalog;1;{battle_id};1')
    kb.button(text='🗑️ Удалить батл', callback_data=f'updatestatuscatalog;2;{battle_id};0')
    kb.button(text='🔙 Назад', callback_data=f'channel_battles;{channel_id}')
    kb.adjust(1)

    await call.message.edit_text(f'Батл {title}',
                                 reply_markup=kb.as_markup())

class Form(StatesGroup):
    waiting_for_password = State()
    status:int
    battle_id:int
    typeDo:int

@dp.callback_query(lambda c: c.data.startswith('updatestatuscatalog'))
async def start_password(call: types.CallbackQuery, state: FSMContext):
    data = call.data.split(';')
    Form.status = data[-1]
    Form.battle_id = data[-2]
    Form.typeDo = data[-3]
    await state.set_state(Form.waiting_for_password)
    kb = InlineKeyboardBuilder()
    kb.button(text='🔙 Назад', callback_data=f'chosed_battle;{call.data.split(";")[-2]}')
    await call.message.edit_text("✅ Введите пароль, чтобы удалить/выставить:", reply_markup=kb.as_markup())

@dp.message(Form.waiting_for_password)
async def process_password(message: types.Message, state: FSMContext):
    password = message.text
    await bot.delete_message(message.chat.id, message.message_id - 1)
    await message.delete()
    if password == "1234":
        kb = InlineKeyboardBuilder()
        kb.button(text="🏡 На главную", callback_data="tohome")
        await update_status(battle_id=Form.battle_id, status=Form.status, typeDo=Form.typeDo)
        await message.answer("Батл успешно выставлен/удален", reply_markup=kb.as_markup())
    else:
        await message.answer("Пароль неверный. Попробуйте еще раз.")

    await state.clear()

@dp.callback_query(lambda c: c.data.startswith('tohome'))
async def go_home(call: types.CallbackQuery):
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await call.message.answer(
        f"👋 Добро пожаловать, @{call.message.chat.username}!\n\n",
        reply_markup=dev.start_menu_for_dev(),
        parse_mode='HTML',
        disable_web_page_preview=True)

async def update_status(battle_id, status, typeDo):
    async with aiosqlite.connect(name_db) as db:
        if typeDo == "2":
            '''Удаление из таблицы'''
            await db.execute('DELETE FROM battles WHERE id = ?', (battle_id,))
        else:
            await db.execute('UPDATE battles SET status = ? WHERE id = ?', (status, battle_id))
        await db.commit()

@dp.callback_query(lambda c: c.data.startswith('backtochannel_list'))
async def back_to_channel_list_handler(call: types.CallbackQuery):
    page = int(call.data.split(';')[1]) if ';' in call.data else 0
    channels, total_channels = await get_paginated_items34(page)
    categories_kb = await build_items_kb34(channels, page, total_channels)
    message = await call.message.edit_text(
        text=f"<b>Список каналов, использующие бота:</b>", reply_markup=categories_kb.as_markup())
    await db.update_info_watcher_channels(message.message_id)

@dp.callback_query(lambda c: c.data.startswith('cancel_delete_channel'))
async def cancel_delete_channel_handler(call: types.CallbackQuery):
    await battle_check_item_handler(call)

@dp.callback_query(lambda c: c.data.startswith('channel_delete'))
async def back_to_channel_list_handler(call: types.CallbackQuery):
    channel_id = call.data.split(';')[1]
    await call.message.edit_text('Вы хотите удалить канал?', reply_markup=channels_dev(channel_id))

@dp.callback_query(lambda c: c.data.startswith('channels_deleted_45'))
async def delete_channel_func(call: types.CallbackQuery):
    channel_id = call.data.split(';')[1]
    await call.message.edit_text('Подтверждаете?', reply_markup=true_channels_delete(channel_id))

async def delete_channel_fromlist(call: types.CallbackQuery, channel_id):
    channel_id = call.data.split(';')[1]
    await db.delete_channel_by_id(channel_id)
    tg_id = call.from_user.id
    channels = await db.checkk_all_channels_where_tg_id(tg_id)
    await call.message.edit_text('<b>✅ Канал удален </b>', reply_markup=channel_is_deletes(channels))

@dp.callback_query(lambda c: c.data.startswith('channel_true'))
async def approve_delete_channel_handler2(callback: types.CallbackQuery):
    channel_id = callback.data.split(';')[1]
    await delete_channel_fromlist(callback, channel_id)

@dp.callback_query(lambda c: c.data.startswith('back_to_channel'))
async def cancel_mailing(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text('<b>⚙️Меню управления (главный админ)</b>')

@dp.callback_query(lambda c: c.data.startswith('addchannel'))
async def add_channel_func(callback_query: types.CallbackQuery, state: FSMContext):
    await cooperation(callback_query.message, state)
    await callback_query.answer()

@dp.callback_query(lambda c: c.data == 'addchannel')
async def add_channel_handler(callback: types.CallbackQuery, state: FSMContext):
    await add_channel_func(callback, state)

@dp.message(lambda message: message.text == "✅ Приступим")
async def cooperation(message: types.Message, state: FSMContext):
    if message.chat.type == 'private':
        tg_id = message.from_user.id
        if tg_id in admins:
            await state.set_state(stats_bot.dev2)
            await message.answer("<b>🚫 Неизвестная команда.</b>",)
            return
        admin_exist = await db.check_admin_exist_return_bool(tg_id)
        if admin_exist:
            await state.set_state(stats_bot.admin2)
            await message.answer("<b>🚫 Неизвестная команда.</b>",)
            return
    # await state.set_state(AddChannel.q1)

    if not await db.check_temp_channels_by_user(message.chat.id):
        await db.add_new_user_temp_channels(message.chat.id)

    kb = InlineKeyboardBuilder()
    kb.button(text='Добавить канал', url=f'http://t.me/{bot_name}?startchannel&admin=manage_chat+delete_messages+manage_video_chats+restrict_members+promote_members+change_info+invite_users+post_messages+edit_messages+pin_messages+manage_topics')
    kb.button(text='🔙 Назад', callback_data='backtochannels')
    kb.adjust(1)

    try:
        await message.edit_text(
    "<b>Добавление канала 📝</b>\n\n"
    "Чтобы подключить канал нажмите кнопку ниже:", reply_markup=kb.as_markup(), show_alert=True,
        disable_web_page_preview=True)
    except Exception as ex:
        await message.answer(
    "<b>Добавление канала 📝</b>\n\n"
    "Чтобы подключить канал нажмите кнопку ниже:", reply_markup=kb.as_markup(), show_alert=True,
        disable_web_page_preview=True)

@dp.callback_query(lambda c: c.data.startswith('nakrutka'))
async def create_mailing(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('<b>[1/2] Введите tg_id пользователя, которому хотите накрутить голоса.</b>')
    await state.set_state(AddVoices.q1)

@dp.callback_query(lambda c: c.data.startswith('cancel_nakrutka'))
async def cancel_mailing(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text('<b>⚙️Меню управления (главный админ)</b>')

@dp.callback_query(lambda c: c.data.startswith('cancel_menu_channels'))
async def cancel_mailing(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text('<b>⚙️Меню управления (главный админ)</b>')

@dp.message(AddVoices.q1)
async def add_voices_handler(message: types.Message, state: FSMContext):
    tg_id = message.text
    if tg_id.isdigit():
        await state.update_data(tg_id=tg_id)
        await message.answer('<b>[2/2] Введите кол-во голосов.</b>')
        await state.set_state(AddVoices.q2)
    else:
        await message.answer('<b>❌ Не похоже на tg_id, попробуйте ещё раз.</b>')

@dp.message(AddVoices.q2)
async def add_voices_handler(message: types.Message, state: FSMContext):
    count = message.text
    if count.isdigit():
        count = int(count)
        if count > 0 and count < 4:
            data = await state.get_data()
            tg_id = data.get('tg_id')
            await db.add_battle_photos_votes_where_tg_id(tg_id, count)
            await message.answer(f'<b>✅ {count} голосов добавлено.</b>')
            await state.clear()
        else:
            await message.answer('<b>❌ За раз максимум можно накрутить до 3 голосов.</b>')
    else:
        await message.answer('<b>❌ Не похоже на число, попробуйте ещё раз.</b>')

@dp.callback_query(lambda c: c.data.startswith('backtosettings'))
async def option_channel_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    channel_id = callback.data.split(';')[1]
    await settings_channel(callback, channel_id)

@dp.message(lambda message: message.text == "💬 Рассылка")
async def handle_profile(message: types.Message, state: FSMContext):
    if message.chat.type == 'private':
        await state.clear()
        tg_id = message.from_user.id
        if tg_id in admins:
            await message.answer(
                "<b>⚙️ Выберите действие:</b>",
                reply_markup=mailing_dev())
            await state.set_state("rassilka.admin_action")
            return
        admin_exist = await db.check_admin_exist_return_bool(tg_id)
        if admin_exist:
            await message.answer(
                "<b>🚫 Неизвестная команда.</b>")
            return
        await message.answer(
            "<b>🚫 Неизвестная команда.</b>")
        return
@dp.callback_query(lambda c: c.data.startswith('cancel_mailing'))
async def cancel_mailing(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text('<b>⚙️Меню управления (главный админ)</b>')

@dp.callback_query(lambda c: c.data.startswith('chose_mailing_type'))
async def chose_mailing_type(call: types.CallbackQuery, state: FSMContext):
    kb = InlineKeyboardBuilder()
    kb.button(text='1. Пересылка поста - ✅ TG PREM EMODZI', callback_data='create_mailling_post')
    kb.button(text='2. Свое сообщение  - 🚫 TG PREM EMODZI', callback_data='create_mailling_text')
    kb.adjust(1)
    await call.message.edit_text('⚒️ Выберите метод рассылки:', reply_markup=kb.as_markup())

@dp.callback_query(lambda c: c.data.startswith('create_mailling_post'))
async def create_mailling_post(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer('<b>Перешлите необходимый пост</b>')
    await state.set_state(MailingPost.q1)
@dp.callback_query(lambda c: c.data.startswith('create_mailling_text'))
async def create_mailing_text(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer('<b>[1/2] Введите сообщение для рассылки</b>')
    await state.set_state(Mailing.q1)

@dp.message(MailingPost.q1)
async def mailing_post(message: types.Message, state: FSMContext):
    '''Пересылка поста всем'''
    print('Попал сюда')
    mess_id = message.message_id
    await state.clear()
    await send_forward_to_all_users(message.chat.id, mess_id)
    await message.answer("<b>🏁 Рассылка завершена.</b>")
@dp.message(Mailing.q1)
async def mailing_handler(message: types.Message, state: FSMContext):
    await state.update_data(message_id=message.message_id)
    await state.set_state(Mailing.q2)
    await message.answer('<b>[2/2] Введите кнопки в формате:</b> Текст;ссылка\n\nКаждую кнопку с новой строки \nЕсли не нужны кнопки, то 0')
@dp.message(Mailing.q2)
async def mailing_handler_q2(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    await state.clear()
    markup = InlineKeyboardBuilder()
    mess_id = user_data['message_id']

    if message.text.strip() != '0':
        buttons = message.text.strip().split('\n')
        for button in buttons:
            if ';' in button:
                btn_text, btn_url = map(str.strip, button.split(';', 1))
                if btn_url.startswith('https://'):
                    markup.button(text=btn_text, url=btn_url)

                else:
                    await message.answer(f"<b>❌ Ошибка: ссылка должна начинаться с 'https://'. Проверьте: {btn_url}</b>")
                    return
        markup.adjust(1)
    await send_copy_to_all_users(message.chat.id, mess_id, markup.as_markup())
    await message.answer("<b>🏁 Рассылка завершена.</b>")
async def send_copy_to_all_users(chat_id, message_id, reply_markup=None):
    user_ids = await db.get_all_users_tg_id()
    count = 0
    for user_id in user_ids:
        try:
            if reply_markup:
                await bot.copy_message(
                    chat_id=user_id[0],
                    from_chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=reply_markup)
            else:
                await bot.copy_message(
                    chat_id=user_id[0],
                    from_chat_id=chat_id,
                    message_id=message_id)
        except Exception as e:
            count +=1
            print(e)
    await db.update_blocked_count(count)

async def send_forward_to_all_users(chat_id, message_id, reply_markup=None):
    user_ids = await db.get_all_users_tg_id()
    count = 0
    for user_id in user_ids:
        try:
            if reply_markup:
                await bot.forward_message(
                    chat_id=user_id[0],
                    from_chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=reply_markup)
            else:
                await bot.forward_message(
                    chat_id=user_id[0],
                    from_chat_id=chat_id,
                    message_id=message_id)
        except Exception as e:
            count += 1
            print(e)
    await db.update_blocked_count(count)
async def send_text_with_buttons_to_all_users(text: str, markup):
    all_users = await db.get_all_users_tg_id()
    if markup is None:
        for user in all_users:
            try:
                await bot.send_message(user[0], text, parse_mode='HTML')
            except Exception as e:
                print(e)
    else:
        for user in all_users:
            try:
                await bot.send_message(user[0], text, reply_markup=markup, parse_mode='HTML')
            except Exception as e:
                print(e)
async def send_photo_with_buttons_to_all_users(photo_id: str, caption: str, markup):
    all_users = await db.get_all_users_tg_id()
    if markup is None:
        for user in all_users:
            try:
                await bot.send_photo(user[0], photo_id, caption=caption, parse_mode='HTML')
            except:
                pass
    else:
        for user in all_users:
            try:
                await bot.send_photo(user[0], photo_id, caption=caption, reply_markup=markup, parse_mode='HTML')
            except Exception as ex:
                print(ex)

@dp.message(lambda message: message.text == "📱 Мой кабинет")
async def handle_profile(message: types.Message):
    tg_id = message.from_user.id
    profile_info = await db.check_info_users_by_tg_id(tg_id)
    count_wins = await db.check_count_battle_winners_where_tg_id(tg_id)

    profile_message = f"""<b>👨‍💻 Ваш кабинет:</b>\n\n<b>🔑 Ваш TG ID:</b> <code>{tg_id}</code>\n\n<b>📊 Статистика:</b>\n\t<b>- Количество выигранных батлов:</b> {count_wins[0]}\n\t<b>- Всего голосов:</b> {profile_info[6]}"""
    await message.answer(profile_message, parse_mode="HTML", reply_markup=cabinet_back())

@dp.message(lambda message: message.text == '⚔️ Принять участие в батле')
async def join_to_the_battle_main_admin_handler(message: Message):
    all_admin_battles = await db.check_all_battles_where_creator_user_id(admins[0])
    kb = InlineKeyboardBuilder()
    isEmpty = True
    for battle in all_admin_battles:
        if battle[21] and battle[14]:
            isEmpty = False
            kb.button(text=battle[3], url=f'https://t.me/{bot_name}?start=b{battle[0]}')

    kb.adjust(1)
    if not isEmpty:
        await message.answer('Выберите батл для участия', reply_markup=kb.as_markup())
    else:
        await message.answer('<b>❌ Набор фото закрыт, попробуйте позже.</b>')

@dp.message(lambda message: message.text == '📊 Статистика бота')
async def statics(message: types.Message, state: FSMContext):
    if message.chat.type == 'private':
        tg_id = message.from_user.id
        blocked = await db.check_blocked_count_where_id_1()
        users = await db.check_len_users()
        items = await db.check_all_battles_where_status_1()

        active_battles = await db.check_all_battles_where_all_ran_return_id()

        await message.answer(f"""<b>📊 Статистика бота "Помощник фото-батлов | Участвовать"</b>\n\n- Количество пользователей: {users}\n\n- Активные батлы: {len(active_battles)}\n\n<b>ℹ️ Ваша статистика представлена в личном кабинете</b>""",reply_markup=statics_back(),parse_mode="HTML",)

@dp.message(lambda message: message.text == '🔙 Назад')
async def statics(message: types.Message, state: FSMContext):
    if message.chat.type == 'private':
        await state.clear()
        tg_id = message.from_user.id
        if tg_id in admins:
            await state.set_state(stats_bot.dev2)
            await message.answer(
                "<b>⚙️Меню управление (главный админ):</b>",
                reply_markup=start_menu_for_dev())
            return

        admin_exist = await db.check_admin_exist_return_bool(tg_id)
        if admin_exist:
            await state.set_state(stats_bot.admin2)
            await message.answer("<b>⚙️Меню управление:</b>", reply_markup=admin_kb.start_menu_for_admins())
            return
    username = message.from_user.username
    await state.set_state(stats_bot.user2)
    await message.answer(
            f"👋 Добро пожаловать, @{username}!\n\n"
            "📖 Пожалуйста, ознакомьтесь с <a href='https://telegra.ph/Politika-konfidencialnosti-kanala-PhotoBattliys-10-05'>политикой конфиденциальности</a>.\n\n"
            "<b>💬 Используя бота, вы автоматически соглашаетесь с данными условиями. Приятного использования!</b>",reply_markup=kb.start_menu_for_users(),parse_mode='HTML',disable_web_page_preview=True)

@dp.message(lambda message: message.text == '🆘 Тех. поддержка')
async def tech_support_start(message: Message, state: FSMContext):
    if message.chat.type == 'private':
        await state.clear()
        await message.answer("""<b>💬 Здесь вы можете задать вопрос только касающийся работы бота.</b>\n\nНашим ботом пользуется много каналов, мы не отвечаем за них.""", reply_markup=kb.support(), parse_mode="HTML")

@dp.message(lambda message: message.text == '🔥 Хочу больше голосов')
async def wated_more_votes_message(message: Message, state: FSMContext):
    '''Отрисовать все батлы, в которых участвует пользователь'''
    battles = await db.check_all_battles_where_user_id_and_posted(message.chat.id)
    kb = InlineKeyboardBuilder()
    for battle in battles:
        kb.button(text=f'{battle[3]}', callback_data=f'donate_to_battle;{battle[0]}')
    kb.adjust(1)
    if len(battles):
        await message.answer('Выберите батл, в который хотите добавить новые голоса', reply_markup=kb.as_markup())
    else:
        await message.answer('Вы не участвуете в батлах!')

@dp.callback_query(lambda c: c.data.startswith('donate_to_battle'))
async def donate_to_battle(call: types.CallbackQuery):
    battle_id = call.data.split(';')[1]
    battle_info = await db.check_battle_info(battle_id)

    kb = InlineKeyboardBuilder()
    kb.button(text='Купить', callback_data=f'support_payment;{call.from_user.id};{battle_id}')
    kb.button(text='Выполнить задания', callback_data=f'wanted_more_voices;{battle_id};{battle_info[5]};0')
    kb.adjust(1)

    await call.message.edit_text('Вы можете получить больше голосов, купив их или выполнив задания:', reply_markup=kb.as_markup())

@dp.callback_query(lambda c: c.data.startswith('subcribed'))
async def subcribed_handler(callback: types.CallbackQuery):
    account_id = callback.data.split(';')[1]
    tg_id = callback.from_user.id
    battle_photos_info = await db.check_battle_photos_where_id1(account_id)
    battle_id = battle_photos_info[2]
    battle_info = await db.check_battle_info(battle_id)
    channel_link = battle_info[5]
    channel_id = battle_info[1]
    channel_info = await db.check_channel_info_by_id(channel_id)
    channel_tg_id = [channel_info[2]]
    is_exist = await db.check_battle_voices_tg_id_exist_return_bool(tg_id, battle_id)

    user_info = await db.check_user_photo_by_id(account_id, battle_id)
    support_kb = InlineKeyboardBuilder()
    support_kb.button(text='Поддержать участника 🆙', callback_data=f'support_user_votes;{user_info[1]};{battle_id}')
    support_kb.adjust(1)

    if is_exist:
        await callback.message.answer('🚫 Вы уже проголосовали в этом раунде', reply_markup=support_kb.as_markup())
        return
    if await check_sub_cahnnels(channel_tg_id, callback.from_user.id):
        await callback.message.delete()
        await callback.message.answer_photo(photo=battle_photos_info[3], caption='<b>Вы хотите проголосовать? Изменить или отменить голос уже не будет возможным</b>', reply_markup=get_my_voice_kb(account_id))
    else:
        kb = InlineKeyboardBuilder()
        kb.button(text='Ссылка на канал', url=channel_link)
        kb.adjust(1)
        await callback.message.answer("Чтобы проголосовать, необходимо подписаться на канал", reply_markup=kb.as_markup())

@dp.callback_query(lambda c: c.data.startswith('getmyvoice'))
async def get_my_voice_handler(callback: types.CallbackQuery, state: FSMContext):
    account_id = callback.data.split(';')[1]
    tg_id = callback.from_user.id
    battle_photos_info = await db.check_battle_photos_where_id1(account_id)
    battle_id = battle_photos_info[2]
    battle_info = await db.check_battle_info(battle_id)
    channel_link = battle_info[5]
    channel_id = battle_info[1]
    channel_info = await db.check_channel_info_by_id(channel_id)
    channel_tg_id = [channel_info[2]]
    is_exist = await db.check_battle_voices_tg_id_exist_return_bool(tg_id, battle_id)

    user_info = await db.check_user_photo_by_id(account_id, battle_id)
    support_kb = InlineKeyboardBuilder()
    support_kb.button(text='Поддержать участника 🆙', callback_data=f'support_user_votes;{user_info[1]};{battle_id}')
    support_kb.adjust(1)

    if is_exist:
        await callback.message.answer('🚫 Вы уже проголосовали в этом раунде', reply_markup=support_kb.as_markup())
        return
    await db.add_one_voice_to_battle_photos_by_id(account_id)
    await db.update_users_today_voices_and_all_voices(battle_photos_info[1])
    await db.add_new_battle_voices(battle_id, callback.from_user.id)
    await callback.message.answer('✅ Вы успешно проголосовали', reply_markup=support_kb.as_markup())

    user_info = await db.check_user_photo_by_id(account_id, battle_id)
    print(account_id, battle_id)
    '''Отправка приглашенных друзей'''
    account_id = user_info[1]
    print(await db.is_invited_friend(account_id, battle_id), user_info)
    if await db.is_invited_friend(account_id, battle_id) and user_info[4] == 3:
        print('Попал сюда')
        row = await db.find_invited_from_friend(account_id, battle_id)
        invited_from_id = row[2]
        user_invited_info = await bot.get_chat(chat_id=account_id)
        await db.update_add_voices_users(3, invited_from_id)
        invited_from_id_user_info = await db.check_info_users_by_tg_id(invited_from_id)
        kb = InlineKeyboardBuilder()
        kb.button(text=f'Использовать доп. голоса ({invited_from_id_user_info[8]} шт)',
                  callback_data=f'add_voices_use;{battle_id}')
        if await check_users_tasks(battle_id, tg_id):
            kb.button(text="🔥 Хочу больше голосов", callback_data=f'wanted_more_voices;{battle_id};{battle_info[5]}')
        await bot.send_message(chat_id=invited_from_id, text=f'✅ Ваш друг @{user_invited_info.username} набрал 3 голоса в 1 раунде. За это вы получили 3 голоса\n\n💰 Ваш баланс голосов: {invited_from_id_user_info[8]} шт')

    time_now = datetime.datetime.now()
    await db.update_last_like(tg_id, time_now.strftime('%Y-%m-%d %H:%M:%S'), battle_id)
    min_votes = battle_info[11]
    user_votes = battle_photos_info[4]

@dp.callback_query(lambda c: c.data.startswith('support_user_votes'))
async def support_user_votes_handler(call: types.CallbackQuery):
    user_id = call.data.split(';')[1]
    battle_id = call.data.split(';')[2]
    kb = InlineKeyboardBuilder()
    kb.button(text='🎁 Поддержать', callback_data=f'support_payment;{user_id};{battle_id}')
    kb.adjust(1)

    await call.message.edit_text(
    '✅ <b>Поддержите участника, купив платные голоса!</b>\n'
    'Вы можете купить любое количество голосов по одной цене, но это не влияет на размер приза.\n\n'
    'ℹ️ <b>Почему так?</b>\n'
    'Это сделано, чтобы все участники имели равные шансы на победу.\n\n'
    '💰 <b>Зачем покупать голоса?</b>\n'
    'Покупка голосов помогает формировать призовой фонд и поддерживать участников!', reply_markup=kb.as_markup())

@dp.callback_query(lambda c: c.data.startswith('support_payment'))
async def support_payment_handler(call: types.CallbackQuery, state: FSMContext):
    user_id = call.data.split(';')[1]
    battle_id = call.data.split(';')[2]
    user_from_id = call.message.from_user.id
    await state.update_data(user_id=user_id)
    await state.update_data(user_from_id=user_from_id)
    await state.update_data(battle_id=battle_id)

    await state.set_state(PaymentCountState.count)
    await call.message.edit_text('<b>🎁 Введите нужное кол-во голосов</b>')

@dp.message(PaymentCountState.count)
async def payment_method_state(message: types.Message, state: FSMContext):
    kb = InlineKeyboardBuilder()
    kb.button(text='CryptoBot', callback_data='crypto_bot_payment')
    kb.button(text='Telegram Stars 🌟', callback_data='payment_telegram_stars')
    kb.button(text='Банковская карта РФ (ручная оплата)', callback_data='RF_CARD_TRANSACTION')
    kb.adjust(1)

    if message.text is None:
        '''Оплата проведена'''
        await success_payment_handler(message, state)
        return

    if message.text.isdigit():
        if int(message.text) > 0:
            await state.update_data(count=int(message.text))
            message_delete = await message.answer('🏦 Выберите метод оплаты:', reply_markup=kb.as_markup())
            await state.update_data(message_delete_id=message_delete.message_id)
        else:
            await message.answer('🚫 Вы ввели число в неправильном формате!\nОтправьте количество голосов больше 0.')
    else:
        await message.answer('🚫 Вы ввели число в неправильном формате!\nОтправьте количество голосов.')
@dp.callback_query(lambda c: c.data.startswith('crypto_bot_payment'))
async def crypto_bot_payment_handler(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    count = data.get('count')
    chat_id = call.message.chat.id
    amount = await money_calc(chat_id, data.get('battle_id'), count, 'crypto')
    pay_link, invoice_id = get_pay_link(amount)
    if pay_link and invoice_id:
        invoices[chat_id] = invoice_id  # Store the invoice id associated with the chat_id
        kb = InlineKeyboardBuilder()
        kb.button(text="Оплатить", url=pay_link)
        kb.button(text="Проверить оплату", callback_data=f'check_payment_{invoice_id}')
        kb.adjust(1)
        await bot.send_message(chat_id, "Перейдите по этой ссылке для оплаты и нажмите 'Проверить оплату'",
                               reply_markup=kb.as_markup())
    else:
        await bot.answer_callback_query(call.id, 'Ошибка: Не удалось создать счет на оплату.')

@dp.callback_query(lambda call: call.data.startswith('check_payment_'))
async def check_payment(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(payment_type="CryptoBot")
    chat_id = call.message.chat.id
    invoice_id = call.data.split('check_payment_')[1]
    payment_status = check_payment_status(invoice_id)
    if payment_status and payment_status.get('ok'):
        if 'items' in payment_status['result']:
            invoice = next((inv for inv in payment_status['result']['items'] if str(inv['invoice_id']) == invoice_id), None)
            if invoice:
                status = invoice['status']
                if status == 'paid':
                    await success_payment_handler(call.message, state)

                    del invoices[chat_id]

                else:
                    await call.answer('Оплата не найдена❌', show_alert=True)
            else:
                await call.answer('Счет не найден.', show_alert=True)
        else:
            print(f"Ответ от API не содержит ключа 'items': {payment_status}")
            await call.answer('Ошибка при получении статуса оплаты.', show_alert=True)
    else:
        print(f"Ошибка при запросе статуса оплаты: {payment_status}")
        await call.answer('Ошибка при получении статуса оплаты.', show_alert=True)

@dp.callback_query(lambda c: c.data.startswith('RF_CARD_TRANSACTION'))
async def rf_card_transaction_handler(call: types.CallbackQuery, state:FSMContext):
    data = await state.get_data()
    from_user_id = call.from_user.id
    from_user_info = await bot.get_chat(from_user_id)
    amount = await money_calc(from_user_id, data.get('battle_id'), data.get('count'), "ruble")

    # battle_id = data.get('battle_id')
    # count = data.get('count')
    # await db.update_donations(from_user_id, battle_id, count)

    await call.message.edit_text(f'<b>✅  Вы покупаете {data.get("count")} голосов пользователю @{from_user_info.username}.</b>\n\nИтоговая сумма - {amount} рублей\n<b>🚫 Чтобы оплатить переводом на карту, напишите - @</b>')
    await state.clear()

@dp.callback_query(lambda c: c.data.startswith('payment_telegram_stars'))
async def send_invoice_handler(call: types.CallbackQuery, state: FSMContext):
    kb = InlineKeyboardBuilder()
    kb.button(text='Telegram Stars 🌟', pay=True)
    kb.adjust(1)

    data = await state.get_data()

    count = data.get('count')
    amount = await money_calc(call.from_user.id, data.get('battle_id'), count, "stars")
    print('цена', count, amount)
    prices = [types.LabeledPrice(label="XTR", amount=amount)]
    await call.message.answer_invoice(
        title="🏦 Выберите метод оплаты:",
        description=f'Поддержка участника',
        provider_token="",
        prices=prices,
        payload="user_support",
        currency="XTR",
        reply_markup=kb.as_markup(),
    )

async def pre_checkout_handler(pre_checkout_query: types.PreCheckoutQuery, state: FSMContext):
    await pre_checkout_query.answer(ok=True)
    await state.update_data(payment_type="Telegram Stars")

async def success_payment_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    count = data.get('count')
    user_id = data.get('user_id')
    battle_id = data.get('battle_id')
    payment_type = data.get('payment_type')
    message_delete_id = data.get('message_delete_id')
    from_user_id = data.get('from_user_id')
    await bot.delete_message(message.chat.id, message_id=message_delete_id)
    await db.update_donations(from_user_id, battle_id, count)
    await state.clear()
    battle_info = await db.check_battle_info(battle_id)
    channel_id = battle_info[1]
    channel_info = await db.check_channel_info_by_id(channel_id)
    await message.answer(text=f"{count} голосов зачислено!")
    await db.add_battle_photos_votes_where_tg_id_and_battle_id(user_id, count, battle_id)
    kb = InlineKeyboardBuilder()
    kb.button(text='🎁 Купить голоса', callback_data=f'support_payment;{user_id};{battle_id}')
    kb.adjust(1)
    user = await bot.get_chat(chat_id=user_id)
    if str(from_user_id) != str(user_id):
        await bot.send_message(chat_id=user_id,
                           text=f'🎁 Поздравляем! Вам только что подарили {count} голосов!\n\n✅ Голоса уже начислены на ваше фото ',
                           reply_markup=kb.as_markup())

    await bot.send_message(chat_id=admins[0], text=f'🏦 Продано {count} голосов пользователю {user.first_name} (@{user.username}) - {user_id}\n\nКанал (в котором купили) - {channel_info[5]}\n\nСпособ оплаты: {payment_type}')
    user_photo = await db.check_user_photo_by_tg_id(user_id, battle_id)
    photos = await db.check_all_battle_photos_where_status_1_and_battle_id_and_number_post(battle_id, user_photo[6])
    for photo in photos:
        kb = InlineKeyboardBuilder()
        kb.button(text='🎁 Купить голоса', callback_data=f'support_payment;{photo[1]};{battle_id}')
        kb.adjust(1)
        if str(user_id) != str(photo[1]):
            await bot.send_message(
                chat_id=photo[1],
                text='<b>❌ Кто-то из ваших противников в посте приобрел голоса.\n\nВам нужно действовать быстрее, чтобы не проиграть!</b>',reply_markup=kb.as_markup())

dp.pre_checkout_query.register(pre_checkout_handler)
dp.message.register(success_payment_handler, F.successful_payment)
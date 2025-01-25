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
from functions.admin_functions import back_main_menu_channels, delete_channel_func
from handlers.admin_handler import settings_channel
from keyboards.another import cabinet_back, create_battle, faq, statics_back
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
                    await message.answer(f"💬 <b>Здравствуйте, @{username}!</b>\n\n"
                        f"Вы обращаетесь в службу поддержки канала <b>{name}.</b>\n\n"
                        "Пожалуйста, напишите свой вопрос, можно отправить фото.",
                        parse_mode="HTML")
                    await state.set_state(waiting_for_answers.q3)
                    return

                if account_id.startswith('b'):
                    battle_id = account_id[1:]
                    is_user_blocked = await db.check_battle_block_battle_id_tg_id_exist_return_bool(
                        battle_id, message.from_user.id)
                    if is_user_blocked:
                        await message.answer('Вы заблокированы в этом батле')
                        return

                    battle_info = await db.check_battle_info(battle_id)
                    if battle_info[21] == 0:
                        await message.answer('❌ Набор фото пока что прекращен, попробуйте позже')
                        return

                    is_user_exist = await db.check_battle_where_battle_id_and_tg_id_exist_and_status_1_return_bool(
                        battle_id, message.from_user.id)
                    if is_user_exist:
                        await message.answer('Вы уже участвуете в этом батле')
                        return

                    await state.set_state(SendPhotoForBattle.q1)
                    await state.update_data(battle_id=battle_id)
                    await message.answer('Отправьте фото, которое не несет 18+ и оскорбительного характера')
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
                if is_exist:
                    await message.answer('<b>🚫 Вы уже проголосовали в этом раунде</b>')
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

        # Если никаких параметров не передано
        await message.answer(
            f"👋 Добро пожаловать, @{username}!\n\n"
            "📖 Пожалуйста, ознакомьтесь с <a href='https://telegra.ph/Polzovatelskoe-soglashenie-kanала-PhotoBattliys-10-05'>пользовательским соглашением</a> и "
            "<a href='https://telegra.ph/Politika-konfidencialnosti-kanala-PhotoBattliys-10-05'>политикой конфиденциальности</a>.\n\n"
            "<b>💬 Используя бота, вы автоматически соглашаетесь с данными условиями. Приятного использования!</b>",
            reply_markup=kb.start_menu_for_users(),
            parse_mode='HTML',
            disable_web_page_preview=True)

@dp.callback_query(lambda c: c.data.startswith('voteby'))
async def vote_in_battle(callback: types.CallbackQuery):
    tg_id = callback.message.from_user.id

    data = callback.data.split(';')
    battle_id = data[1]
    account_id = data[2]
    battle_photos_info = await db.check_battle_photos_where_id1(account_id)
    battle_id = battle_photos_info[2]
    is_exist = await db.check_battle_voices_tg_id_exist_return_bool(tg_id, battle_id)
    if is_exist:
        await callback.message.answer('<b>🚫 Вы уже проголосовали в этом раунде</b>')
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

@dp.message(lambda message: message.text == "🧱 Создать фото-батл")
async def handle_profile(message: types.Message, state: FSMContext):
    if message.chat.type == 'private':
        await state.clear()
        tg_id = message.from_user.id
        admin_exist = await db.check_admin_exist_return_bool(tg_id)
        if admin_exist or tg_id in admins:
         await message.answer(
                "<b>Меню создания фото-батла:</b>",
                reply_markup=create_battle())
         return
        await message.answer(
            "<b>🚫 Неизвестная команда.</b>")
        return
#кнопка создать батл
@dp.callback_query(lambda c: c.data.startswith('create_battle'))
async def go_create_battle(call: types.CallbackQuery):
    tg_id = call.from_user.id
    channels = await db.checkk_all_channels_where_tg_id(tg_id)
    await call.message.edit_text('<b> ⚙️ Выберите канал для создания фото-батла:</b>', reply_markup=back_main_menu_channels(channels))

@dp.callback_query(lambda c: c.data.startswith('backmainmenu'))
async def back_from_create_battle(call: types.CallbackQuery):
    await call.message.edit_text('<b>Меню создания фото-батла:</b>', reply_markup=create_battle())

@dp.callback_query(lambda c: c.data.startswith('backtochannels'))
async def back_from_create_battle(call: types.CallbackQuery):
    tg_id = call.from_user.id
    channels = await db.checkk_all_channels_where_tg_id(tg_id)
    await call.message.edit_text('<b> ⚙️ Выберите канал для создания фото-батла:</b>', reply_markup=back_main_menu_channels(channels))

@dp.callback_query(lambda c: c.data.startswith('back_from_addchannel'))
async def go_create_battle(call: types.CallbackQuery):
    tg_id = call.from_user.id
    channels = await db.checkk_all_channels_where_tg_id(tg_id)
    await call.message.edit_text('<b> ⚙️ Выберите канал для создания фото-батла: </b>', reply_markup=back_main_menu_channels(channels))

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
            channels, total_moments = await get_paginated_items34(0)
            items_kb = await build_items_kb34(channels, 0, total_moments)
            await message.answer(
                "<b>Список каналов, использующие бота:</b>",
                reply_markup=items_kb.as_markup())
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

    for channel in channels:
        channel_info = await db.check_channel_info_by_id(channel[0])
        name = channel_info[3]
        categories_kb.button(text=f"{name}", callback_data=f'channelcheckitem;{channel[0]};{page}')

    categories_kb.adjust(1)
    buttons = [
        InlineKeyboardButton(text='◀️', callback_data=f'channelspageitems;{page-1}'),
        InlineKeyboardButton(text=f'{page+1}/{(total_moments // ITEMS_PER_PAGE) + 1}', callback_data='current'),
        InlineKeyboardButton(text='▶️', callback_data=f'channelspageitems;{page+1}')
          ]
    categories_kb.row(*buttons)
    back_button = InlineKeyboardButton(text='🔙 Назад', callback_data='cancel_menu_channels')
    categories_kb.row(back_button)

    return categories_kb

@dp.callback_query(lambda c: c.data.startswith('channelcheckitem'))
async def battle_check_item_handler(call: types.CallbackQuery):
    channel_id = call.data.split(';')[1]
    kb = InlineKeyboardBuilder()
    channel_info = await db.check_channel_info_by_id(channel_id)
    name = channel_info[3]
    link = channel_info[5]

    kb.button(text='⚔️ Активные наборы на фото-батлы', callback_data=f'channel_battles;{channel_id}')
    kb.button(text='🗑️ Удалить канал', callback_data=f'channel_delete;{channel_id}')
    kb.button(text='🔙 Назад', callback_data=f'backtochannel_list')
    kb.adjust(1)
    await call.message.edit_text(f'''<b>Канал {name}</b>\n\nСсылка: {link}''',disable_web_page_preview=True, reply_markup=kb.as_markup())

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
    await call.message.edit_text(
        text=f"<b>Список каналов, использующие бота:</b>", reply_markup=categories_kb.as_markup())

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

@dp.message(lambda message: message.text == "🛠️ Накрутка голосов")
async def handle_profile(message: types.Message, state: FSMContext):
    if message.chat.type == 'private':
        await state.clear()
        tg_id = message.from_user.id

        if tg_id in admins:
            await message.answer(
                "<b>Меню накрутки голосов 🛠️</b>",
                reply_markup=nakrutka_menu())
            return

        admin_exist = await db.check_admin_exist_return_bool(tg_id)
        if admin_exist:
            await message.answer(
                "<b>🚫 Неизвестная команда.</b>")
            return

        await message.answer(
            "<b>🚫 Неизвестная команда.</b>")
        return

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


    GetChannelId.user = message.chat.id
    print(message.chat.id)

    kb = InlineKeyboardBuilder()
    kb.button(text='Добавить канал', url=f'http://t.me/{bot_name}?startchannel&admin=change_info+invite_users')
    kb.button(text='🔙 Назад', callback_data='backtochannels')
    kb.adjust(1)

    await message.edit_text(
    "<b>Добавление канала 📝</b>\n\n"
    "Чтобы подключить канал:\n\n"
    "1️⃣ <i>Добавьте бота в администраторы канала</i> с разрешением на публикацию и редактирование постов ➕\n"
    "2️⃣ <i>Нажмите кнопку внизу и выберите нужный канал</i>\n", reply_markup=kb.as_markup(), show_alert=True,
        disable_web_page_preview=True)

@dp.message(AddChannel.q1)
async def add_channel_func(message: types.Message, state: FSMContext, bot: Bot):
    tg_id = message.from_user.id
    channel_id = message.chat_shared.chat_id
    try:
        info = await bot.get_chat(channel_id)
    except Exception as ex:
        await message.answer(
            "<b>Что-то пошло не так! 😟</b>\n\n"
            "Убедитесь, что бот добавлен в канал как администратор и пересылаете сообщение из канала. Попробуйте еще раз.")
        return
    channel_title = info.title
    if channel_title and info.type == 'channel':
        try:
            admin_exists = await db.check_admin_exist_return_bool(tg_id)
            if not admin_exists:
                await db.add_admin(tg_id)
            chat_member = await bot.get_chat_member(channel_id, bot.id)
            if chat_member.status in ['administrator', 'creator']:
                result = await db.add_new_cahnnel_by_chan_id(tg_id, channel_id, channel_title)
                if result is True:
                    await db.add_battles_statistic(tg_id)
                    channels = await db.check_all_channels()
                    channel_id_db = channels[-1][0]

                    chan_id = str(channel_id).replace('-100', '')
                    message_link = f'https://t.me/c/{chan_id}/-1'
                    await db.update_channels_post_link_where_id(message_link, channel_id_db)
                    channel_link = info.invite_link

                    await db.update_channel_link_where_id(channel_link, channel_id_db)

                    await message.answer(
                        "<b>Канал успешно добавлен! 🎉</b>\n\n"
                        "Теперь вы можете использовать все функции нашего бота для автоматизации фото-батлов в этом канале.\n\n"
                        "<u><i>Удачного пользования! 😉</i></u>",reply_markup=admin_kb.start_menu_for_admins())
                else:
                    await message.answer(
                    "<b>Этот канал уже добавлен! 🔄</b>\n\n"
                    "Вы можете продолжить пользоваться нашим ботом для автоматизации фото-батлов в этом канале.", reply_markup=admin_kb.start_menu_for_admins())
                    await state.clear()
                    return
                await state.clear()
                return
        except Exception as e:
            print(f"Ошибка: {e}")
    await message.answer(
        "<b>Что-то пошло не так! 😟</b>\n\n"
        "Убедитесь, что бот добавлен в канал как администратор и пересылаете сообщение из канала. Попробуйте еще раз.")

@dp.callback_query(lambda c: c.data.startswith('nakrutka'))
async def create_mailing(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите tg_id пользователя, которому хотите накрутить голоса')
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
        await message.answer('Введите кол-во голосов')
        await state.set_state(AddVoices.q2)
    else:
        await message.answer('Не похоже на tg_id, попробуйте ещё раз')

@dp.message(AddVoices.q2)
async def add_voices_handler(message: types.Message, state: FSMContext):
    count = message.text
    if count.isdigit():
        count = int(count)
        if count > 0 and count < 4:
            data = await state.get_data()
            tg_id = data.get('tg_id')
            await db.add_battle_photos_votes_where_tg_id(tg_id, count)
            await message.answer(f'{count} голосов добавлено')
            await state.clear()
        else:
            await message.answer('За 1 раз максимум можно накрутить3 голоса')
    else:
        await message.answer('Не похоже на число, попробуйте ещё раз')

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
@dp.callback_query(lambda c: c.data.startswith('create_mailling'))
async def create_mailing(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer('<b>[1/2] Введите сообщение для рассылки</b>')
    await state.set_state(Mailing.q1)
@dp.message(Mailing.q1)
async def mailing_handler(message: types.Message, state: FSMContext):
    await state.update_data(message_id=message.message_id)
    await state.set_state(Mailing.q2)
    await message.answer('<b>[2/2] Введите кнопки в формате:</b> Текст;ссылка\n\nКаждую кнопку с новой строки \nЕсли не нужны кнопки, то 0')
@dp.message(Mailing.q2)
async def mailing_handler_q2(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
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
                    await message.answer(f"Ошибка: ссылка должна начинаться с 'https://'. Проверьте: {btn_url}")
                    return
        markup.adjust(1)
    await send_copy_to_all_users(message.chat.id, mess_id, markup.as_markup())
    await state.clear()
    await message.answer("<b>🏁 Рассылка завершена.</b>")
async def send_copy_to_all_users(chat_id, message_id, reply_markup):
    user_ids = await db.get_all_users_tg_id()
    count = 0
    for user_id in user_ids:
        try:
            await bot.copy_message(
                chat_id=user_id[0],
                from_chat_id=chat_id,
                message_id=message_id,
                reply_markup=reply_markup)
        except Exception as e:
            count +=1
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

@dp.message(lambda message: message.text == '📊 Статистика бота')
async def statics(message: types.Message, state: FSMContext):
    if message.chat.type == 'private':
        tg_id = message.from_user.id
        blocked = await db.check_blocked_count_where_id_1()
        users = await db.check_len_users()
        items = await db.check_all_battles_where_status_1()

        active_battles = await db.check_all_battles_where_all_ran_return_id()

        await message.answer(f"""<b>📊 Статистика бота "Помощник фото-батлов | Участвовать"</b>\n\n- Количество активных батлов: {len(items)}\n\n- Количество пользователей: {users}\n\n- Активные батлы: {len(active_battles)}\n\n<b>ℹ️ Ваша статистика представлена в личном кабинете</b>""",reply_markup=statics_back(),parse_mode="HTML",)

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
            f" 👋 Добро пожаловать, @{username}!\n\n"
            "📖 Пожалуйста, ознакомьтесь с <a href='https://telegra.ph/Polzovatelskoe-soglashenie-kanala-PhotoBattliys-10-05'>пользовательским соглашением</a> и "
            "<a href='https://telegra.ph/Politika-konfidencialnosti-kanala-PhotoBattliys-10-05'>политикой конфиденциальности</a>.\n\n"
            "<b>💬 Используя бота, вы автоматически соглашаетесь с данными условиями. Приятного использования!</b>",reply_markup=kb.start_menu_for_users(),parse_mode='HTML',disable_web_page_preview=True)

@dp.message(lambda message: message.text == '🆘 Тех. поддержка')
async def tech_support_start(message: Message, state: FSMContext):
    if message.chat.type == 'private':
        await state.clear()
        await message.answer("""💬 Здесь вы можете задать вопрос только администраторам этого бота. Мы не сможем ответить на вопросы, не связанные с ботом и каналом данного бота.        
\n\n<i>Прежде чем написать, прочтите “Часто задаваемые вопросы (FAQ)”</i>""", reply_markup=kb.support(), parse_mode="HTML")

@dp.message(lambda message: message.text == '📚 FAQ')
async def show_faq(message: types.Message, state: FSMContext):
    await message.answer(
    """❓ *Что такое "Фотобатлы"?*
Это развлекательный проект в Telegram, где участники соревнуются в фотодуэлях.
Присылайте свои лучшие фото и боритесь за призы!

🌟 *Как участвовать?*
1. Отправьте фотографию через нашего Telegram-бота.
2. Дождитесь старта батла.
3. Соревнуйтесь за голоса зрителей.

🏆 *Как определяется победитель?*
- Побеждает фотография, набравшая наибольшее количество голосов.
- Результат зависит только от участников голосования.

💸 *Есть ли денежные игры?*
Да, проводятся конкурсы с денежными призами, например:
- *Аукционы:* участник, предложивший наибольшую ставку, забирает весь банк. Эти игры не являются азартными.

⚠️ *Что делать, если я проиграл?*
- Средства не возвращаются.
- Организатор не несет ответственности за убытки. (Проект предназначен для развлечения.)

🚪 *Как прекратить участие?*
- Просто отпишитесь от канала, либо перестаньте участвовать в батлах.

📜 *Могут ли измениться правила?*
Да, организатор оставляет за собой право изменять условия.
Все изменения публикуются в постах и закрепленных сообщениях канала.""",parse_mode="MARKDOWN", reply_markup=faq())

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
    if is_exist:
        await callback.answer('🚫 Вы уже проголосовали в этом раунде', show_alert=True)
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
    if is_exist:
        await callback.answer('🚫 Вы уже проголосовали в этом раунде', show_alert=True)
        return
    await db.add_one_voice_to_battle_photos_by_id(account_id)
    await db.update_users_today_voices_and_all_voices(battle_photos_info[1])
    await db.add_new_battle_voices(battle_id, callback.from_user.id)
    await callback.answer('✅ Вы успешно проголосовали', show_alert=True)
    time_now = datetime.datetime.now()
    await db.update_last_like(tg_id, time_now.strftime('%Y-%m-%d %H:%M:%S'), battle_id)
    min_votes = battle_info[11]
    user_votes = battle_photos_info[4]

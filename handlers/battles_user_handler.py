from aiogram import types
from handlers.start_handler import add_channel_func
from keyboards.dev import answers_support, question_chat
from keyboards.another import question
from aiogram.enums.content_type import ContentType
from data.config import *
import re
from functions.admin_functions import *
from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from data import loader, config
from database import db
from aiogram.utils.keyboard import InlineKeyboardBuilder
from states.classes_states import *
from constants.constants import *
from aiogram.types import InlineKeyboardButton

dp = Router()
bot = loader.start_bot(config.Token)

ITEMS_PER_PAGE = 10
    
async def get_paginated_items33(page: int = 0):
    items = await db.check_all_battles()
    print(items)
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    print(start, end)
    return items[start:end], len(items)

async def get_paginated_items33_channels(page: int = 0):
    items = await db.check_all_channels()
    print(items)
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    print(start, end)
    return items[start:end], len(items)


def build_items_kb33(categories, page, total_moments):
    categories_kb = InlineKeyboardBuilder()

    for category in categories:
        if category[14] == 1:
            categories_kb.button(text=f"{category[3]}", callback_data=f'battlecheckitem;{category[0]};{page}')
    categories_kb.adjust(1)

    # Add pagination buttons
    buttons = []

    buttons.append(InlineKeyboardButton(text='◀️', callback_data=f'battlespageitems;{page-1}'))
    buttons.append(InlineKeyboardButton(text=f'{page+1}/{(total_moments // ITEMS_PER_PAGE) + 1}', callback_data='current'))
    buttons.append(InlineKeyboardButton(text='▶️', callback_data=f'battlespageitems;{page+1}'))

    categories_kb.row(*buttons)

    # Add "Back" button
    back_button = InlineKeyboardButton(text='🔙 Назад', callback_data='backstartmenu')
    categories_kb.row(back_button)

    return categories_kb

def build_items_kb33_channels(categories, page, total_moments):
    categories_kb = InlineKeyboardBuilder()

    for category in categories:
        categories_kb.button(text=f"{category[3]}", callback_data=f'battlecheckitem;{category[0]};{page}')
    categories_kb.adjust(1)

    # Add pagination buttons
    buttons = []

    buttons.append(InlineKeyboardButton(text='◀️', callback_data=f'channelspageitems;{page-1}'))
    buttons.append(InlineKeyboardButton(text=f'{page+1}/{(total_moments // ITEMS_PER_PAGE) + 1}', callback_data='current'))
    buttons.append(InlineKeyboardButton(text='▶️', callback_data=f'channelspageitems;{page+1}'))

    categories_kb.row(*buttons)

    # Add "Back" button
    back_button = InlineKeyboardButton(text='🔙 Назад', callback_data='backstartmenu')
    categories_kb.row(back_button)

    return categories_kb

@dp.callback_query(lambda c: c.data.startswith('backstartmenu'))
async def backstartmenu(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text('🔙 Возвращаемся')
    return

@dp.message(lambda message: message.text == "⚔️ Наборы на фото-батлы")
async def user_menu_handler(message: types.Message, state: FSMContext):
   if message.chat.type == 'private':
    await state.clear()
    tg_id = message.from_user.id

    admin_exist = await db.check_admin_exist_return_bool(tg_id)
    active_battles = await db.check_battles_where_status_1_and_tg_id(tg_id)

    if tg_id in admins or admin_exist:
     await message.answer('<b>🔠 Выберите нужный батл для управления: \n\n</b> 💁 Вы не можете участвовать в батлах, так как вы админ. \nОтправляйте фото с других аккаунтов.', reply_markup=await active_battles_kb(active_battles))
     return  
    categories, total_items = await get_paginated_items33(0)
    items_kb = build_items_kb33(categories, 0, total_items)
    await message.answer(
    '<b>📸 Активные фото-батлы</b>\n\n'
    'Выбирайте батл и участвуйте прямо сейчас. Все они прошли проверку администрацией.\n\n'
    '<b>💥 Покажите, на что способны, и станьте победителем!</b>',
    reply_markup=items_kb.as_markup(),
    parse_mode="HTML")

@dp.message(lambda message: message.text == "✅ Приступим")   
async def add_channel_handler(callback: types.CallbackQuery, state: FSMContext):
    await add_channel_func(callback, state)
    
@dp.callback_query(lambda c: c.data.startswith('battlespageitems'))
async def battles_page_items_handler(call: types.CallbackQuery):
    page = int(call.data.split(';')[1])
    print(page)
    categories, total_items = await get_paginated_items33(page)

    if page < 0 or page > total_items // ITEMS_PER_PAGE:
        await call.answer()
        return 
    
    items_kb = build_items_kb33(categories, page, total_items)
    await call.message.edit_reply_markup(reply_markup=items_kb.as_markup())


@dp.callback_query(lambda c: c.data.startswith('channelspageitems'))
async def channels_page_items_handler(call: types.CallbackQuery):
    page = int(call.data.split(';')[1])
    print(page)
    categories, total_items = await get_paginated_items33_channels(page)

    if page < 0 or page > total_items // ITEMS_PER_PAGE:
        await call.answer()
        return

    items_kb = build_items_kb33_channels(categories, page, total_items)
    await call.message.edit_reply_markup(reply_markup=items_kb.as_markup())

@dp.callback_query(lambda c: c.data.startswith('battlecheckitem'))
async def battle_check_item_handler(call: types.CallbackQuery):
    battle_id = call.data.split(';')[1]
    battle_info = await db.check_battle_info(battle_id)
    kb = InlineKeyboardBuilder()
    
    kb.button(text='✅ Отправить фото', callback_data=f'battlejoin;{battle_id}')
    kb.button(text='✍️ Задать вопрос', callback_data=f'battlequestion;{battle_id}')
    kb.button(text='🔙 Назад', callback_data=f'usermenu;battles')
    kb.adjust(1)
    await call.message.edit_text(f'''<b>{battle_info[3]}</b>

Ссылка на канал - {battle_info[5]}
Приз: {battle_info[6]}

<b>Начало батла: {battle_info[9]} МСК</b>
''',disable_web_page_preview=True, reply_markup=kb.as_markup())
    
ADMIN_CHAT_ID = -1002410081146

# Обработчик для кнопки "Задать вопрос"
@dp.message(lambda message: message.text == "🙋 Задать вопрос")
async def battle_question_handler(message: types.Message, state: FSMContext):
    await message.answer(
        "<b>💬 Задайте свой вопрос!</b>\n\n"
        "Вы также можете отправить фото 📸, но видео, к сожалению, не принимаются.", reply_markup=question(),
        parse_mode="HTML")
    # Устанавливаем состояние
    await state.set_state(waiting_for_answers.q2)
    
# Обработчик для получения текста вопроса по ПОВОДУ ВОПРОСОВ БОТА
@dp.message(waiting_for_answers.q2)
async def process_question(message: types.Message, state: FSMContext):
    if message.content_type not in [ContentType.TEXT, ContentType.PHOTO]: # ЕСЛИ НЕ ТЕКСТ И НЕ ФОТО
        await message.answer(
            "Вы также можете отправить фото 📸, но видео и другие форматы, к сожалению, не принимаются.", reply_markup=question(),
            parse_mode="HTML")
        # Устанавливаем состояние
        await state.set_state(waiting_for_answers.q2)
        return
    elif message.content_type == ContentType.TEXT:                  #  ЭТО ТЕКСТ

        if not message.text:
            await message.answer(
                "<b>💬 Пожалуйста, задайте свой вопрос в виде текста или прикрепите фото.</b>", parse_mode="HTML")
            # Остаёмся в состоянии ожидания
            await state.set_state(waiting_for_answers.q2)
            return  # Остановка выполнения
        else:
            question_text = message.text.strip()
            photo = None
    else:
        if not message.caption:
            await message.answer(
                "<b>💬 Пожалуйста, отправьте фото с вопросом, чтобы мы могли точно понять ваш вопрос.</b>",
                parse_mode="HTML")
            # Сохраняем состояние ожидания
            await state.set_state(waiting_for_answers.q2)
            return  # Остановка выполнения
        else:
            question_text = message.caption.strip()
            photo = message.photo[-1]

    # Проверяем длину текста
    if question_text and len(question_text) < 5:
        await message.answer(
            "<b>💬 Пожалуйста, опишите ваш вопрос подробнее (минимум 5 символов).</b>", parse_mode="HTML")
        return  # Остановка выполнения

    if question_text and len(question_text) > 100:
        await message.answer(
            "<b>💬 Пожалуйста, опишите ваш вопрос короче (максимум 100 символов).</b>", parse_mode="HTML")
        # Остаёмся в состоянии ожидания
        await state.set_state(waiting_for_answers.q2)
        return  # Остановка выполнения

    # Если всё корректно, отправляем сообщение администратору
    def escape_markdown(text: str) -> str:
        return re.sub(r"([_*[\]()~`>#+\-=|{}.!])", r"\\\1", text)

    username = f"@{escape_markdown(message.from_user.username)}" if message.from_user.username else "неизвестно"
    user_id = message.from_user.id
    question_message = (
        f"📩 *Новый вопрос от пользователя*:\n\n"
        f"👤 Имя: {username}\n"
        f"🆔 ID: `{user_id}`\n\n"
        f"❓ Вопрос:\n\n{question_text}")
    await state.update_data(user_id=user_id)
    try:
        if photo:
            await bot.send_photo(
                ADMIN_CHAT_ID,
                photo=photo.file_id,
                caption=question_message,
                parse_mode="Markdown",
                reply_markup=question_chat(user_id=user_id, has_photo=True))
        else:
            await bot.send_message(
                ADMIN_CHAT_ID,
                question_message,
                parse_mode="Markdown",
                reply_markup=question_chat(user_id=user_id, has_photo=False))
        await message.answer(
            "<b>✅ Ваш вопрос успешно отправлен!</b>\n"
            "Мы свяжемся с вами в ближайшее время. Спасибо за обращение! 🙌", parse_mode="HTML")
    except Exception as e:
        await message.answer(
            "<b>⚠️ Произошла ошибка при отправке вопроса.</b>\n"
            "Пожалуйста, попробуйте ещё раз немного позже.",
            parse_mode="HTML")
        print(f"Ошибка отправки сообщения администратору: {e}")
    finally:
        # Завершаем состояние
        await state.clear()

# Обработчик для получения текста вопроса по ПОВОДУ ВОПРОСОВ ДРУГИХ КАНАЛОВ
@dp.message(waiting_for_answers.q3)
async def process_question(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    channel_id = user_data.get('channel_id')
    if message.content_type not in [ContentType.TEXT, ContentType.PHOTO]: # ЕСЛИ НЕ ТЕКСТ И НЕ ФОТО
        await message.answer(
            "Вы также можете отправить фото 📸, но видео и другие форматы, к сожалению, не принимаются.", reply_markup=question(),
            parse_mode="HTML")
        # Устанавливаем состояние
        await state.set_state(waiting_for_answers.q3)
        return
    elif message.content_type == ContentType.TEXT:                  #  ЭТО ТЕКСТ

        if not message.text:
            await message.answer(
                "<b>💬 Пожалуйста, задайте свой вопрос в виде текста или прикрепите фото.</b>", parse_mode="HTML")
            # Остаёмся в состоянии ожидания
            await state.set_state(waiting_for_answers.q3)
            return  # Остановка выполнения
        else:
            question_text = message.text.strip()
            photo = None
    else:
        if not message.caption:
            await message.answer(
                "<b>💬 Пожалуйста, отправьте фото с вопросом, чтобы мы могли точно понять ваш вопрос.</b>",
                parse_mode="HTML")
            # Сохраняем состояние ожидания
            await state.set_state(waiting_for_answers.q3)
            return  # Остановка выполнения
        else:
            question_text = message.caption.strip()
            photo = message.photo[-1]

    # Проверяем длину текста
    if question_text and len(question_text) < 5:
        await message.answer(
            "<b>💬 Пожалуйста, опишите ваш вопрос подробнее (минимум 5 символов).</b>", parse_mode="HTML")
        return  # Остановка выполнения

    if question_text and len(question_text) > 100:
        await message.answer(
            "<b>💬 Пожалуйста, опишите ваш вопрос короче (максимум 100 символов).</b>", parse_mode="HTML")
        # Остаёмся в состоянии ожидания
        await state.set_state(waiting_for_answers.q3)
        return  # Остановка выполнения

    # Если всё корректно, отправляем сообщение администратору
    def escape_markdown(text: str) -> str:
        return re.sub(r"([_*[\]()~`>#+\-=|{}.!])", r"\\\1", text)

    username = f"@{escape_markdown(message.from_user.username)}" if message.from_user.username else "неизвестно"
    user_id = message.from_user.id
    question_message = (
        f"📩 *Новый вопрос от пользователя*:\n\n"
        f"👤 Имя: {username}\n"
        f"🆔 ID: `{user_id}`\n\n"
        f"❓ Вопрос:\n\n{question_text}")
    channel_info = await db.check_channel_info_by_id(channel_id)  # Получаем информацию о канале из базы данных
    admin_chat_id = channel_info[4]  # Предположим, что 5-й элемент — это admin_chat_id
    try:
        if photo:
            await bot.send_photo(
                admin_chat_id,
                photo=photo.file_id,
                caption=question_message,
                parse_mode="Markdown",
                reply_markup=question_chat(user_id=user_id, has_photo=True))
        else:
            await bot.send_message(
                admin_chat_id,
                question_message,
                parse_mode="Markdown",
                reply_markup=question_chat(user_id=user_id, has_photo=False))
        await message.answer(
            "<b>✅ Ваш вопрос успешно отправлен!</b>\n"
            "Мы свяжемся с вами в ближайшее время. Спасибо за обращение! 🙌", parse_mode="HTML")
    except Exception as e:
        await message.answer(
            "<b>⚠️ Произошла ошибка при отправке вопроса.</b>\n"
            "Пожалуйста, попробуйте ещё раз немного позже.",
            parse_mode="HTML")
        print(f"Ошибка отправки сообщения администратору: {e}")
    finally:
        # Завершаем состояние
        await state.clear()
        
@dp.callback_query(lambda c: c.data.startswith('admin_reply'))
async def admin_reply(call: types.CallbackQuery, state: FSMContext):
    # Сохраняем user_id в состояние
    user_id = call.data.split(';')[1]
    await call.message.answer("<b>✍️ Введите ваш ответ:</b>\n", parse_mode="HTML")
    await state.set_state(waiting_for_answers.q1)
    await state.update_data(user_id=user_id)



@dp.message(waiting_for_answers.q1)
async def process_answers(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data['user_id']
    if message.content_type not in [ContentType.TEXT, ContentType.PHOTO]:  # ЕСЛИ НЕ ТЕКСТ И НЕ ФОТО
        await message.answer(
            "Вы также можете отправить фото 📸, но видео и другие форматы, к сожалению, не принимаются.",
            reply_markup=question(),
            parse_mode="HTML")
        # Устанавливаем состояние
        await state.set_state(waiting_for_answers.q1)
        return
    elif message.content_type == ContentType.TEXT:  # ЭТО ТЕКСТ
        if not message.text:
            await message.answer(
                "<b>💬 Пожалуйста, задайте свой ответ в виде текста или прикрепите фото.</b>", parse_mode="HTML")
            # Остаёмся в состоянии ожидания
            await state.set_state(waiting_for_answers.q1)
            return  # Остановка выполнения
        else:
            answer_text = message.text.strip()
            photo = None
    else:  # ЗНАЧИТ ЭТО ФОТО
        if not message.caption:
            await message.answer(
                "<b>💬 Пожалуйста, отправьте фото с ответом.</b>",
                parse_mode="HTML")
            # Сохраняем состояние ожидания
            await state.set_state(waiting_for_answers.q1)
            return  # Остановка выполнения
        else:
            photo = message.photo[-1]
            answer_text = message.caption.strip()

    if len(answer_text) < 5 or len(answer_text) > 100:
        await message.answer("<b>💬 Ответ должен быть от 5 до 100 символов.</b>", parse_mode="HTML")
        await state.set_state(waiting_for_answers.q1)
        return
    # Формируем сообщение
    answer_text_message = f"<b>📩 Новый ответ от администратора:</b>\n\n {answer_text}"
    try:
        if photo:
            await bot.send_photo(user_id, photo=photo.file_id, caption=answer_text_message, reply_markup=answers_support(user_id, has_photo=False))
        else:
            await bot.send_message(user_id, text=answer_text_message, reply_markup=answers_support(user_id, has_photo=False))
        await message.answer("<b>✅ Ответ пользователю успешно отправлен!</b>", parse_mode="HTML")
    except Exception as e:
        await message.answer("<b>⚠️ Ошибка при отправке ответа.</b>", parse_mode="HTML")
        print(f"Ошибка отправки сообщения: {e}")
    finally:
        await state.clear()


@dp.callback_query(lambda c: c.data.startswith('replying'))
async def option_channel_handler(callback_query: types.CallbackQuery, state: FSMContext):
    await battle_question_handler(callback_query.message, state)
    await callback_query.answer()
    
@dp.callback_query(lambda c: c.data.startswith('answers_done'))
async def answers_done(call: types.CallbackQuery):
    await call.message.edit_text('<b>Мы рады были вам помочь, если вдруг возникнут ещё вопросы - обращайтесь! 🫂</b>')



@dp.callback_query(lambda c: c.data.startswith('battlejoin'))
async def battle_join_handler(call: types.CallbackQuery, state: FSMContext):
    battle_id = call.data.split(';')[1]
    is_user_blocked = await db.check_battle_block_battle_id_tg_id_exist_return_bool(battle_id, call.from_user.id)
    if is_user_blocked:
        await call.answer('Вы заблокированы в этом батле', show_alert=True)
        return
    is_user_exist = await db.check_battle_where_battle_id_and_tg_id_exist_and_status_1_return_bool(battle_id, call.from_user.id)

    is_user_exist_battle = await db.check_battle_where_battle_id_and_tg_id_exist_and_status_0_return_bool(battle_id, call.from_user.id)
    if is_user_exist_battle:
        await call.answer('Вы уже отправили фото на проверку, ожидайте...', show_alert=True)
        return
    if is_user_exist:
        await call.answer('Вы уже участвуете в этом батле', show_alert=True)
        return
    await state.set_state(SendPhotoForBattle.q1)
    await state.update_data(battle_id=battle_id)
    await call.message.edit_text('Отправьте фото, которое не несет 18+ и оскорбительного характера')


@dp.message(SendPhotoForBattle.q1)
async def send_photo_for_battle_handler(message: types.Message, state: FSMContext):
    if message.photo:
        photo = message.photo[-1].file_id
        await state.update_data(photo=photo)
        await state.set_state(SendPhotoForBattle.q2)
        kb = InlineKeyboardBuilder()
        kb.button(text='✅ Подтверждаю', callback_data=f'confirmbattlejoin')
        kb.button(text='🔙 Другое фото', callback_data=f'usermenu;battles')
        kb.adjust(1)
        await message.answer('Подтверждаете свой выбор?', reply_markup=kb.as_markup())
    else:
        await message.reply('Пожалуйста, отправьте фото')

@dp.callback_query(lambda c: c.data.startswith('usermenu;battles'))
async def option_channel_handler(callback_query: types.CallbackQuery, state: FSMContext):
    await battle_join_handler(callback_query, state)
    await callback_query.answer()

@dp.callback_query(lambda c: c.data=='confirmbattlejoin', SendPhotoForBattle.q2)
async def confirm_battle_join_handler(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    battle_id = data['battle_id']
    photo_file_id = data['photo']
    tg_id = call.from_user.id
    photo_battle_id = await db.add_battle_photo(tg_id, battle_id, photo_file_id)
    battle_info = await db.check_battle_info(battle_id)
    channel_id = battle_info[1]
    channel_info = await db.check_channel_info_by_id(channel_id)
    admin_chat_id = channel_info[4]
    kbs = InlineKeyboardBuilder()
    kbs.button(text='✅ Принять', callback_data=f'searchbattle;approve;{photo_battle_id}')
    kbs.button(text='❌ Отклонить', callback_data=f'searchbattle;decline;{photo_battle_id}')
    kbs.button(text='🛡️ Заблокировать', callback_data=f'searchbattle;block;{photo_battle_id}')
    kbs.adjust(2,1)
    try:
        await bot.send_photo(chat_id=admin_chat_id, photo=photo_file_id, caption=f'Фото от {call.from_user.first_name} (@{call.from_user.username})\nID <code>{call.from_user.id}</code>', reply_markup=kbs.as_markup())
    except Exception as e:
        await call.answer('<b>❌ При отправке фото произошла ошибка</b>')
    await call.message.edit_text('<b>⏳ Фото  отправлено на проверку </b>')
    await state.clear()

@dp.callback_query(lambda c: c.data.startswith('searchbattle'))
async def search_battle_handler(call: types.CallbackQuery, state: FSMContext):
    action = call.data.split(';')[1]
    photo_battle_id = call.data.split(';')[2]
    kb = InlineKeyboardBuilder()
    battle_photo_info = await db.check_battle_photos_where_id1(photo_battle_id)
    tg_id = battle_photo_info[1]
    user_id = battle_photo_info[1]
    battle_id = battle_photo_info[2]
    battle_info = await db.check_battle_info(battle_id)
    if action == 'approve':
        try:
            
            await bot.send_message(chat_id=user_id, text=f'''<b>✅ ВАШЕ ФОТО ОДОБРЕНО</b>\n\nПоздравляем, теперь вы участвуете в фото-батле. \nОжидайте объявление начала батла в канале \n\nСсылка на вступление в канал - {battle_info[5]}''', disable_web_page_preview=True)
        except Exception as e:
            print(e)
        await db.battle_photos_status_by_id(photo_battle_id, 1)
        photos = await db.get_photos_where_status_1(battle_id)
        if len(photos) % battle_info[13] == 0:
            print('Надо выпускать пост')

        try:
            await db.update_photo_approved_time(photo_battle_id)
        except Exception as e:
            print(e)
        kb.button(text='✅ Принят', callback_data='nonefsafs')
        await call.message.edit_reply_markup(reply_markup=kb.as_markup())

        if battle_info[23] == 1:
            channel_info = await db.check_channel_info_by_id(battle_info[1])
            channel_id = channel_info[2]
            print(channel_id)

            await state.update_data(battle_id=battle_id)
            await state.update_data(channel_id=channel_id)
            await state.update_data(photo=photos[-1][3])
            await state.update_data(photo_id=photos[-1][0])
            await state.update_data(user_id=user_id)
            await call.message.answer('⚙️ Введите текст поста, под которым собираетесь опубликовать этот пост')
            await state.set_state(PublishPhotoByOneBattle.text)
    else:
        await state.update_data(user_id=user_id)
        await state.update_data(photo_battle_id=photo_battle_id)
        await state.update_data(battle_id=battle_id)
        await state.update_data(tg_id=tg_id)
        await call.message.answer("Введите причину:")
        if action == 'decline':
            await state.set_state(ReasonRejectOrBlock.q1)

        elif action == 'block':
            await state.set_state(ReasonRejectOrBlock.q2)

@dp.message(ReasonRejectOrBlock.q1)
async def reject_photo(message: types.Message, state: FSMContext):
    await state.update_data(reason=message.text)
    data = await state.get_data()


    try:
        kb = InlineKeyboardBuilder()
        kb.button(text="☁️ Ответить", callback_data='answer')
        kb.button(text="🔄 Отправить заново", callback_data=f'sendagainphoto;{data["battle_id"]}')
        await bot.send_message(chat_id=data['user_id'], text=f'''☁️ Ваше фото отклонено. Сообщение от администратора: <b>{data["reason"]}</b>''', disable_web_page_preview=True, reply_markup=kb.as_markup())
    except Exception as e:
        print(e)

    kb = InlineKeyboardBuilder()
    kb.button(text='❌ Отклонен', callback_data='nonefsafs')
    await message.delete()
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)

    await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.message_id - 2, reply_markup=kb.as_markup())
    await db.delete_user_from_battle_photos(data['photo_battle_id'])

    await state.clear()

@dp.message(ReasonRejectOrBlock.q2)
async def block_photo(message: types.Message, state: FSMContext):
    await state.update_data(reason=message.text)
    data = await state.get_data()

    kb = InlineKeyboardBuilder()

    try:
        await bot.send_message(chat_id=data['user_id'], text=f'''☁️ Вы заблокированы. Сообщение от администратора: <b>{data["reason"]}</b>''', disable_web_page_preview=True)
    except Exception as e:
        print(e)
    kb.button(text='🛡️ Заблокирован', callback_data='nonefsafs')
    await message.delete()
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)

    await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.message_id - 2, reply_markup=kb.as_markup())
    await db.delete_user_from_battle_photos(data['photo_battle_id'])
    await db.add_new_user_to_battle_blocks(data['battle_id'], data['tg_id'])

    await state.clear()

@dp.callback_query(lambda c: c.data.startswith('sendagainphoto'))
async def send_again_photo(call: types.CallbackQuery, state: FSMContext):
    battle_id = call.data.split(';')[1]
    is_user_blocked = await db.check_battle_block_battle_id_tg_id_exist_return_bool(
        battle_id, call.message.from_user.id)
    if is_user_blocked:
        await call.message.answer('Вы заблокированы в этом батле')
        return

    is_user_exist = await db.check_battle_where_battle_id_and_tg_id_exist_and_status_1_return_bool(
        battle_id, call.message.from_user.id)
    if is_user_exist:
        await call.message.answer('Вы уже участвуете в этом батле')
        return

    await state.set_state(SendPhotoForBattle.q1)
    await state.update_data(battle_id=battle_id)
    await call.message.answer('Отправьте фото, которое не несет 18+ и оскорбительного характера')


@dp.message(waiting_for_because.q1)
async def process_answers(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data['user_id']
    if message.content_type not in [ContentType.TEXT, ContentType.PHOTO]:  # ЕСЛИ НЕ ТЕКСТ И НЕ ФОТО
        await message.answer(
            "Вы также можете отправить фото 📸, но видео и другие форматы, к сожалению, не принимаются.",
            reply_markup=question(),
            parse_mode="HTML")
        # Устанавливаем состояние
        await state.set_state(waiting_for_because.q1)
        return
    elif message.content_type == ContentType.TEXT:  # ЭТО ТЕКСТ
        if not message.text:
            await message.answer(
                "<b>💬 Пожалуйста, задайте свой ответ в виде текста или прикрепите фото.</b>", parse_mode="HTML")
            # Остаёмся в состоянии ожидания
            await state.set_state(waiting_for_because.q1)
            return  # Остановка выполнения
        else:
            answer_text = message.text.strip()
            photo = None
    else:  # ЗНАЧИТ ЭТО ФОТО
        if not message.caption:
            await message.answer(
                "<b>💬 Пожалуйста, отправьте фото с ответом.</b>",
                parse_mode="HTML")
            # Сохраняем состояние ожидания
            await state.set_state(waiting_for_because.q1)
            return  # Остановка выполнения
        else:
            photo = message.photo[-1]
            answer_text = message.caption.strip()

    if len(answer_text) < 5 or len(answer_text) > 100:
        await message.answer("<b>💬 Ответ должен быть от 5 до 100 символов.</b>", parse_mode="HTML")
        await state.set_state(waiting_for_because.q1)
        return
        
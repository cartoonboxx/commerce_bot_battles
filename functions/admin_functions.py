from aiogram import types
import datetime
from data.config import *
from aiogram import types
from aiogram.fsm.context import FSMContext
from data import loader, config
from database import db
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardMarkup
from keyboards.another import back_main_menu_add_channel, back_main_menu_channels, back_main_menu_create_battle, create_battle_kb, create_good
from states.classes_states import *
from constants.constants import *
import json
import asyncio

bot = loader.start_bot(config.Token)

def back_main_menu_add_channel2(channed_id):
    kb = InlineKeyboardBuilder()
    kb.button(text='Удалить', callback_data=f'approvedelete;{channed_id}')
    kb.button(text='🔙 Назад', callback_data=f'backtosettings;{channed_id}')
    kb.adjust(1)
    return kb.as_markup()

def back_main_menu_add_channel3(channed_id):
    kb = InlineKeyboardBuilder()
    kb.button(
        text='✅ Подтверждаю', callback_data=f'2approvedelete;{channed_id}'
    )
    kb.button(
        text='🔙 Назад', callback_data='backtochannels'
    )
    kb.adjust(1)
    return kb.as_markup()

def back_main_menu_channels(channels):
    kb = InlineKeyboardBuilder()
    for chan in channels:
        name = chan[3]
        id = chan[0]
        kb.button(text=name, callback_data=f'optionchannel;{id}')
    else:
        kb.button(text='Добавить канал', callback_data='addchannel')
        kb.button(text='🔙 Назад', callback_data='backmainmenu')
    kb.adjust(1)
    return kb.as_markup()

async def active_battles_kb(battles):

    kb = InlineKeyboardBuilder()
    for battle in battles:
        name = battle[3]
        if name != '-':
            id = battle[0]
            kb.button(
            text=name, callback_data=f'optionactivebattle;{id}')
    kb.button(text='🔙 В меню создания батлов', callback_data='backmainmenu')
    kb.adjust(1)
    return kb.as_markup()

async def active_battle_settings_kb(battle_id, status):
    kb = InlineKeyboardBuilder()
    battle_info = await db.check_battle_info(battle_id)

    if status == 0:
        status = 1

    if status == Status.CREATED.value:
        kb.button(text='✅ Начать раунд', callback_data=f'activebattlesettings;start;{battle_id}')
        if battle_info[2] in config.admins:
            kb.button(text='🏞 Добавить фото', callback_data=f'activebattlesettings;fake;{battle_id}')

    if status == Status.NEXTROUND.value:
        kb.button(text='✅ Запустить следующий раунд', callback_data=f'activebattlesettings;next;{battle_id}')

    if status == Status.CREATED.value or status == Status.NEXTROUND.value:
        if battle_info[7] == "-":
            kb.button(text='❌ Раунд по счёту', callback_data=f'activebattlesettings;descr;{battle_id}')
        else:
            kb.button(text='✅ Раунд по счёту', callback_data=f'activebattlesettings;descr;{battle_id}')

        if battle_info[13] == 0:
            kb.button(text='❌ Участников в посте', callback_data=f'activebattlesettings;participants;{battle_id}')
        else:
            kb.button(text='✅ Участников в посте', callback_data=f'activebattlesettings;participants;{battle_id}')

        if battle_info[11] == 0:
            kb.button(text='❌ Мин. голосов для победы', callback_data=f'activebattlesettings;voices;{battle_id}')
        else:
            kb.button(text='✅ Мин. голосов для победы', callback_data=f'activebattlesettings;voices;{battle_id}')

    if status == Status.ENDROUND.value:
        if battle_info[23] == 2:
            kb.button(text='⛔️ Завершить раунд и подвести итоги', callback_data=f'activebattlesettings;end;{battle_id}')
        else:
            kb.button(text='⛔️ Завершить раунд и подвести итоги', callback_data=f'activebattlesettings;endone;{battle_id}')
        if battle_info[22] == 0:
            if battle_info[21] == 0:
                kb.button(text='✅ Открыть набор фото', callback_data=f'activebattlesettings;photo_send;{battle_id}')
            else:
                kb.button(text='❌ Закрыть набор фото', callback_data=f'activebattlesettings;photo_send;{battle_id}')
            if battle_info[23] == 2:
                kb.button(text="✅ Выставить новые фото", callback_data=f'activebattlesettings;update_photo_before;{battle_id}')
            kb.button(text='📝 Изменить текст выпускаемого поста', callback_data=f'activebattlesettings;change_post_text;{battle_id}')



    if status == Status.Error.value:
        kb.button(text='▶️ Продолжить', callback_data=f'aprovecontinuebattleesettings;{battle_id}')

    kb.button(text='🗑 Удалить батл', callback_data=f'activebattlesettings;delete;{battle_id}')

    if status != Status.ENDROUND.value:
        kb.adjust(1, 1, 2, 1, 1, 1, 1)
    else:
        kb.adjust(1, 1, 1, 1, 1)
    return kb.as_markup()

async def back_battle__active_setting_kb(battle_id):
    battle_info = await db.check_battle_info(battle_id)
    kb = InlineKeyboardBuilder()
    if battle_info[23] == 2:
        kb.button(text='🔙 Назад', callback_data=f'optionactivebattle;{battle_id}')
    else:
        if battle_info[14] != 3:
            kb.button(text='🔙 Назад', callback_data=f'one_battle_message;{battle_id}')
        else:
            kb.button(text='🔙 Назад', callback_data=f'returntobattlemenu;{battle_id}')

    return kb.as_markup()

async def round_buttons_battle(battle_id):
    kb = InlineKeyboardBuilder()
    battle_info = await db.check_battle_info(battle_id)
    kb.button(text=f'{battle_info[22] + 1} РАУНД', callback_data=f'saveRoundParam;{battle_info[22] + 1} РАУНД;{battle_id}')
    kb.button(text='Финал', callback_data=f'saveRoundParam;Финал;{battle_id}')
    kb.button(text='🔙 Назад', callback_data=f'optionactivebattle;{battle_id}')
    kb.adjust(1)
    return kb.as_markup()

async def battle_answer_func_message(message: types.Message, battle_id,state:FSMContext):
    await state.clear()
    battle_info = await db.check_battle_info(battle_id)
    post_start_battle = battle_info[17]
    time_now = datetime.datetime.now().strftime("%H:%M")

    if post_start_battle == 0 or post_start_battle is None:
        post_start_battle = 'Не нужен'
    else:
        post_start_battle = f'Нужен'
    await message.answer(f'''<b>🛠️ Настройки фото-батла</b>                                                
''', reply_markup=await create_battle_kb(battle_id, battle_info[5]), disable_web_page_preview=True)

async def kb_return_2page_battlecreate(battle_id):
    battle_info = await db.check_battle_info(battle_id)

    kb = InlineKeyboardBuilder()
    if battle_info[23] == 2:
        kb.button(text='🔙 Назад', callback_data=f"firstround;returnback;{battle_id}")
    else:
        kb.button(text='🔙 Назад', callback_data=f"one_battle_message;{battle_id}")

    kb.adjust(1)
    return kb.as_markup()

async def firstround_menu_setting(message: types.Message, battle_id):

    battle_info = await db.check_battle_info(battle_id)

    kb = InlineKeyboardBuilder()
    kb.button(text='✅ Создать батл', callback_data=f'firstround;iagree;{battle_id}')

    if battle_info[13] == 0:
        kb.button(text='❌ Участников в посте', callback_data=f'firstround;users_in_post;{battle_id}')
    else:
        kb.button(text='✅ Участников в посте', callback_data=f'firstround;users_in_post;{battle_id}')

    if battle_info[15] == "-":
        kb.button(text='❌ Время завершения раунда', callback_data=f'firstround;end_time_round;{battle_id}')
    else:
        kb.button(text='✅ Время завершения раунда', callback_data=f'firstround;end_time_round;{battle_id}')

    if battle_info[11] == 0:
        kb.button(text='❌ Мин. голосов для победы', callback_data=f'firstround;min_votes_win;{battle_id}')
    else:
        kb.button(text='✅ Мин. голосов для победы', callback_data=f'firstround;min_votes_win;{battle_id}')

    kb.button(text='🔙 Назад', callback_data=f'firstround;returnback;{battle_id}')
    kb.adjust(1)
    await message.answer(f'''<b>🛠 Создание фото-батла (2 ШАГ ИЗ 2):\n\n⚙️ Введение настроек для 1 раунда:</b>\n\nВремя завершения раунда: {battle_info[13]}\nМинимальное кол-во голосов для победы в раунде: {battle_info[15]}\nУчастников в одном посте: {battle_info[11]}''', reply_markup=kb.as_markup())

async def admin_subscribed_to_channel(admin_user_id) -> bool:
    admin_channel = await db.check_admin_channel_from_table()

    admin_link_chat_id = admin_channel[3]
    try:
        chat_info = await bot.get_chat(admin_link_chat_id)
        result = await chat_info.get_member(admin_user_id)
        if result.status == 'left':
            return False
        return True
    except Exception as ex:
        return False

async def battle_settings_func(callback: types.CallbackQuery, battle_id, action, state):
    battle_info = await db.check_battle_info(battle_id)
    message = callback.message
    if action == 'createbattle':

        await db.update_battle_end(battle_id, "00:00")
        await db.update_participants_battle(battle_id, 2)
        await db.update_status_battle(battle_id, 0)
        await db.update_battle_prize(battle_id, 'Приз')
        if battle_info[3] == '-' or battle_info[5] == '-' or battle_info[6] == '-' or battle_info[17] == 0:

            await callback.answer('Заполните все поля', show_alert=True)
            return
        else:

            await message.delete()

            await firstround_menu_setting(message, battle_id)

    if action == 'channel_link':
        await state.set_state(AddLinkToBattle.q1)
        await state.update_data(battle_id=battle_id)
        await message.edit_text('<b>⚙️ Введите ссылку на ваш канал</b>',
                                         reply_markup=await back_main_menu_create_battle(battle_id))
    if action == 'name':
        await state.set_state(AddBattleName.q1)
        await state.update_data(battle_id=battle_id)
        await message.edit_text('<b>⚙️ Введите название для вашего батла</b>', reply_markup=await back_main_menu_create_battle(battle_id))
    if action == 'prize':
        await state.set_state(AddBattlePrize.q1)
        await state.update_data(battle_id=battle_id)
        await message.edit_text('<b>⚙️ Введите текст для каждого выкладываемого поста:</b>', reply_markup=await back_main_menu_create_battle(battle_id))
    if action == 'battlepost':
        await state.set_state(AddBattlePost.q1)
        await state.update_data(battle_id=battle_id)
        data_stringify = json.dumps(await state.get_data())
        kb = InlineKeyboardBuilder()
        kb.button(text="✅ Создать пост", callback_data=f"accessCreatePostVote;{data_stringify}")
        kb.button(text="🚫 Пост не нужен", callback_data=f"declineCreatePostVote;{data_stringify}")
        kb.adjust(1)
        await callback.message.edit_text('''⚙️ Вам нужно создать пост о наборе фото? Или вы создадите сами, но она будет без URL-кнопки\n
    \nℹ️ Пост о наборе с URL-кнопкой собирает больше фото, чем без нее''', reply_markup=kb.as_markup())


async def delete_channel_func(call: types.CallbackQuery, channel_id):
    await call.message.edit_text('Подтверждаете?', reply_markup= back_main_menu_add_channel3(channel_id))

async def delete_channel_func2(call: types.CallbackQuery, channel_id):
    await db.delete_channel_by_id(channel_id)
    tg_id = call.from_user.id
    channels = await db.checkk_all_channels_where_tg_id(tg_id)
    message = call.message
    await message.edit_text('<b>✅ Канал удален </b>', reply_markup= back_main_menu_channels(channels))

def generate_support_link(channel_id):
    base_url = f"https://t.me/{config.bot_name}?start=support_{channel_id}"
    return base_url

async def chennelsetting_func(call: types.CallbackQuery, channel_id, action, state:FSMContext):
    tg_id = call.from_user.id
    if action == 'delete':
        await call.message.edit_text('Вы уверены что хотите удалить канал?', reply_markup=back_main_menu_add_channel2(channel_id))
    if action == 'adminchat':

        if not await db.check_temp_admin_chats_by_user(call.message.chat.id):
            await db.add_new_user_temp_admin_chats(call.message.chat.id)
            await db.update_channel_id_temp_admin_chats(call.message.chat.id, channel_id)

        channel_info = await db.check_channel_info_by_id(channel_id)

        if channel_info[4] != 0:
            kb = InlineKeyboardBuilder()
            kb.button(text='Изменить', url=f'http://t.me/{bot_name}?startgroup&admin=manage_chat+delete_messages+change_info+invite_users+post_messages+edit_messages+pin_messages+manage_topics&claim=owner')
            kb.button(text='🔙 Назад', callback_data=f'channelsetting;correct_chat;{channel_id}')
            kb.adjust(1)

            await call.message.edit_text('Для изменения админ-чата нажмите кнопку ниже', reply_markup=kb.as_markup())
        else:
            kb = InlineKeyboardBuilder()
            kb.button(text='⚒️Установить', url=f'http://t.me/{bot_name}?startgroup&admin=manage_chat+delete_messages+change_info+invite_users+post_messages+edit_messages+pin_messages+manage_topics&claim=owner',
                      )
            kb.button(text='🔙 Назад', callback_data=f'backtosettings;{channel_id}')
            kb.adjust(1)
            await call.message.edit_text('Админ-чат не установлен, для установки нажмите кнопку ниже', reply_markup=kb.as_markup())

    if action == 'correct_chat':
        channel_info = await db.check_channel_info_by_id(channel_id)
        print(channel_info[4])
        chat_info = await bot.get_chat(chat_id=channel_info[4])
        print(chat_info)
        kb = InlineKeyboardBuilder()
        kb.button(text='⚒️ Изменить', callback_data=f'channelsetting;adminchat;{channel_id}')
        kb.button(text='🔙 Назад', callback_data=f'backtosettings;{channel_id}')
        kb.adjust(1)
        await call.message.edit_text(f'Текущий админ-чат <a href="{chat_info.invite_link}">{chat_info.title}</a>', reply_markup=kb.as_markup(), disable_web_page_preview=True)

    if action == 'create_one':
        channel_id = call.data.split(';')[2]

        battle_id = await db.create_new_battle_return_id(channel_id, tg_id)
        battle_info = await db.check_battle_info(battle_id)
        post_start_battle = battle_info[17]
        channel_info = await db.check_channel_info_by_id(channel_id)

        try:
            await bot.get_chat(channel_info[2])
        except Exception as ex:
            await call.message.answer(
                'Бот был удален из администраторов в этом канале, верните его в канал и повторите операцию еще раз')
            return

        channel_tg_id = channel_info[5]
        time_now = datetime.datetime.now().strftime("%H:%M")

        await db.update_type_battle(battle_id, 1)

        await db.update_battle_channel_link_by_battle_id(battle_id, channel_tg_id)
        # await db.update_battle_prize(battle_id, 'null')
        await db.update_end_round_battle(battle_id, 'null')
        await db.update_battle_end(battle_id, '00:00')
        await db.update_participants_battle(battle_id, 2)
        # await db.update_min_golos_battle(battle_id, 1)
        await db.update_round_users_battle(battle_id, 1)


        '''Устанавливается только пост и название'''

        kb = InlineKeyboardBuilder()
        kb.button(text='✅ Продолжить', callback_data=f'create_one_battle_continue;{battle_id}')
        if battle_info[3] == "-":
            kb.button(text='❌ Название', callback_data=f'battlesettings;name;{battle_id}')
        else:
            kb.button(text='✅ Название', callback_data=f'battlesettings;name;{battle_id}')
        if battle_info[11] == 0:
            kb.button(text='❌ Мин. голосов для победы', callback_data=f'firstround;min_votes_win;{battle_id}')
        else:
            kb.button(text='✅ Мин. голосов для победы', callback_data=f'firstround;min_votes_win;{battle_id}')
        if battle_info[6] == "-":
            kb.button(text='❌ Текст для каждого поста', callback_data=f'battlesettings;prize;{battle_id}')
        else:
            kb.button(text='✅ Текст для каждого поста', callback_data=f'battlesettings;prize;{battle_id}')
        if battle_info[17] == 0:
            kb.button(text='❌ Пост о батле', callback_data=f'battlesettings;battlepost;{battle_id}')
        else:
            kb.button(text='✅ Пост о батле', callback_data=f'battlesettings;battlepost;{battle_id}')
        kb.button(text='🔙 Назад', callback_data=f'channelsetting;choise_type;{channel_id}')
        kb.adjust(1)
        await call.message.edit_text(f'⚔️ Настройки фото батла', reply_markup=kb.as_markup(), disable_web_page_preview=True)

    if action == 'create_good':
        battle_id = await db.create_new_battle_return_id(channel_id, tg_id)
        battle_info = await db.check_battle_info(battle_id)
        post_start_battle = battle_info[17]
        channel_info = await db.check_channel_info_by_id(channel_id)

        try:
            await bot.get_chat(channel_info[2])
        except Exception as ex:
            await call.message.answer(
                'Бот был удален из администраторов в этом канале, верните его в канал и повторите операцию еще раз')
            return

        channel_tg_id = channel_info[5]
        time_now = datetime.datetime.now().strftime("%H:%M")

        await db.update_battle_channel_link_by_battle_id(battle_id, channel_tg_id)
        if post_start_battle == 0:
            post_start_battle = 'Не нужен'
        else:
            post_start_battle = f'Нужен'
        await call.message.edit_text(f'''<b>🛠️ Настройки фото-батла</b>                                                
''', reply_markup=await create_battle_kb(battle_id, channel_id), disable_web_page_preview=True)
    if action == 'choise_type':
        channel_info = await db.check_channel_info_by_id(channel_id)
        try:
            await bot.get_chat(channel_info[2])
        except Exception as ex:
            await call.message.answer(
                'Бот был удален из администраторов в этом канале, верните его в канал и повторите операцию еще раз')
            return

        if channel_info[4] == 0:
            await call.answer('Заполните все поля', show_alert=True)
            return
        else:
            kb = InlineKeyboardBuilder()
            kb.button(text='Пост с одной фотографией (Соло-батл)', callback_data=f'channelsetting;create_one;{channel_id}')
            kb.button(text='Пост с несколькими фото (Стандартный)', callback_data=f'channelsetting;create_good;{channel_id}')
            kb.button(text='🔙 Назад', callback_data=f'optionchannel;{channel_id}')
            kb.adjust(1)
            await call.message.edit_text(text='<b>⚙️ Выберите тип батла:</b>', reply_markup=kb.as_markup())

async def battle_one_message(message, battle_id):

    battle_info = await db.check_battle_info(battle_id)
    post_start_battle = battle_info[17]

    channel_id = battle_info[1]
    '''Устанавливается только пост и название'''

    kb = InlineKeyboardBuilder()
    kb.button(text='✅ Продолжить', callback_data=f'create_one_battle_continue;{battle_id}')
    if battle_info[3] == "-":
        kb.button(text='❌ Название', callback_data=f'battlesettings;name;{battle_id}')
    else:
        kb.button(text='✅ Название', callback_data=f'battlesettings;name;{battle_id}')
    if battle_info[11] == 0:
        kb.button(text='❌ Мин. голосов для победы', callback_data=f'firstround;min_votes_win;{battle_id}')
    else:
        kb.button(text='✅ Мин. голосов для победы', callback_data=f'firstround;min_votes_win;{battle_id}')
    if battle_info[6] == "-":
        kb.button(text='❌ Текст для каждого поста', callback_data=f'battlesettings;prize;{battle_id}')
    else:
        kb.button(text='✅ Текст для каждого поста', callback_data=f'battlesettings;prize;{battle_id}')
    if battle_info[17] == 0:
        kb.button(text='❌ Пост о батле', callback_data=f'battlesettings;battlepost;{battle_id}')
    else:
        kb.button(text='✅ Пост о батле', callback_data=f'battlesettings;battlepost;{battle_id}')
    kb.button(text='🔙 Назад', callback_data=f'channelsetting;choise_type;{channel_id}')
    kb.adjust(1)
    await message.answer(f'⚔️ Настройки фото батла', reply_markup=kb.as_markup(), disable_web_page_preview=True)


async def active_battle_func(call: types.CallbackQuery, battle_id):
    battle_info = await db.check_battle_info(battle_id)
    tg_id = call.from_user.id
    count_users_in_battle = await db.check_count_battle_photos_where_battle_id_and_status_1(battle_info[0])
    time_now = datetime.datetime.now().strftime("%H:%M:%S")
    status = battle_info[14]
    photo_send = "Открыт" if battle_info[21] else "Закрыт"
    if battle_info[23] == 2:
        battle_info_text = f'''
<b>⚔️ Батл: {battle_info[3]}</b>

- Раунд: {battle_info[7]}
- Минимум для прохождения: {battle_info[11]}

- Участников в одном посте: {battle_info[13]}
- Текущее количество участников: {count_users_in_battle}

- Набор фото: {photo_send}
'''
    else:
        battle_info_text = '<b>Меню управления:</b>'
    await call.message.edit_text(battle_info_text, disable_web_page_preview=True, reply_markup=await active_battle_settings_kb(battle_id, status))

async def active_battle_answer_func(msg: types.Message, battle_id):
    battle_info = await db.check_battle_info(battle_id)
    count_users_in_battle = await db.check_count_battle_photos_where_battle_id_and_status_1(battle_info[0])
    time_now = datetime.datetime.now().strftime("%H:%M:%S")
    status = battle_info[14]
    photo_send = "Открыт" if battle_info[21] else "Закрыт"
    battle_info_text = f'''
<b>⚔️ Батл: {battle_info[3]}</b>

- Раунд: {battle_info[7]}
- Минимум для прохождения: {battle_info[11]}

- Участников в одном посте: {battle_info[13]}
- Текущее количество участников: {count_users_in_battle}

- Набор фото: {photo_send}
'''
    await msg.answer(battle_info_text, disable_web_page_preview=True, reply_markup=await active_battle_settings_kb(battle_id, status))


async def redact_all_status_posts(battle_id, photo_send):
    battle_info = await db.check_battle_info(battle_id)
    channel_link = battle_info[5]
    channel_info = await db.check_channel_info_by_link(channel_link)
    channel_id = channel_info[2]

    posts = await db.get_all_posts_by_battle(battle_id)
    for index, post in enumerate(posts):
        kb = InlineKeyboardBuilder()
        kb.button(text='✅ Проголосовать', url=f'https://t.me/{bot_name}?start=vote{battle_id}page{index+1}')
        kb.adjust(1)
        if photo_send and battle_info[22] == 0:
            await bot.edit_message_text(text=battle_info[6], chat_id=channel_id, message_id=post[2], disable_web_page_preview=True, reply_markup=kb.as_markup())
        else:
            await bot.edit_message_text(text=battle_info[6], chat_id=channel_id, message_id=post[2], disable_web_page_preview=True, reply_markup=kb.as_markup())




async def active_battle_options_func(call: types.CallbackQuery, battle_id, action, state: FSMContext):

    if action =='start':
        battle_info = await db.check_battle_info(battle_id)
        count_users_in_battle = await db.check_count_battle_photos_where_battle_id_and_status_1(battle_info[0])
        count_photos = len(await db.check_all_battle_photos_where_battle_id(battle_info[0]))
        if count_photos % battle_info[13] != 0:
            await call.answer(text='Нужно еще фото', show_alert=True)
            return

        if int(count_users_in_battle) < int(battle_info[10]):
            await call.answer('Нельзя начать раунд, пока количество участников меньше 1', show_alert=True)
            return
        if battle_info[13] == 0:
            await call.answer('Нельзя начать раунд, пока не установлено количество участников в посте', show_alert=True)
            return
        if battle_info[7] == '-':
            await call.answer('Нельзя начать раунд, пока не указано, какой раунд по счёту', show_alert=True)
            return
        if battle_info[11] == 0:
            await call.answer('Нельзя начать раунд, пока не установлено количество голосов для победы', show_alert=True)
            return
        if battle_info[15] == '-':
            await call.answer('Нельзя начать раунд, пока не установлено время завершения батла', show_alert=True)
            return
        if int(count_users_in_battle) < int(battle_info[13]):
            await call.answer('Нельзя начать раунд, участников в посте больше текущего количества участников', show_alert=True)
            return

        kb = InlineKeyboardBuilder()
        kb.button(text='✅ Подтверждаю', callback_data=f'approveactivebattlesettings;{battle_id}')
        kb.button(text='🔙 Назад', callback_data=f'optionactivebattle;{battle_id}')
        kb.adjust(1)
        await call.message.edit_text('Начать раунд?', reply_markup=kb.as_markup())
    if action == 'descr':
        await call.message.edit_text('<b>⚙️ Введите раунд по счёту, нажав на кнопки ниже</b>.', reply_markup=await round_buttons_battle(battle_id))

    if action == 'participants':
        await call.message.edit_text('<b>⚙️ Введите кол-во участников. в одном посте от 2 до 10.</b> \n\nУказывайте только число.', reply_markup=await back_battle__active_setting_kb(battle_id))
        await state.set_state(AddActiveBattleParticipants.q1)
        await state.update_data(battle_id=battle_id)
    if action == 'time':
        await call.message.edit_text('<b>⚙️ Введите время конца раунда в формате: “сегодня в 12:00"</b>\n\nУказывайте время по московскому времени.', reply_markup=await back_battle__active_setting_kb(battle_id))
        await state.set_state(AddActiveBattleEnd.q1)
        await state.update_data(battle_id=battle_id)
    if action =='voices':
        await call.message.edit_text('<b>⚙️ Введите минимальное количество голосов для победы в раунде.</b>\n\nПобеда учитывается, если человек набрал минималку и обогнал соперников.', reply_markup=await back_battle__active_setting_kb(battle_id))
        await state.set_state(AddVoicesToWin.q1)
        await state.update_data(battle_id=battle_id)

    if action == 'change_post_text':
        await call.message.edit_text('⚙️ Отправьте новый текст, который будет выкладываться с постами', reply_markup=await back_battle__active_setting_kb(battle_id))
        await state.set_state(SetTextToPublish.post_text)
        await state.update_data(battle_id=battle_id)

    if action == 'photo_send':
        await call.answer('✅ Статус набора на фото изменен!')
        battle_info = await db.check_battle_info(battle_id)
        photo_send = battle_info[21]
        photo_send = int(not photo_send)

        await db.update_photo_send_battle(photo_send, battle_id)

        # await redact_all_status_posts(battle_id, photo_send)

        await active_battle_func(call, battle_id)
        await state.update_data(battle_id=battle_id)

    if action == 'update_photo':

        await active_battle_func(call, battle_id)

        from handlers.admin_handler import replace_last_digits, check_battle_info
        battle_info = await db.check_battle_info(battle_id)

        channel_id = battle_info[1]
        channel_info = await db.check_channel_info_by_id(channel_id)
        channel_tg_id = channel_info[2]
        members_in_post = battle_info[13]

        all_battle_users_posted = await db.check_all_battle_photos_where_status_1_and_battle_id(battle_id)
        posts_posted = [all_battle_users_posted[i:i + members_in_post] for i in range(0, len(all_battle_users_posted),
                                                                                      members_in_post)]

        while [] in posts_posted:
            posts_posted.remove([])


        start_page = 0
        if len(posts_posted) != 0:
            start_page = posts_posted[-1][-1][6]

        need_photos = battle_info[13] - len(posts_posted[-1])

        all_battle_users = await db.check_all_battle_photos_where_number_post_0_and_battle_id(battle_id)

        if need_photos != 0:
            media_group = []

            if len(all_battle_users) < need_photos:
                need_photos = len(all_battle_users)

            for index in range(need_photos):
                try:
                    media = types.InputMediaPhoto(media=all_battle_users[index][3])
                    media_group.append(media)
                    await db.update_number_post_in_battle_photos_by_id(all_battle_users[index][0], start_page)
                    all_battle_users.pop(index)
                except Exception as ex:

                    break
            index = start_page

            text = battle_info[6]

            await asyncio.sleep(5)
            await bot.send_media_group(chat_id=channel_tg_id, media=media_group)
            kb = InlineKeyboardBuilder()
            kb.button(text=f'✅ Проголосовать',
                      url=f'https://t.me/{config.bot_name}?start=vote{battle_id}page{index}')
            kb.adjust(1)
            message = await bot.send_message(chat_id=channel_tg_id, text=text, disable_web_page_preview=True, reply_markup=kb.as_markup())
            await db.update_id_post(message.message_id, battle_id)

        posts = [all_battle_users[i:i + members_in_post] for i in range(0, len(all_battle_users), members_in_post)]

        if len(posts) == 0:
            await call.answer('Одобренных фото нет')
            return
        else:
            '''проверка и вывешиваем предупреждение'''
            resultation1 = 0
            for post in posts:
                for user in post:
                    resultation1 += 1

            resultation2 = 0
            for post in posts_posted:
                for user in post:
                    resultation2 += 1

            if (resultation1 + resultation2) % members_in_post == 0 and resultation1 != 0:
             await call.message.answer(f'✅ Идёт публикация новых фото: {resultation1} шт.')

        count = 0

        not_posted_photo = await db.all_photo_by_battle(battle_id)
        while [] in not_posted_photo:
            not_posted_photo.remove([])

        for index, post in enumerate(posts):
            index += start_page
            count += 1
            media_group = []
            for user in post:
                media_photo = types.InputMediaPhoto(media=user[3])
                media_group.append(media_photo)
            kb = InlineKeyboardBuilder()

            if battle_info[20] == '-':
                text = battle_info[6]
            else:
                text = battle_info[20]
            await asyncio.sleep(5)
            try:
                await bot.send_media_group(chat_id=channel_tg_id, media=media_group)

            except Exception:
                await db.update_status_battle(battle_id, Status.Error.value)
                await active_battle_func(call, battle_id)
                await call.message.answer('Произошла ошибка при отправке фото в канал, нажмите продолжить')

                last_user_id = post[-1][0]
                await db.update_error_number(last_user_id - 1, battle_id)
                last_number_post = index + 1
                await db.update_error_post(last_number_post, battle_id)
                return

            await asyncio.sleep(5)
            try:
                kb.button(text=f'✅ Проголосовать',
                          url=f'https://t.me/{config.bot_name}?start=vote{battle_id}page{index + 1}')
                kb.adjust(1)
                message = await bot.send_message(chat_id=channel_tg_id, text=text, disable_web_page_preview=True, reply_markup=kb.as_markup())
                message_id = message.message_id
                await db.update_id_post(message_id, battle_id)


            except Exception:
                await db.update_status_battle(battle_id, Status.Error.value)
                await active_battle_func(call, battle_id)
                await call.message.answer('Произошла ошибка при отправке фото в канал, нажмите продолжить')

                last_user_id = post[-1][0]
                await db.update_error_number(last_user_id - 1, battle_id)
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
                    channel_info = await db.check_channel_info_by_id(battle_info[1])
                    channel_data = await bot.get_chat(channel_info[2])
                    if not channel_data.username:
                        kb.button(text="Ссылка на канал", url=battle_info[5])
                    kb.adjust(1)

                    current_battle = await check_battle_info(battle_id)

                    await bot.send_message(chat_id=user[1], text=f'''✅ <b>ВАШЕ ФОТО ОПУБЛИКОВАНО</b>''', disable_web_page_preview=True, reply_markup=kb.as_markup())

                except Exception as e:
                    print(e)
            await db.update_count_in_posts(battle_id, count)


    if action == 'update_photo_before':
        battle_info = await db.check_battle_info(battle_id)

        channel_id = battle_info[1]
        channel_info = await db.check_channel_info_by_id(channel_id)
        channel_tg_id = channel_info[2]
        members_in_post = battle_info[13]

        all_battle_users_posted = await db.check_all_battle_photos_where_status_1_and_battle_id(battle_id)
        posts_posted = [all_battle_users_posted[i:i + members_in_post] for i in range(0, len(all_battle_users_posted),
                                                                                      members_in_post)]

        for post in posts_posted:
            for index, user in enumerate(post):
                if user[6] == 0:
                    post.pop(index)

        start_page = 0

        while [] in posts_posted:
            posts_posted.remove([])
        if len(posts_posted) != 0:
            start_page = posts_posted[-1][-1][6]

        need_photos = battle_info[13] - len(posts_posted[-1])
        if need_photos != 0:
            start_page -= 1

        all_battle_users = await db.check_all_battle_photos_where_number_post_0_and_battle_id(battle_id)


        posts = [all_battle_users[i:i + members_in_post] for i in range(0, len(all_battle_users), members_in_post)]

        if len(posts) == 0:
            await call.answer('Одобренных фото нет')
            return
        else:
            resultation1 = 0
            for post in posts:
                for user in post:
                    resultation1 += 1

            resultation2 = 0
            for post in posts_posted:
                for user in post:
                    resultation2 += 1

            if (resultation1 + resultation2) % members_in_post == 0 and resultation1 != 0:
                kb = InlineKeyboardBuilder()
                kb.button(text='✅ Опубликовать', callback_data=f'activebattlesettings;update_photo;{battle_id}')
                kb.button(text='🔙 Назад', callback_data=f'activebattlesettings;reload;{battle_id}')
                kb.adjust(1)
                await call.message.edit_text(
                    'Вы точно хотите опубликовать новые фото?',
                    reply_markup=kb.as_markup())
            else:

                await call.answer('Нужно ещё фото')



    if action =='reload':
        await active_battle_func(call, battle_id)
    if action == 'end':
        kb = InlineKeyboardBuilder()
        kb.button(text='Подтверждаю', callback_data=f'endapproveactivebattle;{battle_id}')
        kb.button(text='🔙 Назад', callback_data=f'optionactivebattle;{battle_id}')
        kb.adjust(1)
        await call.message.edit_text('Завершить раунд?', reply_markup=kb.as_markup())

    if action == 'endone':

        await call.answer('Батл успешно завершился', show_alert=True)
        battle_info = await db.check_battle_info(battle_id)

        '''количество вышедших постов делим на количество в одном посте'''
        all_posts_photo = await db.all_photo_by_battle(battle_id)

        count = len(all_posts_photo) // int(battle_info[13])
        if len(all_posts_photo) % 2 != 0:
            count += 1

        min_voices = battle_info[11]

        for i in range(1, count + 1):
            post = await db.check_battle_photos_by_battle_id_and_number_post(battle_id, i)

            if not post:
                continue

            eligible_participants = [user for user in post if user[4] >= min_voices]

            if not eligible_participants:
                for user in post:
                    await db.delete_user_from_battle_photos(user[0])
                continue

            max_votes = max(user[4] for user in eligible_participants)

            winners = [user for user in eligible_participants if user[4] == max_votes]

            for winner in winners:
                await db.update_battle_photos_votes_and_number_post(winner[0], 0, 0)

            for user in post:
                if user not in winners:
                    await db.delete_user_from_battle_photos(user[0])


            kb = InlineKeyboardBuilder()
            kb.button(text='🗑 Удалить батл', callback_data=f'activebattlesettings;delete;{battle_id}')
            kb.adjust(1)
            if winners:
                text_users = ''
                for user in winners:
                    current_user = await db.check_info_users_by_tg_id(user[1])
                    text_users += f'- Участник @{current_user[3]}({current_user[1]})\n'
                await call.message.answer(f'⚔️ Итоги раунда:\n\n{text_users}', reply_markup=kb.as_markup())
            else:
                text_users = ''
                for user in winners:
                    current_user = await db.check_info_users_by_tg_id(user[1])
                    text_users += f'- Участник @{current_user[3]}({current_user[1]})\n'
                await call.message.answer(f'⚔️ Итоги раунда:\n\n{text_users}', reply_markup=kb.as_markup())

        await db.update_battles_descr_round_users_min_golos_end_round_by_id(battle_id)
        await db.delete_all_battle_voices_where_battle_id(battle_id)

    if action == 'next':
        battle_info = await db.check_battle_info(battle_id)
        await db.update_photo_send_battle(0, battle_info[0])
        count_users_in_battle = await db.check_count_battle_photos_where_battle_id_and_status_1(battle_info[0])
        if count_users_in_battle == 0:
            tg_id = call.from_user.id
            await db.update_end_battle_statistic(tg_id)
            await call.message.answer('К сожалению никто не победил')
        if count_users_in_battle == 1:
            tg_id = call.from_user.id
            await db.update_end_battle_statistic(tg_id)
            await call.message.answer('Победитель определен!')
            post_info = await db.check_battle_photos_where_id(battle_id)
            user_info = await db.check_info_users_by_tg_id(post_info[1])
            username = user_info[3]
            first_name = user_info[2]
            if await db.check_battle_winner_exist_return_bool(battle_id, post_info[1]):
                pass
            else:
                await db.add_new_battle_winner(battle_id, post_info[1])
            kb = InlineKeyboardBuilder()
            kb.button(text='🗑 Удалить батл', callback_data=f'activebattlesettings;delete;{battle_id}')
            kb.adjust(1)
            await call.message.answer_photo(post_info[3], caption=f'🎉 Победитель: {first_name}\n@{username}\n{post_info[1]} ', reply_markup=kb.as_markup())
            return
        if battle_info[13] == 0:
            await call.answer('Нельзя начать раунд, пока не установлено количество участников в посте', show_alert=True)
            return
        if battle_info[11] == 0:
            await call.answer('Нельзя начать раунд, пока не установлено количество голосов для победы', show_alert=True)
            return
        if battle_info[15] == '-':
            await call.answer('Нельзя начать раунд, пока не установлено время завершения батла', show_alert=True)
            return
        if int(count_users_in_battle) < int(battle_info[13]):
            await call.answer('Нельзя начать раунд, участников в посте больше текущего количества участников', show_alert=True)
            return
        kb = InlineKeyboardBuilder()
        kb.button(text='✅ Подтверждаю', callback_data=f'approveactivebattlesettings;{battle_id}')
        kb.button(text='🔙 Назад', callback_data=f'optionactivebattle;{battle_id}')
        kb.adjust(1)
        await call.message.edit_text('Начать раунд?', reply_markup=kb.as_markup())
    if action == 'delete':
        kb = InlineKeyboardBuilder()
        await state.set_state(DeleteBattleFromDB.password)
        await state.update_data(battle_id=battle_id)
        kb.button(text='🔙 Назад', callback_data=f'optionactivebattle;{battle_id}')
        kb.adjust(1)
        await call.message.edit_text('⚠️ <b>Вы уверены, что хотите удалить батл?</b>\n\n''Введите <code>1234</code>, чтобы подтвердить удаление. 🗑️', reply_markup=kb.as_markup())
    if action == 'fake':
        await call.message.edit_text('<b>⚙️ Отправьте фото, чтобы добавить фото в батл.</b> \n\n Используйте этот метод загрузки фото только в тестовых случаях, за раз можно отправить несколько фото.', reply_markup=await back_battle__active_setting_kb(battle_id))
        await state.set_state(AddFakePhoto.q1)
        await state.update_data(battle_id=battle_id)
        return

async def check_users_tasks(battle_id, user_id) -> bool:
    battle_info = await db.check_battle_info(battle_id)
    channel_info = await db.check_channel_info_by_id(battle_info[1])
    link_channel = channel_info[5]

    try:
        chat_user = await bot.get_chat_member(chat_id=user_id, user_id=user_id)
        user_info = await db.check_info_users_by_tg_id(user_id)
        print('chat_user', chat_user)
        is_premium = chat_user.user.is_premium
        user_in_battle_info = await db.check_user_photo_by_tg_id(tg_id=user_id, battle_id=battle_id)

        status_voiced = await bot.get_user_chat_boosts(chat_id=channel_info[2], user_id=user_id)
        status_voiced = status_voiced.boosts
        print(is_premium)
        if is_premium:
            if not status_voiced:
                return True
        if await db.check_all_sponsors() and not user_in_battle_info[10]:
            return True
        if battle_info[21]:
            return True
        if user_info[8]:
            return True
    except Exception as ex:
        print('Произошла ошибка в проверке')

    return False
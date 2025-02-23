import types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database import db

def cabinet_back():
    kb = ReplyKeyboardBuilder()
    kb.button(text='🔙 Назад')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)

def statics_back():
    kb = ReplyKeyboardBuilder()
    kb.button(text='🔙 Назад')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)

def question():
    kb = ReplyKeyboardBuilder()
    kb.button(text='🔙 Назад')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)

def create_battle():
    kb = InlineKeyboardBuilder()
    kb.button(text='✅ Создать батл', callback_data="create_battle")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)

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

def back_from_addchannel():
    kb = InlineKeyboardBuilder()
    kb.button(text='🔙 Назад', callback_data='back_from_addchannel')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)

async def create_good(channel_id):
    kb = InlineKeyboardBuilder()
    kb.button(text='✅ Всё правильно, проверил(а)', callback_data=f'channelsetting;choise_type;{channel_id}')
    kb.button(text='🔙 Назад', callback_data=f'backtosettings;{channel_id}')
    kb.adjust(1)
    return kb.as_markup()

async def back_main_menu_add_channel_opt(channel_id):
    channel_info = await db.check_channel_info_by_id(channel_id)
    kb = InlineKeyboardBuilder()
    kb.button(text='✅ Создать фото-батл', callback_data=f'channelsetting;choise_type;{channel_id}')
    if channel_info[4] == 0 and channel_info[8] == '-':
        kb.button(text='Не выбран способ получения фото и вопросов', callback_data=f'change_method_send;{channel_id}')
        # kb.button(text='Установить админ-чат для принятия фото', callback_data=f'channelsetting;adminchat;{channel_id}')
    else:
        kb.button(text='Выбран способ получения фото и вопросов', callback_data=f'choice_method_send_photos;{channel_id}')
        # kb.button(text='Изменить админ-чат', callback_data=f'channelsetting;correct_chat;{channel_id}')
    kb.button(text='Удалить канал', callback_data=f'channelsetting;delete;{channel_id}')
    kb.button(text='🔙 Назад', callback_data='backtochannels')
    kb.adjust(1)
    return kb.as_markup()

async def back_main_menu_add_channel(channel_id):
    kb = InlineKeyboardBuilder()
    kb.button(text='🔙 Назад', callback_data=f'backtosettings;{channel_id}')
    return kb.as_markup()

async def back_main_menu_create_battle(battle_id):
    kb = InlineKeyboardBuilder()
    battle_info = await db.check_battle_info(battle_id)
    if battle_info[23] == 2:
        kb.button(text='🔙 Назад', callback_data=f'backtocreate;{battle_id}')
    else:
        kb.button(text='🔙 Назад', callback_data=f'one_battle_message;{battle_id}')
    return kb.as_markup()

async def create_battle_kb(battle_id, channel_id):
    battle_info = await db.check_battle_info(battle_id)
    kb = InlineKeyboardBuilder()
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
    if battle_info[13] == 0:
        kb.button(text='❌ Участников в посте', callback_data=f'firstround;users_in_post;{battle_id}')
    else:
        kb.button(text='✅ Участников в посте', callback_data=f'firstround;users_in_post;{battle_id}')

    kb.button(text='✅ Создать батл', callback_data=f'firstround;iagree;{battle_id}')
    kb.button(text='🔙 Назад', callback_data=f'channelsetting;choise_type;{channel_id}')
    kb.adjust(1)
    return kb.as_markup()
import types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database import db

#общие кнопки

#кнопка назад из мой кабинет
def cabinet_back():
    kb = ReplyKeyboardBuilder()
    kb.button(text='🔙 Назад')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)

#кнопка назад из статистика бота
def statics_back():
    kb = ReplyKeyboardBuilder()
    kb.button(text='🔙 Назад')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)

#кнопка назад из FAQ
def faq():
    kb = ReplyKeyboardBuilder()
    kb.button(text='🔙 Назад')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)

#кнопка назад из задать вопрос
def question():
    kb = ReplyKeyboardBuilder()
    kb.button(text='🔙 Назад')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)

#кнопки в создать фото-батл
def create_battle():
    kb = InlineKeyboardBuilder()
    kb.button(text='✅ Создать батл', callback_data="create_battle")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)

#кнопки выберите канал для создания батла
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

#кнопка назад из добавления канала
def back_from_addchannel():
    kb = InlineKeyboardBuilder()
    kb.button(text='🔙 Назад', callback_data='back_from_addchannel')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)

#кнопки в подтверждении правильных данных
async def create_good(channel_id):
    kb = InlineKeyboardBuilder()
    kb.button(text='✅ Всё правильно, проверил(а)', callback_data=f'channelsetting;choise_type;{channel_id}')
    kb.button(text='🔙 Назад', callback_data=f'backtosettings;{channel_id}')
    kb.adjust(1)
    return kb.as_markup()
#кнопка в Настройка канала
async def back_main_menu_add_channel_opt(channel_id):
    channel_info = await db.check_channel_info_by_id(channel_id)
    kb = InlineKeyboardBuilder()
    kb.button(text='✅ Создать фото-батл', callback_data=f'channelsetting;create;{channel_id}')
    if channel_info[4] == 0:
        kb.button(text='Установить админ чат для принятия фото', callback_data=f'channelsetting;adminchat;{channel_id}')
    else:
        kb.button(text='Изменить админ-чат', callback_data=f'channelsetting;adminchat;{channel_id}')
    if channel_info[5] == "-":
     kb.button(text='Добавить ссылку на канал', callback_data=f'channelsetting;channellink;{channel_id}')
    else:
        kb.button(text='Изменить ссылку на канал', callback_data=f'channelsetting;channellink;{channel_id}')
    if channel_info[6] == "-":
     kb.button(text='Добавить ссылку на пост', callback_data=f'channelsetting;channelpost;{channel_id}')
    else:
        kb.button(text='Изменить ссылку на пост', callback_data=f'channelsetting;channelpost;{channel_id}')
    kb.button(text='🛠️ Тех. поддержка', callback_data=f'channelsetting;support;{channel_id}')
    kb.button(text='Удалить канал', callback_data=f'channelsetting;delete;{channel_id}')
    kb.button(text='🔙 Назад', callback_data='backtochannels')
    kb.adjust(1)
    return kb.as_markup()

#кнопка назад в настройки канала
async def back_main_menu_add_channel(channel_id):
    kb = InlineKeyboardBuilder()
    kb.button(text='🔙 Назад', callback_data=f'backtosettings;{channel_id}')
    return kb.as_markup()

#кнопка назад в создание фото-батла
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
    if battle_info[5] == '-':
        kb.button(text='❌ Ссылка на канал', callback_data=f'battlesettings;channel_link;{battle_id}')
    else:
        kb.button(text='✅ Ссылка на канал', callback_data=f'battlesettings;channel_link;{battle_id}')
    if battle_info[17] == 0:
     kb.button(text='❌ Пост о батле', callback_data=f'battlesettings;battlepost;{battle_id}')
    else:
       kb.button(text='✅ Пост о батле', callback_data=f'battlesettings;battlepost;{battle_id}')
    if battle_info[6] == "-":
     kb.button(text='❌ Приз', callback_data=f'battlesettings;prize;{battle_id}')
    else:
       kb.button(text='✅ Приз', callback_data=f'battlesettings;prize;{battle_id}')
    if battle_info[9] == "-":
     kb.button(text='❌ Время завершения', callback_data=f'battlesettings;end;{battle_id}')
    else:
       kb.button(text='✅ Время завершения', callback_data=f'battlesettings;end;{battle_id}')
    if battle_info[10] == 0:
     kb.button(text='❌ Минимальное кол-во участников', callback_data=f'battlesettings;participants;{battle_id}')
    else:
       kb.button(text='✅ Минимальное кол-во участников', callback_data=f'battlesettings;participants;{battle_id}')
    kb.button(text='✅ Перейти к следующему шагу', callback_data=f'battlesettings;createbattle;{battle_id}; {channel_id}')
    kb.button(text='🔙 Назад', callback_data='backtochannels')
    kb.adjust(1,1,2,2,1,1,1)
    return kb.as_markup()
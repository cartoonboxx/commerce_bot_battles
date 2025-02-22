import aiogram
from aiogram import types, Router
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data import config, loader


dp = Router()
bot = loader.start_bot(config.Token)

@dp.callback_query(lambda c: c.data.startswith('choice_method_send_photos'))
async def choice_method_send_photos(call: types.CallbackQuery):
    channel_id = call.data.split(';')[1]

    kb = InlineKeyboardBuilder()
    kb.button(text='Изменить метод', callback_data=f'change_method_send;{channel_id}')
    kb.button(text='Изменить админ-чат', callback_data=f'channelsetting;adminchat;{channel_id}')
    kb.adjust(1)
    await call.message.edit_text('Текущий способ получения фото и вопросов: админ-чат/чат с ботом',
                              reply_markup=kb.as_markup())

@dp.callback_query(lambda c: c.data.startswith('change_method_send'))
async def change_method_send(call: types.CallbackQuery):
    channel_id = call.data.split(';')[1]

    kb = InlineKeyboardBuilder()
    kb.button(text='Админ-чат', callback_data=f'channelsetting;adminchat;{channel_id}')
    kb.button(text='Чат с ботом', callback_data=f'set_chat_bot_mailing_photos;{channel_id}')
    kb.adjust(1)
    await call.message.edit_text('Выберите способ получения фото и вопросов: \n\n1.Админ-чат – бот будет отправлять фото и вопросы от пользователей в отдельную группу. \n\n2.Чат с ботом – бот будет присылать фото и вопросы от пользователей прямо в этот чат.',
                                 reply_markup=kb.as_markup())

@dp.callback_query(lambda c: c.data.startswith('set_chat_bot_mailing_photos'))
async def set_chat_bot_mailing_photos(call: types.CallbackQuery):
    channel_id = call.data.split(';')[1]

    kb = InlineKeyboardBuilder()
    kb.button(text='🔙 Назад', callback_data=f'optionchannel;{channel_id}')
    kb.adjust(1)

    '''Установка этого чата'''
    await call.message.edit_text('✅ Метод получения установлен', reply_markup=kb.as_markup())
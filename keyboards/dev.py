from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.keyboard import InlineKeyboardBuilder

def start_menu_for_dev():
    kb = ReplyKeyboardBuilder()
    kb.button(text='🧱 Создать фото-батл')
    kb.button(text='💬 Рассылка')
    kb.button(text='🧑‍💼 Каналы')
    kb.button(text='📱 Мой кабинет')
    kb.button(text='🛠️ Накрутка голосов')
    kb.button(text='📊 Статистика бота')
    kb.button(text='🆘 Тех. поддержка')
    kb.button(text='⚔️ Наборы на фото-батлы')
    kb.button(text='🥇 Спонсорство и админ-канал')
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

def question_chat(user_id, has_photo=False):
    kb = InlineKeyboardBuilder()
    kb.button(text='💬 Ответить', callback_data=f"admin_reply;{user_id};{'photo' if has_photo else 'no_photo'}")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)

def mailing_dev():
    kb = InlineKeyboardBuilder()
    kb.button(text='📢 Создать рассылку', callback_data="create_mailling")
    kb.button(text='❌ Отмена', callback_data="cancel_mailing")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)

def channels_dev(channel_id):
    kb = InlineKeyboardBuilder()
    kb.button(text='✅ Удалить канал', callback_data=f"channels_deleted_45;{channel_id}")
    kb.button(text='❌ Отмена', callback_data=f"cancel_delete_channel;{channel_id}")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)

def true_channels_delete(channel_id):
    kb = InlineKeyboardBuilder()
    kb.button(text='‼️ Подтверждаю', callback_data=f"channel_true;{channel_id}")
    kb.button(text='❌ Отмена', callback_data=f"cancel_delete_channel;{channel_id}")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)

def channel_is_deletes(channel_id):
    kb = InlineKeyboardBuilder()
    kb.button(text='На главную', callback_data=f"back_to_channel;{channel_id}")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)

def answers_support(user_id, has_photo=False):
    kb = InlineKeyboardBuilder()
    kb.button(text='💬 Ответить', callback_data=f"replying;{user_id};{'photo' if has_photo else 'no_photo'}")
    kb.button(text='✅ Вопрос решён', callback_data=f"answers_done;{user_id};{'photo' if has_photo else 'no_photo'}")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)

def nakrutka_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text='✅ Накрутить', callback_data="nakrutka")
    kb.button(text='❌ Отмена', callback_data="cancel_nakrutka")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)
   
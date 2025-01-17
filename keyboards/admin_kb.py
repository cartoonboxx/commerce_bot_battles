from aiogram.utils.keyboard import ReplyKeyboardBuilder

def start_menu_for_admins():
    kb = ReplyKeyboardBuilder()
    kb.button(text='🧱 Создать фото-батл')
    kb.button(text='📱 Мой кабинет')
    kb.button(text='📊 Статистика бота')
    kb.button(text='🆘 Тех. поддержка')
    kb.button(text='⚔️ Наборы на фото-батлы')
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

def kabinet_back_admin():
    kb = ReplyKeyboardBuilder()
    kb.button(text='🔙 Назад')
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

def statiks_back_admin():
    kb = ReplyKeyboardBuilder()
    kb.button(text='🔙 Назад')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


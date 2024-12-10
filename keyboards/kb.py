from aiogram.utils.keyboard import ReplyKeyboardBuilder

#обычных юзеров

def start_menu_for_users():
    kb = ReplyKeyboardBuilder()
    kb.button(text='📱 Мой кабинет')
    kb.button(text='⚔️ Наборы на фото-батлы')
    kb.button(text='🆘 Тех. поддержка')
    kb.button(text='🤝 Сотрудничество')
    kb.button(text='📊 Статистика бота')
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

def gocooperation():
    kb = ReplyKeyboardBuilder()
    kb.button(text='✅ Приступим')
    kb.button(text='🔙 Назад')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)

def yescooperation():
    kb = ReplyKeyboardBuilder()
    kb.button(text='✅ В админ-меню')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)

def support():
    kb = ReplyKeyboardBuilder()
    kb.button(text='📚 FAQ')
    kb.button(text='🙋 Задать вопрос')
    kb.button(text='🔙 Назад')
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

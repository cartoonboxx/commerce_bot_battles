from aiogram import types
import datetime
from data.config import *
from aiogram import types
from aiogram.fsm.context import FSMContext
from data import loader, config
from database import db
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards.another import back_main_menu_add_channel, back_main_menu_channels, back_main_menu_create_battle, create_battle_kb, create_good
from states.classes_states import *
from constants.constants import *
import json, asyncio

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

async def active_battles_kb(battles):
    print(battles)
    kb = InlineKeyboardBuilder()
    for battle in battles:
        name = battle[3]
        id = battle[0]
        kb.button(
        text=name, callback_data=f'optionactivebattle;{id}')
    kb.button(text='🔙 В меню создания батлов', callback_data='backmainmenu')
    kb.adjust(1)
    return kb.as_markup()



async def active_battle_settings_kb(battle_id, status):
    kb = InlineKeyboardBuilder()
    battle_info = await db.check_battle_info(battle_id)
    print('current menu', status)
    if status == 0:
        status = 1
    # Кнопки только для статуса CREATED
    if status == Status.CREATED.value:
        kb.button(text='✅ Начать раунд', callback_data=f'activebattlesettings;start;{battle_id}')
        kb.button(text='🏞 Добавить фото', callback_data=f'activebattlesettings;fake;{battle_id}')

    # Кнопки только для статуса NEXTROUND
    if status == Status.NEXTROUND.value:
        kb.button(text='✅ Запустить следующий раунд', callback_data=f'activebattlesettings;next;{battle_id}')

    # Кнопки для статусов CREATED и NEXTROUND
    if status == Status.CREATED.value or status == Status.NEXTROUND.value:
        if battle_info[7] == "-":
            kb.button(text='❌ Раунд по счёту', callback_data=f'activebattlesettings;descr;{battle_id}')
        else:
            kb.button(text='✅ Раунд по счёту', callback_data=f'activebattlesettings;descr;{battle_id}')

        if battle_info[13] == 0:
            kb.button(text='❌ Участников в посте', callback_data=f'activebattlesettings;participants;{battle_id}')
        else:
            kb.button(text='✅ Участников в посте', callback_data=f'activebattlesettings;participants;{battle_id}')

        if battle_info[15] == "-":
            kb.button(text='❌ Время завершения раунда', callback_data=f'activebattlesettings;time;{battle_id}')
        else:
            kb.button(text='✅ Время завершения раунда', callback_data=f'activebattlesettings;time;{battle_id}')

        if battle_info[11] == 0:
            kb.button(text='❌ Мин. голосов для победы', callback_data=f'activebattlesettings;voices;{battle_id}')
        else:
            kb.button(text='✅ Мин. голосов для победы', callback_data=f'activebattlesettings;voices;{battle_id}')

    # Кнопки для других статусов
    if status == Status.ENDROUND.value:
        kb.button(text='⛔️ Завершить раунд и подвести итоги', callback_data=f'activebattlesettings;end;{battle_id}')
        if battle_info[21] == 0:
            kb.button(text='✅ Открыть набор фото', callback_data=f'activebattlesettings;photo_send;{battle_id}')
        else:
            kb.button(text='❌ Закрыть набор фото', callback_data=f'activebattlesettings;photo_send;{battle_id}')
        kb.button(text='Проверить количество новых фотографий', callback_data=f'activebattlesettings;check_photo;{battle_id}')
        kb.button(text="✅ Выставить новые фото", callback_data=f'activebattlesettings;update_photo_before;{battle_id}')









    if status == Status.Error.value:
        kb.button(text='▶️ Продолжить', callback_data=f'aprovecontinuebattleesettings;{battle_id}')

    # Общие кнопки
    # kb.button(text='🔄', callback_data=f'activebattlesettings;reload;{battle_id}')
    kb.button(text='🗑 Удалить батл', callback_data=f'activebattlesettings;delete;{battle_id}')

    if status != Status.ENDROUND.value:
        kb.adjust(1, 1, 2, 1, 1, 1, 1)
    else:
        kb.adjust(1, 1, 1, 1, 1)
    return kb.as_markup()





async def back_battle__active_setting_kb(battle_id):
    kb = InlineKeyboardBuilder()

    kb.button(text='🔙 Назад', callback_data=f'optionactivebattle;{battle_id}')
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
    print('post_id', post_start_battle)
    if post_start_battle == 0 or post_start_battle is None:
        post_start_battle = 'Не нужен'
    else:
        post_start_battle = f'Нужен'
    await message.answer(f'''<b>🛠️ Создание фото-батла: (1 ШАГ ИЗ 2)</b>

- Название:  {battle_info[3]}
- Ссылка на канал: {battle_info[5]}
- Пост о начале батла: {post_start_battle}
- Приз: {battle_info[6]}
- Время начала: {time_now}
- Время завершения: {battle_info[9]}
- Минимальное кол-во участников: {battle_info[10]}                                                    
''', reply_markup=await create_battle_kb(battle_id, battle_info[5]), disable_web_page_preview=True)

async def kb_return_2page_battlecreate(battle_id):
    kb = InlineKeyboardBuilder()
    kb.button(text='🔙 Назад', callback_data=f"firstround;returnstep2;{battle_id}")
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


async def battle_settings_func(callback: types.CallbackQuery, battle_id, action, state):
    battle_info = await db.check_battle_info(battle_id)
    tg_id = callback.from_user.id
    if action == 'createbattle':

        await db.update_status_battle(battle_id, 0)
        if battle_info[3] == '-'or battle_info[5] == '-' or battle_info[6] == '-' or battle_info[9] == '-' or battle_info[10] == 0 or battle_info[17] == 0:
            print(battle_info[3], battle_info[5], battle_info[6], battle_info[9], battle_info[10], battle_info[17])
            await callback.answer('Заполните все поля', show_alert=True)
            return
        else:

            await callback.message.delete()

            # await callback.message.answer('<b>✅ Батл создан </b> \n\nПерейдите в ⚔️ Наборы на фото-батлы, чтобы продолжить настройку')
            #
            # tg_id = callback.from_user.id
            # await db.update_battle_statistic_plus_1(tg_id)
            # await db.update_admin_count_minus_1(tg_id)
            # channel_id = battle_info[1]
            # channel_info = await db.check_channel_info_by_id(channel_id)
            # channel_tg_id = channel_info[2]
            # kb = InlineKeyboardBuilder()
            # kb.button(text='Участвовать', url=f'https://t.me/{config.bot_name}?start=b{battle_id}')
            # try:
            #     post_id = battle_info[17]
            #     if post_id is not None:
            #         await bot.copy_message(chat_id=channel_tg_id, from_chat_id=callback.message.chat.id,
            #                            message_id=battle_info[17], reply_markup=kb.as_markup()
            #                            )
            # except Exception as e:
            #     print(e)
            #     await callback.message.answer('Ошибка отправки поста о батле')

            await firstround_menu_setting(callback.message, battle_id)

    if action == 'channel_link':
        await state.set_state(AddLinkToBattle.q1)
        await state.update_data(battle_id=battle_id)
        await callback.message.edit_text('<b>⚙️ Введите ссылку на ваш канал</b>',
                                         reply_markup=await back_main_menu_create_battle(battle_id))
    if action == 'name':
        await state.set_state(AddBattleName.q1)
        await state.update_data(battle_id=battle_id)
        await callback.message.edit_text('<b>⚙️ Введите название для вашего батла</b>', reply_markup=await back_main_menu_create_battle(battle_id))
    if action == 'prize':
        await state.set_state(AddBattlePrize.q1)
        await state.update_data(battle_id=battle_id)
        await callback.message.edit_text('<b>⚙️ Введите приз для победителя в фото-батле:</b>', reply_markup=await back_main_menu_create_battle(battle_id))
    if action == 'end':
        await state.set_state(AddBattleEnd.q1)
        await state.update_data(battle_id=battle_id)
        await callback.message.edit_text('<b>⚙️ Введите время конца набора фото в формате: 00:00:</b>', reply_markup=await back_main_menu_create_battle(battle_id))
    if action == 'participants':
        await state.set_state(AddBattleParticipants.q1)
        await state.update_data(battle_id=battle_id)
        await callback.message.edit_text('<b>⚙️ Введите минимальное кол-во участников для начала батла. \n\n Отправьте только число</b>', reply_markup=await back_main_menu_create_battle(battle_id))
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
    await call.message.edit_text('<b>✅ Канал удален </b>', reply_markup= back_main_menu_channels(channels))




def generate_support_link(channel_id):
    base_url = f"https://t.me/{config.bot_name}?start=support_{channel_id}"  # Ссылка для запуска бота
    return base_url

async def chennelsetting_func(call: types.CallbackQuery, channel_id, action, state:FSMContext):
    tg_id = call.from_user.id
    if action == 'delete':
        await call.message.edit_text('Вы уверены что хотите удалить канал?', reply_markup=back_main_menu_add_channel2(channel_id))
    if action == 'support':
        support_link = generate_support_link(channel_id)
        await call.message.edit_text(
            f'<b>🛠️ Ваша ссылка для принятия вопросов от пользователей анонимно:</b> \n\n{support_link}\n\nВопросы будут приходить в админ-чат.',reply_markup=await back_main_menu_add_channel(channel_id))
    if action == 'adminchat':
        await state.set_state(AddChat.q1)
        await state.update_data(channel_id=channel_id)
        channel_info = await db.check_channel_info_by_id(channel_id)
        await call.message.edit_text(f'''<b>⚙️ Добавление чата для администраторов </b>

Текущий ID админ-чата: {channel_info[4]}

ℹ️ В этом чате будут появляться фото для батлов и сообщения от пользователей. Любой участник чата сможет принимать или отклонять фотографии, а также отвечать на сообщения.

<b>⁉️ Как добавить админ-чат: </b>

1. Добавьте бота в нужный чат.
2. Перешлите сообщение от имени чата. 
3. Назначьте бота администратором с правами на публикацию!''',
reply_markup=await back_main_menu_add_channel(channel_id) )
    if action == 'create':
      channel_info = await db.check_channel_info_by_id(channel_id)
      if channel_info[4] == '0'or channel_info[5] == '-' or channel_info[6] == '-':
            await call.answer('Заполните все поля', show_alert=True)
            return
      else:
       await call.message.edit_text(
        f'⚙️ <b>ВНИМАНИЕ</b>\n\n'
        'Перепроверьте все поля, которые вы заполнили ранее. Бот не может проверить их корректность автоматически.\n\n'
        '⚠️ Если данные неверны, это может привести к следующим проблемам:\n'
        '- Фото могут не загружаться;\n'
        '- Пользователи не смогут войти в канал;\n'
        '- И другие неполадки.\n\n'
        'Пожалуйста, убедитесь, что всё заполнено правильно!', reply_markup=await create_good(channel_id))
    if action == 'create_good':
        battle_id = await db.create_new_battle_return_id(channel_id, tg_id)
        battle_info = await db.check_battle_info(battle_id)
        post_start_battle = battle_info[17]
        channel_info = await db.check_channel_info_by_id(channel_id)
        channel_tg_id = channel_info[5]
        time_now = datetime.datetime.now().strftime("%H:%M")

        await db.update_battle_channel_link_by_battle_id(battle_id, channel_tg_id)
        if post_start_battle == 0:
            post_start_battle = 'Не нужен'
        else:
            post_start_battle = f'Нужен'
        await call.message.edit_text(f'''<b>🛠️ Создание фото-батла: (1 ШАГ ИЗ 2)</b>

- Название:  {battle_info[3]}
- Ссылка на канал: {channel_tg_id}
- Пост о начале батла: {post_start_battle}
- Приз: {battle_info[6]}
- Время начала: {time_now}
- Время завершения: {battle_info[9]}
- Минимальное кол-во участников: {battle_info[10]}                                                    
''', reply_markup=await create_battle_kb(battle_id, channel_id), disable_web_page_preview=True)
    if action == 'channelpost':
        await state.update_data(channel_id=channel_id)
        await state.set_state(AddChannelPost.q1)
        channel_info = await db.check_channel_info_by_id(channel_id)
        await call.message.edit_text(
    "<b>⚙️ Добавление ссылки на пост </b>\n\n"
    f'Текущая ссылка на пост: {channel_info[6]}\n\n'
    "ℹ️ Этот параметр необходим для технической работы бота.\n\n"
    "<b>⁉️ Пожалуйста, отправьте ссылку на любой пост из вашего канала.</b>",
    reply_markup=await back_main_menu_add_channel(channel_id), disable_web_page_preview=True)

    if action == 'channellink':
        channel_info = await db.check_channel_info_by_id(channel_id)
        await state.update_data(channel_id=channel_id)
        await state.set_state(AddChannelLink.q1)
        await call.message.edit_text(
    f'<b>⚙️ Добавление ссылки на канал </b>\n\n'
    f'Текущая ссылка на канал: {channel_info[5]}\n\n'
    f'ℹ️ Ссылка на ваш канал будет использоваться для уведомлений участников батла, а также будет отображаться в информации о батле.\n\n'
    f'<b>⁉️ Пожалуйста, отправьте корректную ссылку на канал, чтобы пользователи могли перейти на него.</b>',
    reply_markup=await back_main_menu_add_channel(channel_id))

async def active_battle_func(call: types.CallbackQuery, battle_id):
    battle_info = await db.check_battle_info(battle_id)
    tg_id = call.from_user.id
    count_users_in_battle = await db.check_count_battle_photos_where_battle_id_and_status_1(battle_info[0])
    time_now = datetime.datetime.now().strftime("%H:%M:%S")
    status = battle_info[14]
    photo_send = "Открыт" if battle_info[21] else "Закрыт"
    battle_info_text = f'''
<b>⚔️ Батл: {battle_info[3]}</b>

- Раунд: {battle_info[7]}
- Итоги раунда: {battle_info[15]}
- Минимум для прохождения: {battle_info[11]}

- Участников в одном посте: {battle_info[13]}
- Приз: {battle_info[6]}
- Всего участников в батле
- Текущее количество участников: {count_users_in_battle}

- Набор фото: {photo_send}
'''
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
- Итоги раунда: {battle_info[15]}
- Минимум для прохождения: {battle_info[11]}

- Участников в одном посте: {battle_info[13]}
- Приз: {battle_info[6]}
- Всего участников в батле
- Текущее количество участников: {count_users_in_battle}

- Набор фото: {photo_send}
'''
    await msg.answer(battle_info_text, disable_web_page_preview=True, reply_markup=await active_battle_settings_kb(battle_id, status))


async def redact_all_status_posts(battle_id, photo_send):
    '''photo send необходимо для понимания, закрыт или открыт набор'''
    battle_info = await db.check_battle_info(battle_id)
    channel_link = battle_info[5]
    channel_info = await db.check_channel_info_by_link(channel_link)
    channel_id = channel_info[2]

    posts = await db.get_all_posts_by_battle(battle_id)
    for index, post in enumerate(posts):
        kb = InlineKeyboardBuilder()
        kb.button(text='✅ Проголосовать', url=f'https://t.me/{bot_name}?start=vote{battle_id}page{index+1}')
        kb.adjust(1)
        if photo_send:
            await bot.edit_message_text(text=f'''<b>⚔️ {battle_info[7]}</b>\n<b>💰 ПРИЗ — {battle_info[6]}</b>\n\n<b><a href="https://t.me/{bot_name}?start=b{battle_id}">✅ ИДЕТ НАБОР НА БАТЛ ТУТ</a></b>\n\n<b>📝 Условия:</b> обогнать соперника и набрать минимум {battle_info[11]} голосов\n<b>⏳Итоги:</b> {battle_info[15]} по МСК
        ''', chat_id=channel_id, message_id=post[2], reply_markup=kb.as_markup())
        else:
            await bot.edit_message_text(text=f'''<b>⚔️ {battle_info[7]}</b>\n<b>💰 ПРИЗ — {battle_info[6]}</b>\n\n<b>📝 Условия:</b> обогнать соперника и набрать минимум {battle_info[11]} голосов\n<b>⏳Итоги:</b> {battle_info[15]} по МСК
                    ''', chat_id=channel_id, message_id=post[2], reply_markup=kb.as_markup())




async def active_battle_options_func(call: types.CallbackQuery, battle_id, action, state: FSMContext):

    if action =='start':
        battle_info = await db.check_battle_info(battle_id)
        count_users_in_battle = await db.check_count_battle_photos_where_battle_id_and_status_1(battle_info[0])
        if int(count_users_in_battle) < int(battle_info[10]):
            await call.answer('Нельзя начать раунд, пока количество участников меньше минимального', show_alert=True)
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
    if action == 'photo_send':
        await call.answer('✅ Записи постов были успешно изменены!')
        battle_info = await db.check_battle_info(battle_id)
        photo_send = battle_info[21]
        if photo_send:
            photo_send = 0
        else:
            photo_send = 1

        await db.update_photo_send_battle(photo_send, battle_id)

        await redact_all_status_posts(battle_id, photo_send)

        await active_battle_func(call, battle_id)
        await state.update_data(battle_id=battle_id)

    if action == 'check_photo':
        battle_info = await db.check_battle_info(battle_id)

        channel_id = battle_info[1]
        channel_info = await db.check_channel_info_by_id(channel_id)
        channel_tg_id = channel_info[2]
        members_in_post = battle_info[13]

        all_battle_users = await db.check_all_battle_photos_where_number_post_0_and_battle_id(battle_id)
        posts = [all_battle_users[i:i + members_in_post] for i in range(0, len(all_battle_users), members_in_post)]

        resultation = 0
        for post in posts:
            for user in post:
                resultation += 1

        post_text = ''
        if resultation % members_in_post == 0 and resultation != 0:
            post_text = 'Можете выкладывать новые фотографии'
        else:
            post_text = 'Выкладывать новые фотографии не рекомендуется'

        await call.answer(f'Количество новых фото: {resultation}. {post_text}')

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

        for post in posts_posted:
            for index, user in enumerate(post):
                if user[6] == 0:
                    post.pop(index)

        start_page = 0
        if len(posts_posted) != 0:
            start_page = posts_posted[-2][-1][6]

        need_photos = battle_info[13] - len(posts_posted[-2])
        if need_photos != 0:
            start_page -= 1

        all_battle_users = await db.check_all_battle_photos_where_number_post_0_and_battle_id(battle_id)
        print('all', all_battle_users)


        if need_photos != 0:
            media_group = []
            print(need_photos, 'need_photos')
            if len(all_battle_users) < need_photos:
                need_photos = len(all_battle_users)
                print('попал сюда')
            for index in range(need_photos):
                media = types.InputMediaPhoto(media=all_battle_users[index][3])
                media_group.append(media)
                all_battle_users.pop(index)
                await db.update_number_post_in_battle_photos_by_id(all_battle_users[index][0], start_page)
            index = start_page
            print()
            text = f'''⚔️ <b>{battle_info[7]}</b>
<b>💰 ПРИЗ — {battle_info[6]}</b>

<b><a href="https://t.me/{bot_name}?start=b{battle_id}">✅ ИДЕТ НАБОР НА БАТЛ ТУТ</a></b>

📝 <b>Условия:</b> обогнать соперника и набрать минимум {battle_info[11]} голосов
⏳<b>Итоги:</b> {battle_info[15]} по МСК'''
            # await asyncio.sleep(20)
            await bot.send_media_group(chat_id=channel_tg_id, media=media_group)
            kb = InlineKeyboardBuilder()
            kb.button(text=f'✅ Проголосовать',
                      url=f'https://t.me/{config.bot_name}?start=vote{battle_id}page{index + 1}')
            kb.adjust(1)
            message = await bot.send_message(chat_id=channel_tg_id, text=text, reply_markup=kb.as_markup())

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

            post_text = ''
            if (resultation1 + resultation2) % members_in_post == 0 and resultation1 != 0:
                post_text = 'Можете выкладывать новые фотографии'
            else:
                post_text = 'Выкладывать новые фотографии не рекомендуется'

            await call.answer(f'Количество новых фото: {resultation1}. {post_text}')


        count = 0

        for index, post in enumerate(posts):
            index += start_page + 1
            count += 1
            media_group = []
            for user in post:
                media_photo = types.InputMediaPhoto(media=user[3])
                media_group.append(media_photo)
                # Обновление для каждого пользователя
            kb = InlineKeyboardBuilder()

            if battle_info[20] == '-':
                text = f'''⚔️ <b>{battle_info[7]}</b>
<b>💰 ПРИЗ — {battle_info[6]}</b>

<b><a href="https://t.me/{bot_name}?start=b{battle_id}">✅ ИДЕТ НАБОР НА БАТЛ ТУТ</a></b>

📝 <b>Условия:</b> обогнать соперника и набрать минимум {battle_info[11]} голосов
⏳<b>Итоги:</b> {battle_info[15]} по МСК'''
            else:
                text = battle_info[20]
            await asyncio.sleep(20)
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

            await asyncio.sleep(10)
            try:
                kb.button(text=f'✅ Проголосовать',
                          url=f'https://t.me/{config.bot_name}?start=vote{battle_id}page{index + 1}')
                kb.adjust(1)
                message = await bot.send_message(chat_id=channel_tg_id, text=text, reply_markup=kb.as_markup())
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
                    kb.button(text='Ссылка на голосование', url=new_channel_link)
                    kb.button(text='Ссылка на канал', url=battle_info[5])
                    kb.adjust(1)

                    current_battle = await check_battle_info(battle_id)

                    await bot.send_message(chat_id=user[1], text=f'''✅ <b>ВАШЕ ФОТО ОПУБЛИКОВАНО</b>\n\nПоздравляем, вы участвуете в фото-батле. Набирайте голоса и увидимся в следующем раунде
                    ''', disable_web_page_preview=True, reply_markup=kb.as_markup())

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
        if len(posts_posted) != 0:
            start_page = posts_posted[-2][-1][6]

        need_photos = battle_info[13] - len(posts_posted[-2])
        if need_photos != 0:
            start_page -= 1

        all_battle_users = await db.check_all_battle_photos_where_number_post_0_and_battle_id(battle_id)
        print('all', all_battle_users)

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

            post_text = ''
            if (resultation1 + resultation2) % members_in_post == 0 and resultation1 != 0:
                post_text = 'Можете выкладывать новые фотографии'
            else:
                kb = InlineKeyboardBuilder()
                kb.button(text='✅ Продолжить', callback_data=f'activebattlesettings;update_photo;{battle_id}')
                kb.button(text='🔙 Назад', callback_data=f'activebattlesettings;reload;{battle_id}')
                kb.adjust(1)
                await call.message.edit_text('⚠️ Новые посты с фотографиями могут выйти не так, как должны. Продолжить?', reply_markup=kb.as_markup())



    if action =='reload':
        await active_battle_func(call, battle_id)
    if action == 'end':
        kb = InlineKeyboardBuilder()
        kb.button(text='Подтверждаю', callback_data=f'endapproveactivebattle;{battle_id}')
        kb.button(text='🔙 Назад', callback_data=f'optionactivebattle;{battle_id}')
        kb.adjust(1)
        await call.message.edit_text('Завершить раунд?', reply_markup=kb.as_markup())
    if action == 'next':
        battle_info = await db.check_battle_info(battle_id)
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
        # kb.button(text='✅ Подтверждаю', callback_data=f'secapprovedeletebattle;{battle_id}')
        await state.set_state(DeleteBattleFromDB.password)
        await state.update_data(battle_id=battle_id)
        kb.button(text='🔙 Назад', callback_data=f'optionactivebattle;{battle_id}')
        kb.adjust(1)
        await call.message.edit_text('Вы точно хотите удалить батл? Введите "1234", чтобы удалить', reply_markup=kb.as_markup())
    if action == 'fake':
        await call.message.edit_text('<b>⚙️ Отправьте фото, чтобы добавить фото в батл.</b> \n\n Используйте этот метод загрузки фото только в крайних случаях, за раз можно отправить несколько фото.', reply_markup=await back_battle__active_setting_kb(battle_id))
        await state.set_state(AddFakePhoto.q1)
        await state.update_data(battle_id=battle_id)
        return
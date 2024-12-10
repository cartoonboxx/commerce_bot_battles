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
import json

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
        kb.button(text='▶️ Следующий раунд', callback_data=f'activebattlesettings;next;{battle_id}')

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
        kb.button(text='⭕️ Завершить раунд', callback_data=f'activebattlesettings;end;{battle_id}')
    if status == Status.Error.value:
        kb.button(text='▶️ Продолжить', callback_data=f'aprovecontinuebattleesettings;{battle_id}')

    # Общие кнопки
    kb.button(text='🔄', callback_data=f'activebattlesettings;reload;{battle_id}')
    kb.button(text='🗑 Удалить батл', callback_data=f'activebattlesettings;delete;{battle_id}')

    kb.adjust(1, 2, 1, 1, 1, 1, 1)
    return kb.as_markup()





async def back_battle__active_setting_kb(battle_id):
    kb = InlineKeyboardBuilder()
    
    kb.button(text='🔙 Назад', callback_data=f'optionactivebattle;{battle_id}')
    return kb.as_markup()















    

async def battle_answer_func_message(message: types.Message, battle_id,state:FSMContext):
    await state.clear()
    battle_info = await db.check_battle_info(battle_id)
    post_start_battle = battle_info[17]
    time_now = datetime.datetime.now().strftime("%H:%M")
    if post_start_battle == 0:
            post_start_battle = 'Отсутствует'
    else:
            post_start_battle = f'Создан'
    await message.answer(f'''<b>🛠️ Создание фото-батла:</b>

- Название:  {battle_info[3]}
- Ссылка на канал: {battle_info[5]}
- Пост о начале батла: {post_start_battle}
- Приз: {battle_info[6]}
- Время начала: {time_now}
- Время завершения: {battle_info[9]}
- Минимальное кол-во участников: {battle_info[10]}                                                    
''', reply_markup=await create_battle_kb(battle_id, battle_info[5]), disable_web_page_preview=True)



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
            
            await callback.message.answer('<b>✅ Батл создан </b> \n\nПерейдите в ⚔️ Наборы на фото-батлы, чтобы продолжить настройку')

            tg_id = callback.from_user.id
            await db.update_battle_statistic_plus_1(tg_id)
            await db.update_admin_count_minus_1(tg_id)
            channel_id = battle_info[1]
            channel_info = await db.check_channel_info_by_id(channel_id)
            channel_tg_id = channel_info[2]
            kb = InlineKeyboardBuilder()
            kb.button(text='Участвовать', url=f'https://t.me/{config.bot_name}?start=b{battle_id}')
            try:
                print(battle_info[17])
                await bot.copy_message(chat_id=channel_tg_id, from_chat_id=callback.message.chat.id,
                                       message_id=battle_info[17], reply_markup=kb.as_markup()
                                       )
            except Exception as e:
                print(e)
                await callback.message.answer('Ошибка отправки поста о батле')
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
    battle_info_text = f'''
<b>{battle_info[3]}</b>

Раунд по счёту: {battle_info[7]}
Ссылка на вступление: {battle_info[5]}
Приз: {battle_info[6]}
Время конца набора фото: {battle_info[9]}

Время завершения раунда: {battle_info[15]}
Голосов для победы в раунде: {battle_info[11]}
Участников в одном посте: {battle_info[13]}

Количество участников для старта батла: {battle_info[10]}
Текущее количество участников: {count_users_in_battle}

Время: {time_now}'''
    await call.message.edit_text(battle_info_text, disable_web_page_preview=True, reply_markup=await active_battle_settings_kb(battle_id, status))

async def active_battle_answer_func(msg: types.Message, battle_id):
    battle_info = await db.check_battle_info(battle_id)
    count_users_in_battle = await db.check_count_battle_photos_where_battle_id_and_status_1(battle_info[0])
    time_now = datetime.datetime.now().strftime("%H:%M:%S")
    status = battle_info[14]
    battle_info_text = f'''
<b>{battle_info[3]}</b>

Раунд по счёту: {battle_info[7]}
Ссылка на вступление: {battle_info[5]}
Приз: {battle_info[6]}
Время конца набора фото: {battle_info[9]}

Время завершения раунда: {battle_info[15]}
Голосов для победы в раунде: {battle_info[11]}
Участников в одном посте: {battle_info[13]}

Количество участников для старта батла: {battle_info[10]}
Текущее количество участников: {count_users_in_battle}

Время: {time_now}'''
    await msg.answer(battle_info_text, disable_web_page_preview=True, reply_markup=await active_battle_settings_kb(battle_id, status))




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
        await call.message.edit_text('<b>⚙️ Отправьте текстом раунд по счёту</b>. \n\nПример: "1 РАУНД" или "ПОЛУФИНАЛ" или "ФИНАЛ"\n\nЭтот текст будет использоваться в посте.', reply_markup=await back_battle__active_setting_kb(battle_id))
        await state.set_state(AddActiveBattleDescr.q1)
        await state.update_data(battle_id=battle_id)
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
            await call.message.answer_photo(post_info[3], caption=f'Победитель: {post_info[1]} \n{first_name}\n@{username}')
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
        kb.button(text='✅ Подтверждаю', callback_data=f'secapprovedeletebattle;{battle_id}')
        kb.button(text='🔙 Назад', callback_data=f'optionactivebattle;{battle_id}')   
        kb.adjust(1)
        await call.message.edit_text('Удалить батл?', reply_markup=kb.as_markup())
    if action == 'fake':
        await call.message.edit_text('<b>⚙️ Отправьте фото, чтобы добавить фото в батл.</b> \n\n Используйте этот метод загрузки фото только в крайних случаях, за раз можно отправить несколько фото.', reply_markup=await back_battle__active_setting_kb(battle_id))
        await state.set_state(AddFakePhoto.q1)
        await state.update_data(battle_id=battle_id)
        return
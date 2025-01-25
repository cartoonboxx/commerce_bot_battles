from aiogram import types
import datetime
from data.config import *
from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from data import loader, config
from database import db
from states.classes_states import *
from keyboards import admin_kb
from constants.constants import *
from functions.admin_functions import *
import re
import json
import random


dp = Router()
bot = loader.start_bot(config.Token)

@dp.message(AddChat.q1)
async def add_chat_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    channel_id = data.get('channel_id')

    try:
        chat_id = message.chat_shared.chat_id
        chat_member = await bot.get_chat_member(chat_id, bot.id)
    except Exception as ex:
        await message.answer(
            '''<b>❌ Ошибка!</b>\n\n- Бот должен быть администратором в чате. Пожалуйста, предоставьте боту права администратора и попробуйте снова.\n\n- Сообщение должно быть отправлено от имени чата, а не переслано от участника. Убедитесь, что пересылаете сообщение из чата.\n\n<b>ℹ️ Чтобы избежать ошибок:</b>\n1. Проверьте, что бот имеет права администратора.\n2. Убедитесь, что сообщение отправлено из чата, а не от пользователя.\n\n<b>Если возникнут вопросы, пишите нам в разделе 🛠️ Тех. поддержка! </b>''',
            reply_markup=admin_kb.start_menu_for_admins())
        await state.clear()
        return

    if chat_member.status in ['administrator', 'creator']:
        await message.answer(
            text='''<b>✅ Чат успешно добавлен!</b>\n\nℹ️ Теперь фото для батлов и сообщения от пользователей будут отправляться в этот чат. Любой участник сможет принимать или отклонять фотографии, а также отвечать на сообщения.\n\nСпасибо, что доверяете нашему боту!''', reply_markup=admin_kb.start_menu_for_admins()
        )

        await db.uopdate_admin_chat_by_chat_id(channel_id, chat_id)
        await state.clear()
    else:
        await message.answer(
    '''<b>❌ Ошибка!</b>\n\n- Бот должен быть администратором в чате. Пожалуйста, предоставьте боту права администратора и попробуйте снова.\n\n- Сообщение должно быть отправлено от имени чата, а не переслано от участника. Убедитесь, что пересылаете сообщение из чата.\n\n<b>ℹ️ Чтобы избежать ошибок:</b>\n1. Проверьте, что бот имеет права администратора.\n2. Убедитесь, что сообщение отправлено из чата, а не от пользователя.\n\n<b>Если возникнут вопросы, пишите нам в разделе 🛠️ Тех. поддержка! </b>''', reply_markup=admin_kb.start_menu_for_admins())
        await state.clear()

@dp.message(AddBattleName.q1)
async def add_battle_name(message: types.Message, state: FSMContext):
    battle_name = message.text
    data = await state.get_data()
    battle_id = data['battle_id']
    battle_info = await db.check_battle_info(battle_id)
    await db.update_battle_name_by_battle_id(battle_id, battle_name)
    if battle_info[23] == 2:
        await battle_answer_func_message(message, battle_id, state)
    else:
        await battle_one_message(message, battle_id)
    await state.clear()

    await bot.delete_message(message.chat.id, message.message_id)
    await bot.delete_message(message.chat.id, message.message_id - 1)

@dp.message(AddLinkToBattle.q1)
async def add_link_to_battle(message: types.Message, state: FSMContext):
    battle_link = message.text
    data = await state.get_data()
    battle_id = data['battle_id']
    await db.update_link_by_battle_id(battle_id, battle_link)
    await battle_answer_func_message(message, battle_id, state)
    await state.clear()


@dp.message(AddBattleLinkChannel.q1)
async def add_battle_channel_link(message: types.Message, state: FSMContext):
    battle_link = message.text
    data = await state.get_data()
    battle_id = data['battle_id']
    if battle_link.startswith('https://'):
        await db.update_battle_channel_link_by_battle_id(battle_id, battle_link)
        await battle_answer_func_message(message, battle_id, state)
        await state.clear()
    else:
        await message.answer("Не похоже на ссылку... Попробуйте ещё раз.", reply_markup=await back_main_menu_create_battle(battle_id))
@dp.message(AddBattleLinkPost.q1)
async def add_battle_post_link(message: types.Message, state: FSMContext):
    battle_link = message.text
    data = await state.get_data()
    battle_id = data['battle_id']
    if battle_link.startswith('https://'):
        await db.update_battle_post_link_by_battle_id(battle_id, battle_link)
        await battle_answer_func_message(message, battle_id, state)
        await state.clear()
    else:
        await message.answer("Не похоже на ссылку... Попробуйте ещё раз.", reply_markup=await back_main_menu_create_battle(battle_id))
@dp.message(AddBattlePrize.q1)
async def add_battle_prize(message: types.Message, state: FSMContext):
    prize = message.text
    data = await state.get_data()
    battle_id = data['battle_id']
    battle_info = await db.check_battle_info(battle_id)
    await db.update_battle_prize(battle_id, prize)
    if battle_info[23] == 2:
        await battle_answer_func_message(message, battle_id, state)
    else:
        await battle_one_message(message, battle_id)
    await state.clear()

    await bot.delete_message(message.chat.id, message.message_id)
    await bot.delete_message(message.chat.id, message.message_id - 1)

@dp.message(AddBattleDescr.q1)
async def add_battle_descr(message: types.Message, state: FSMContext):
    descr = message.text
    data = await state.get_data()
    battle_id = data['battle_id']
    await db.update_battle_description(battle_id, descr)
    await battle_answer_func_message(message, battle_id, state)
    await state.clear()
    
@dp.message(AddActiveBattleDescr.q1)
async def add_active_battle_descr(message: types.Message, state: FSMContext):
    descr = message.text
    data = await state.get_data()
    battle_id = data['battle_id']
    await db.update_battle_description(battle_id, descr)
    await active_battle_answer_func(message, battle_id)
    await state.clear()
  
@dp.message(AddBattleStart.q1)
async def add_battle_start_time(message: types.Message, state: FSMContext):
    time_text = message.text
    time_pattern = r"^(?:[01]\d|2[0-3]):[0-5]\d$"

    if not re.match(time_pattern, time_text):
        await message.answer("Неверный формат времени. Пожалуйста, введите время в формате ЧЧ:ММ, например, 14:30.")
        return

    try:
        valid_time = datetime.datetime.strptime(time_text, '%H:%M').time()
    except ValueError:
        await message.answer("Неверный формат времени. Пожалуйста, введите время в формате ЧЧ:ММ, например, 14:30.")
        return

    data = await state.get_data()
    battle_id = data['battle_id']
    await db.update_battle_start(battle_id, time_text)
    await battle_answer_func_message(message, battle_id, state)
    await state.clear()

@dp.message(AddActiveBattleEnd.q1)
async def add_active_battle_end_time(message: types.Message, state: FSMContext):
    time = message.text
    data = await state.get_data()
    battle_id = data['battle_id']
    round = data.get('round')
    await db.update_end_round_battle(battle_id, time)
    if round is None:
        await active_battle_answer_func(message, battle_id)
    else:
        await firstround_menu_setting(message, battle_id)
    await state.clear()

    await bot.delete_message(message.chat.id, message.message_id)
    await bot.delete_message(message.chat.id, message.message_id - 1)

@dp.message(AddActiveBattleParticipants.q1)
async def add_active_battle_participants(message: types.Message, state: FSMContext):
    participants = message.text
    data = await state.get_data()
    battle_id = data['battle_id']
    round = data.get('round')
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    if participants.isdigit():
        if int(participants) < 2 or int(participants) > 10:
            await message.answer("Минимальное кол-во участников должно быть от 2х до 10", reply_markup=await back_battle__active_setting_kb(battle_id))
            return
        
        await db.update_round_users_battle(battle_id, participants)
        if round is None:
            await active_battle_answer_func(message, battle_id)
        else:
            await firstround_menu_setting(message, battle_id)
        await state.clear()
    else:
        await message.answer("Не похоже на число... Попробуйте ещё раз.", reply_markup=await back_battle__active_setting_kb(battle_id))

@dp.message(AddVoicesToWin.q1)
async def add_voices_to_win(message: types.Message, state: FSMContext):
    voices = message.text
    data = await state.get_data()
    battle_id = data['battle_id']
    battle_info = await db.check_battle_info(battle_id)
    round = data.get('round')
    if voices.isdigit():
        if int(voices) < 1:
            await message.answer("Минимальное кол-во голосов должно быть больше 1", reply_markup=await back_battle__active_setting_kb(battle_id))
            return
        await db.update_min_golos_battle(battle_id, voices)
        if round is None:
            await active_battle_answer_func(message, battle_id)
        else:
            if battle_info[23] == 2:
                await firstround_menu_setting(message, battle_id)
            else:
                await battle_one_message(message, battle_id)
        await state.clear()
    else:
        await message.answer("Не похоже на число... Попробуйте ещё раз.", reply_markup=await back_battle__active_setting_kb(battle_id))
    await bot.delete_message(message.chat.id, message.message_id)
    await bot.delete_message(message.chat.id, message.message_id - 1)

@dp.message(SetTextToPublish.post_text)
async def SetTextToPublish_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    battle_id = data.get('battle_id')
    battle_info = await db.check_battle_info(battle_id)
    textSave = message.html_text or message.text
    await db.update_battle_prize(battle_id, textSave)
    await bot.delete_message(message.chat.id, message_id=message.message_id - 1)
    await bot.delete_message(message.chat.id, message_id=message.message_id)
    await state.clear()
    battle_info_text = '<b>Меню управления</b>'
    await message.answer(battle_info_text, disable_web_page_preview=True,
                                 reply_markup=await active_battle_settings_kb(battle_id, 3))

@dp.message(AddBattlePost.q1)
async def add_battle_post(message: types.Message, state: FSMContext):
    data = await state.get_data()
    battle_id = data.get('battle_id')
    await state.update_data(message="empty")
    battle_info = await db.check_battle_info(battle_id)
    post_id = message.message_id
    await bot.delete_message(message.chat.id, message.message_id - 1)
    await db.update_post_id(post_id, battle_id)
    if battle_info[23] == 2:
        await battle_answer_func_message(message, battle_id, state)
    else:
        await battle_one_message(message, battle_id)
        await state.clear()

@dp.message(DeleteBattleFromDB.password)
async def deleteBattleFromDB(message: types.Message, state: FSMContext):
    await message.delete()
    if message.text != '1234':
        await message.answer('Введено некорректное значение, попробуйте еще раз')
        await state.set_state(DeleteBattleFromDB.password)
        return

    data = await state.get_data()
    battle_id = data.get('battle_id')
    await state.clear()
    await db.delete_battle_by_id(battle_id)
    await bot.edit_message_text(text='Батл был успешно удален!', chat_id=message.chat.id, message_id=message.message_id - 1)

@dp.callback_query(lambda c: c.data.startswith('admitPostData'))
async def admitPostData(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    battle_id = data.get('battle_id')
    message = data.get('message')
    post_id = message.message_id
    await call.message.delete()
    await db.update_post_id(post_id, battle_id)
    await battle_answer_func_message(message, battle_id, state)

@dp.callback_query(lambda c: c.data.startswith('accessCreatePostVote'))
async def accessCreatePostVote(call: types.CallbackQuery, state: FSMContext):
    data = json.loads(call.data.split(';')[1])
    battle_id = data.get('battle_id')
    await state.update_data(battle_id=battle_id)
    await call.message.edit_text('<b>⚙️ Пришлите текст о наборе фото на батл.</b>\n\n⚠️Тг премиум эмодзи не поддерживаются', reply_markup=await back_main_menu_create_battle(battle_id))
    await state.set_state(AddBattlePost.q1)

@dp.callback_query(lambda c: c.data.startswith('declineCreatePostVote'))
async def declineCreatePostVote(call: types.CallbackQuery, state: FSMContext):
    data = json.loads(call.data.split(';')[1])
    post_id = data.get('post_id')
    battle_id = data.get('battle_id')
    battle_info = await db.check_battle_info(battle_id)
    await call.message.edit_text(f'Ваша ссылка для принятия участников на батл: https://t.me/{bot_name}?start=b{battle_id}\n\n'
                            f'ℹ️<b>Разместите эту ссылку в посте для приема фото, иначе бот не будет работать без фото</b>')
    await db.update_post_id(post_id, battle_id)
    if battle_info[23] == 2:
        await battle_answer_func_message(call.message, battle_id, state)
    else:
        await state.clear()
        await battle_one_message(call.message, battle_id)

@dp.message(AddFakePhoto.q1)
async def add_fake_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    battle_id = data['battle_id']
    if message.photo:
        photo = message.photo[-1].file_id
        random_tg_id = random.randint(1000000000, 9999999999)
        photo_battle_id = await db.add_battle_photo(random_tg_id, battle_id, photo)
        await db.battle_photos_status_by_id(photo_battle_id, 1)
        await message.answer('фото добавлено')
        await active_battle_answer_func(message, battle_id)
    else:
        await message.reply('Пожалуйста, отправьте фото', reply_markup=await back_battle__active_setting_kb(battle_id))
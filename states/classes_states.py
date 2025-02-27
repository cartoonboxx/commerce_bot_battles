from aiogram.fsm.state import State, StatesGroup

class stats_bot(StatesGroup):  #раздел стастика бота
    admin1 = State()
    admin2 = State()
    dev1 = State()
    dev2 = State()
    user1 = State()
    user2 = State()

class support(StatesGroup):  # тех поддержка
    admin = State()
    dev = State()
    user = State()
        
class support_back(StatesGroup):  #назад из тех поддержки
    admin = State()
    dev = State()
    user = State()
    
class rassilka(StatesGroup):
    admin_action = State()
    mailing_message = State()
    mailing_buttons = State()
    
    
class WriteQuestion(StatesGroup):
    q1 = State()
    
class AddChannel(StatesGroup):
    q1 = State()
    q2 = State()

class AddAdminChatAdmins(StatesGroup):
    q1 = State()
    q2 = State()

class AddChat(StatesGroup):
    q1 = State()

class AddLinkToBattle(StatesGroup):
    q1 = State()

class AddBattleName(StatesGroup):
    q1 = State()
class AddBattleLinkChannel(StatesGroup):
    q1 = State()
class AddBattleLinkPost(StatesGroup):
    q1 = State()
class AddBattlePrize(StatesGroup):
    q1 = State()
class AddBattleDescr(StatesGroup):
    q1 = State()
class AddActiveBattleDescr(StatesGroup):
    q1 = State()
class AddActiveBattleParticipants(StatesGroup):
    q1 = State()

class AddBattleStart(StatesGroup):
    q1 = State()
class AddBattleEnd(StatesGroup):
    q1 = State()
class AddActiveBattleEnd(StatesGroup):
    q1 = State()
class AddVoicesToWin(StatesGroup):
    q1 = State()

class AddBattleParticipants(StatesGroup):
    q1 = State()

class AddBattlePost(StatesGroup):
    q1 = State()

class SendPhotoForBattle(StatesGroup):
    q1 = State()
    q2 = State()

class BattleQuestion(StatesGroup):
    q1 = State()
    q2 = State()

class AddFakePhoto(StatesGroup):
    q1 = State()

class AddTextPost(StatesGroup):
    q1 = State()

class Battleanswer(StatesGroup):
    q1 = State()
    q2 = State()

class waiting_for_answers(StatesGroup):
    q1 = State()
    q2 = State()
    q3 = State()

class ReasonRejectOrBlock(StatesGroup):
    q1 = State() # reject
    q2 = State() # block

class waiting_for_because(StatesGroup):
    q1 = State()
    q2 = State()

class FormFirstBattle(StatesGroup):
    countUsersInBattle = State()
    timeEndRouns = State()
    minVotes = State()

class DeleteBattleFromDB(StatesGroup):
    password = State()

class PublishPhotoByOneBattle(StatesGroup):
    text = State()

class SetTextToPublish(StatesGroup):
    post_text = State()

class AddVoices(StatesGroup):
    q1 = State()
    q2 = State()

class Mailing(StatesGroup):
    q1 = State()
    q2 = State()

class MailingPost(StatesGroup):
    q1 = State()

class VotesOperation(StatesGroup):
    tg_id = State()
    count = State()
    access = State()

class PaymentCountState(StatesGroup):
    count = State()

class CreatingPrizeApp(StatesGroup):
    channel_id = State()

class AddChannelPrizes(StatesGroup):
    channel_id = State()
    channel_link = State()